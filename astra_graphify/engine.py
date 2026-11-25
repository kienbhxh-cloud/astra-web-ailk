"""Transactional knowledge-graph store.

Fixes carried over from the KTST-004/005 review:

* Update atomicity: every change is staged on a copy of the state, fully
  validated (both schemas + layer rules + edge endpoint integrity) and only
  then committed with an atomic file replace. A failure leaves the live state
  and the file untouched (Gemini v1.1 mutated state before its cross-project
  check could return).
* Safe prune: pruning requires ``listing_complete=True`` from the lister and
  refuses to delete more than ``max_prune_ratio`` of a project's sources in
  one run unless explicitly allowed.
* Edge integrity: both endpoints must exist as nodes of the SAME project.
* Rollback: each commit keeps a snapshot; ``rollback()`` restores the previous
  one atomically. Every operation is appended to ``journal.jsonl``.
"""
from __future__ import annotations

import copy
import json
import math
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from . import VERSION
from .security import AuthError, CallerAuthRegistry, Principal
from .validator import PROVENANCE_SCHEMA, RECORD_SCHEMA, validate_envelope

GRAPH_FILE = "graph.json"
KEEP_SNAPSHOTS = 10


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _empty_state() -> Dict[str, Any]:
    return {"format": "astra-graphify-store/1", "engine_version": VERSION,
            "nodes": {}, "edges": {}, "source_index": {}, "builds": []}


class SourceBatch:
    """All envelopes produced from one source file (or one Drive file)."""

    def __init__(self, source_key: str, sha256: Optional[str], envelopes: List[Dict[str, Any]]):
        self.source_key = source_key
        self.sha256 = sha256
        self.envelopes = envelopes


