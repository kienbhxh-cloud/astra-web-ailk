"""Convert a Graphify graph.json (AST-only build) into an ASTRA graph snapshot
with one provenance v1.2 record per node and per edge, then check integrity."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import VERSION, GRAPHIFY_PIN
from .provenance import graph_errors, provenance_errors
from .security import path_allowed, scan_sensitive_content, sha256_file

CONFIDENCE_MAP = {"EXTRACTED": "EXTRACTED", "INFERRED": "INFERRED", "AMBIGUOUS": "INFERRED"}


class IntegrityError(ValueError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _nid(project_id: str, raw: str) -> str:
    return f"{project_id}::{raw}"


def convert(graphify_graph: dict, *, project_id: str, src_root: Path, source_revision: str,
            source_url_base: str, allow_prefixes: list[str], built_at_utc: str | None = None) -> dict:
    """source_url_base example: https://github.com/OWNER/REPO/blob/<sha>/"""
    built = built_at_utc or _now()
    src_root = Path(src_root)
    file_hash: dict[str, str] = {}
    blocked: dict[str, list[str]] = {}

    def file_sha(rel: str) -> str | None:
        if rel in file_hash:
            return file_hash[rel]
        if rel in blocked or not path_allowed(rel, allow_prefixes):
            blocked.setdefault(rel, ["PATH_NOT_ALLOWED"])
            return None
        p = src_root / rel
        if not p.is_file():
            blocked[rel] = ["SOURCE_MISSING"]
            return None
        flags = scan_sensitive_content(p.read_text(encoding="utf-8", errors="replace"))
        if flags:
            blocked[rel] = flags
            return None
        file_hash[rel] = sha256_file(p)
        return file_hash[rel]

    def prov(pid: str, rel: str | None, locator: str, evidence: str, relation: dict | None = None) -> dict:
        sha = file_sha(rel) if rel else None
        rec = {
            "id": pid, "project_id": project_id,
            "source_url": f"{source_url_base}{rel}" if rel else f"graphify:external:{locator}",
            "source_revision": source_revision, "updated_at_utc": built,
            "locator": locator or "unknown", "evidence_kind": evidence,
            "execution_status": "ACTUAL",
        }
        if rel and sha:
            rec.update(source_kind="FILE", sha256=sha,
                       verification_status="VERIFIED" if evidence == "EXTRACTED" else "UNVERIFIED")
        else:  # external module or unhashable source: never invent a hash
            rec.update(source_kind="EXTERNAL_REFERENCE", sha256=None, verification_status="UNVERIFIED")
        if relation:
            rec["relation"] = relation
        return rec

    nodes, edges, provs = [], [], []
    known: set[str] = set()
    for n in graphify_graph.get("nodes", []):
        rel = n.get("source_file") or None
        if rel and file_sha(rel) is None:
            continue  # blocked/denied source: drop the node entirely
        nid = _nid(project_id, n["id"])
        pid = f"prov:node:{nid}"
        provs.append(prov(pid, rel, f"{rel or n['id']}#{n.get('source_location', '')}".rstrip("#"), "EXTRACTED"))
        nodes.append({"id": nid, "project_id": project_id, "label": str(n.get("label", n["id"])),
                      "kind": str(n.get("file_type", "unknown")), "source_path": rel, "provenance_id": pid})
        known.add(nid)

    dropped_edges = 0
    for i, e in enumerate(graphify_graph.get("links", graphify_graph.get("edges", []))):
        a, b = _nid(project_id, e["source"]), _nid(project_id, e["target"])
        if a not in known or b not in known:
            dropped_edges += 1  # endpoint removed (blocked) or never existed
            continue
        eid = f"{project_id}::e{i}:{e['source']}->{e['target']}:{e.get('relation', 'related')}"
        pid = f"prov:edge:{eid}"
        rel = e.get("source_file") or None
        evidence = CONFIDENCE_MAP.get(str(e.get("confidence", "INFERRED")).upper(), "INFERRED")
        provs.append(prov(pid, rel, f"{rel or 'edge'}#{e.get('source_location', '')}".rstrip("#"), evidence,
                          {"from": a, "to": b, "type": str(e.get("relation", "related"))}))
        edges.append({"id": eid, "project_id": project_id, "from": a, "to": b,
                      "type": str(e.get("relation", "related")), "provenance_id": pid})

    graph = {
        "schema": "astra-graph/1", "project_id": project_id, "source_revision": source_revision,
        "built_at_utc": built,
        "generator": {"name": "astra_graphify", "version": VERSION, "extractor": f"{GRAPHIFY_PIN} ast-only"},
        "sources": [{"path": k, "sha256": v} for k, v in sorted(file_hash.items())],
        "nodes": nodes, "edges": edges, "provenance": provs,
    }
    check_integrity(graph)
    graph_report = {"blocked_sources": blocked, "dropped_edges": dropped_edges}
    return {"graph": graph, "report": graph_report}


def check_integrity(graph: dict) -> None:
    """Raise IntegrityError on any violation. Called before every write."""
    errs = graph_errors(graph)
    pid = graph["project_id"] if isinstance(graph, dict) else None
    prov_by_id: dict[str, dict] = {}
    for rec in graph.get("provenance", []):
        for m in provenance_errors(rec):
            errs.append(f"provenance {rec.get('id')}: {m}")
        if rec.get("project_id") != pid:
            errs.append(f"provenance {rec.get('id')}: CROSS_PROJECT")
        if rec.get("id") in prov_by_id:
            errs.append(f"provenance {rec.get('id')}: DUPLICATE_ID")
        prov_by_id[rec.get("id")] = rec
    node_ids: set[str] = set()
    for n in graph.get("nodes", []):
        if n["id"] in node_ids:
            errs.append(f"node {n['id']}: DUPLICATE_ID")
        node_ids.add(n["id"])
        if n["project_id"] != pid:
            errs.append(f"node {n['id']}: CROSS_PROJECT")
        if n["provenance_id"] not in prov_by_id:
            errs.append(f"node {n['id']}: PROVENANCE_MISSING")
    edge_ids: set[str] = set()
    for e in graph.get("edges", []):
        if e["id"] in edge_ids:
            errs.append(f"edge {e['id']}: DUPLICATE_ID")
        edge_ids.add(e["id"])
        if e["project_id"] != pid:
            errs.append(f"edge {e['id']}: CROSS_PROJECT")
        for end in ("from", "to"):
            if e[end] not in node_ids:
                errs.append(f"edge {e['id']}: DANGLING_{end.upper()}")
        p = prov_by_id.get(e["provenance_id"])
        if p is None:
            errs.append(f"edge {e['id']}: PROVENANCE_MISSING")
        elif p.get("relation") != {"from": e["from"], "to": e["to"], "type": e["type"]}:
            errs.append(f"edge {e['id']}: PROVENANCE_RELATION_MISMATCH")
    if errs:
        raise IntegrityError("; ".join(errs[:20]) + (f" (+{len(errs) - 20} more)" if len(errs) > 20 else ""))


def load_graphify(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