class KnowledgeStore:
    def __init__(self, data_dir: Path, record_schema: Path = RECORD_SCHEMA,
                 provenance_schema: Path = PROVENANCE_SCHEMA):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "snapshots").mkdir(exist_ok=True)
        self.graph_file = self.data_dir / GRAPH_FILE
        self.record_schema = record_schema
        self.provenance_schema = provenance_schema
        self.state = self._load()

    # ------------------------------------------------------------------ io
    def _load(self) -> Dict[str, Any]:
        if self.graph_file.exists():
            return json.loads(self.graph_file.read_text(encoding="utf-8"))
        return _empty_state()

    def _write_atomic(self, path: Path, data: Dict[str, Any]) -> None:
        tmp = path.with_name(path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)

    def _journal(self, entry: Dict[str, Any]) -> None:
        with (self.data_dir / "journal.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(dict(entry, at=_now()), ensure_ascii=False) + "\n")

    def _snapshots(self) -> List[Path]:
        return sorted((self.data_dir / "snapshots").glob("graph-*.json"))

    def _commit(self, candidate: Dict[str, Any], summary: Dict[str, Any]) -> None:
        if self.graph_file.exists():
            seq = len(self._snapshots())
            snap = self.data_dir / "snapshots" / f"graph-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%f}-{seq:04d}.json"
            self._write_atomic(snap, self.state)
            for old in self._snapshots()[:-KEEP_SNAPSHOTS]:
                old.unlink()
        self._write_atomic(self.graph_file, candidate)
        self.state = candidate
        self._journal(summary)

    def rollback(self) -> Dict[str, Any]:
        snaps = self._snapshots()
        if not snaps:
            return {"ok": False, "status": "NO_SNAPSHOT"}
        last = snaps[-1]
        restored = json.loads(last.read_text(encoding="utf-8"))
        self._write_atomic(self.graph_file, restored)
        last.unlink()
        self.state = restored
        self._journal({"op": "rollback", "restored_from": last.name})
        return {"ok": True, "status": "ROLLED_BACK", "restored_from": last.name}

    # -------------------------------------------------------------- writes
    @staticmethod
    def _drop_source(state: Dict[str, Any], src_key: str) -> None:
        meta = state["source_index"].pop(src_key, None)
        if not meta:
            return
        for nid in meta.get("node_ids", []):
            state["nodes"].pop(nid, None)
        for eid in meta.get("edge_ids", []):
            state["edges"].pop(eid, None)

    def _edge_integrity(self, state: Dict[str, Any], project_id: str) -> List[str]:
        errs = []
        nodes = state["nodes"]
        for eid, env in state["edges"].items():
            rec = env["record"]
            if rec["project_id"] != project_id:
                continue
            for end in ("source", "target"):
                node = nodes.get(rec[end])
                if node is None:
                    errs.append(f"EDGE_ENDPOINT_MISSING:{eid}:{end}={rec[end]}")
                elif node["record"]["project_id"] != project_id:
                    errs.append(f"CROSS_PROJECT_EDGE_DENIED:{eid}:{end}")
        return errs

    def apply_build(
        self,
        project_id: str,
        batches: Iterable[SourceBatch],
        *,
        active_sources: Optional[Set[str]] = None,
        listing_complete: bool = False,
        max_prune_ratio: float = 0.5,
        allow_mass_prune: bool = False,
        source_revision: str = "",
    ) -> Dict[str, Any]:
        """Stage -> validate everything -> commit atomically, or change nothing."""
        candidate = copy.deepcopy(self.state)
        prefix = f"{project_id}|"
        errors: List[str] = []
        stats = Counter()
        owners = {i: k for k, meta in candidate["source_index"].items()
                  for i in meta.get("node_ids", []) + meta.get("edge_ids", [])}

        for batch in batches:
            if not batch.source_key.startswith(prefix):
                errors.append(f"SOURCE_KEY_PROJECT_MISMATCH:{batch.source_key}")
                continue
            old = candidate["source_index"].get(batch.source_key)
            if old and batch.sha256 and old.get("sha256") == batch.sha256:
                stats["sources_unchanged"] += 1
                continue
            node_ids, edge_ids = [], []
            batch_errors = []
            for env in batch.envelopes:
                ok, errs = validate_envelope(env, self.record_schema, self.provenance_schema)
                rec = env.get("record", {}) if isinstance(env, dict) else {}
                if ok and rec["project_id"] != project_id:
                    ok, errs = False, ["ENVELOPE_PROJECT_MISMATCH"]
                if not ok:
                    batch_errors += [f"{rec.get('id', '?')}:{e}" for e in errs]
                    continue
                (node_ids if rec["kind"] == "node" else edge_ids).append(rec["id"])
            if batch_errors:
                errors += batch_errors
                continue
            self._drop_source(candidate, batch.source_key)
            owners = {i: k for i, k in owners.items() if k != batch.source_key}
            for env in batch.envelopes:
                rec = env["record"]
                bucket = candidate["nodes"] if rec["kind"] == "node" else candidate["edges"]
                owner = owners.get(rec["id"])
                if owner and owner != batch.source_key:
                    errors.append(f"DUPLICATE_ID_ACROSS_SOURCES:{rec['id']}:{owner}")
                owners[rec["id"]] = batch.source_key
                bucket[rec["id"]] = env
            candidate["source_index"][batch.source_key] = {
                "sha256": batch.sha256, "node_ids": node_ids, "edge_ids": edge_ids}
            stats["sources_updated"] += 1
            stats["nodes_written"] += len(node_ids)
            stats["edges_written"] += len(edge_ids)

        prune_status = "PRUNE_SKIPPED_NO_LISTING"
        if active_sources is not None:
            if not listing_complete:
                prune_status = "PRUNE_ABORTED_INCOMPLETE_LISTING"
            else:
                project_keys = [k for k in candidate["source_index"] if k.startswith(prefix)]
                stale = [k for k in project_keys if k not in active_sources]
                ratio = len(stale) / len(project_keys) if project_keys else 0.0
                if stale and ratio > max_prune_ratio and not allow_mass_prune:
                    prune_status = "PRUNE_ABORTED_RATIO_GUARD"
                    errors.append(f"PRUNE_ABORTED_RATIO_GUARD:{len(stale)}/{len(project_keys)}")
                else:
                    for k in stale:
                        self._drop_source(candidate, k)
                    stats["sources_pruned"] = len(stale)
                    prune_status = "PRUNED"

        errors += self._edge_integrity(candidate, project_id)
        result = {"project_id": project_id, "prune_status": prune_status, **stats}
        if errors:
            self._journal({"op": "build_rejected", "project_id": project_id, "errors": errors[:50]})
            return {"ok": False, "status": "REJECTED_NO_CHANGE", "errors": errors, **result}
        if not stats["sources_updated"] and not stats.get("sources_pruned"):
            return {"ok": True, "status": "NO_CHANGE", **result}
        candidate["engine_version"] = VERSION
        candidate["builds"] = (candidate.get("builds", []) + [{
            "at": _now(), "project_id": project_id, "source_revision": source_revision, **stats}])[-50:]
        self._commit(candidate, {"op": "build", **result, "source_revision": source_revision})
        return {"ok": True, "status": "COMMITTED", **result}

    # --------------------------------------------------------------- reads
    def stats(self, project_id: str) -> Dict[str, Any]:
        layers = Counter(e["record"]["knowledge_layer"] for e in self.state["nodes"].values()
                         if e["record"]["project_id"] == project_id)
        n = sum(layers.values())
        m = sum(1 for e in self.state["edges"].values() if e["record"]["project_id"] == project_id)
        builds = [b for b in self.state.get("builds", []) if b["project_id"] == project_id]
        return {"project_id": project_id, "nodes": n, "edges": m, "layers": dict(layers),
                "last_build": builds[-1] if builds else None, "engine_version": self.state.get("engine_version")}

    def search(self, project_id: str, query: str, top_k: int = 8, max_chars: int = 4000) -> Dict[str, Any]:
        terms = set(re.findall(r"\w+", (query or "").lower()))
        scored = []
        for env in self.state["nodes"].values():
            rec = env["record"]
            if rec["project_id"] != project_id or rec["knowledge_layer"] == "REJECTED":
                continue
            hay = Counter(re.findall(r"\w+", f"{rec.get('label', '')} {rec.get('source_file', '')} {rec.get('snippet', '')}".lower()))
            score = sum(1.0 + math.log1p(hay[t]) for t in terms if hay[t])
            if score:
                scored.append((score, rec["id"], env))
        scored.sort(key=lambda x: (-x[0], x[1]))
        results, used = [], 0
        for score, _, env in scored[:top_k]:
            item = {"score": round(score, 3), "record": env["record"], "provenance": env["provenance"]}
            size = len(json.dumps(item, ensure_ascii=False))
            if used + size > max_chars:
                break
            used += size
            results.append(item)
        return {"ok": True, "project_id": project_id, "query": query, "total_hits": len(scored),
                "returned": len(results), "context_chars": used, "token_count": None,
                "token_note": "NOT_MEASURED: context_chars counts characters, not model tokens",
                "results": results}

    def node(self, project_id: str, node_id: str, max_edges: int = 50) -> Dict[str, Any]:
        env = self.state["nodes"].get(node_id)
        if not env or env["record"]["project_id"] != project_id:
            return {"ok": False, "status": "NODE_NOT_FOUND"}
        edges = [e for e in self.state["edges"].values()
                 if e["record"]["project_id"] == project_id and node_id in (e["record"]["source"], e["record"]["target"])]
        edges.sort(key=lambda e: e["record"]["id"])
        return {"ok": True, "node": env, "edges": edges[:max_edges], "edge_total": len(edges)}


class AuthorizedReader:
    """Only read interface exposed to API/MCP: identity first, then project."""

    def __init__(self, store: KnowledgeStore, registry: CallerAuthRegistry):
        self.store = store
        self.registry = registry

    def _project(self, principal: Principal, project_id: Optional[str]) -> str:
        return self.registry.authorize(principal, project_id)

    def call(self, principal: Principal, op: str, args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            pid = self._project(principal, args.get("project_id"))
        except AuthError as exc:
            return {"ok": False, "status": exc.code}
        if op == "search":
            top_k = max(1, min(int(args.get("top_k", 8)), 50))
            return self.store.search(pid, str(args.get("query", "")), top_k=top_k)
        if op == "node":
            return self.store.node(pid, str(args.get("node_id", "")))
        if op == "stats":
            return {"ok": True, **self.store.stats(pid)}
        return {"ok": False, "status": "UNKNOWN_OPERATION"}
