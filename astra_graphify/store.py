"""Graph store: validate-then-commit, atomic snapshots, one-step rollback, guarded prune.

Fixes over v1.1 (Gemini):
- No state mutation before the full candidate snapshot passes integrity checks.
- Prune refuses incomplete listings and mass deletions (Drive can return partial pages).
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

from .convert import check_integrity


class PruneRefused(RuntimeError):
    pass


class GraphStore:
    def __init__(self, data_dir: Path):
        self.dir = Path(data_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, project_id: str) -> Path:
        if not project_id or not all(c.isalnum() or c in "_-" for c in project_id):
            raise ValueError("INVALID_PROJECT_ID")
        return self.dir / f"{project_id}.graph.json"

    def load(self, project_id: str) -> dict | None:
        p = self._path(project_id)
        if not p.exists():
            return None
        graph = json.loads(p.read_text(encoding="utf-8"))
        check_integrity(graph)  # never serve a corrupted snapshot
        return graph

    @staticmethod
    def fingerprint(graph: dict) -> str:
        """Content fingerprint of sources + extractor; equal fingerprint => skip rebuild/commit."""
        import hashlib
        h = hashlib.sha256(graph["generator"]["extractor"].encode())
        for s in sorted(graph["sources"], key=lambda s: s["path"]):
            h.update(f"{s['path']}\0{s['sha256']}\n".encode())
        return h.hexdigest()

    def commit(self, graph: dict) -> dict:
        """Validate the whole candidate first; only then write atomically, keeping .prev for rollback."""
        candidate = copy.deepcopy(graph)
        check_integrity(candidate)
        p = self._path(candidate["project_id"])
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(candidate, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
        if p.exists():
            os.replace(p, p.with_suffix(".json.prev"))
        os.replace(tmp, p)
        return {"ok": True, "status": "COMMITTED", "nodes": len(candidate["nodes"]),
                "edges": len(candidate["edges"])}

    def rollback(self, project_id: str) -> dict:
        p = self._path(project_id)
        prev = p.with_suffix(".json.prev")
        if not prev.exists():
            return {"ok": False, "status": "NO_PREVIOUS_SNAPSHOT"}
        check_integrity(json.loads(prev.read_text(encoding="utf-8")))
        os.replace(prev, p)
        return {"ok": True, "status": "ROLLED_BACK"}

    def prune_sources(self, project_id: str, active_paths: set[str], *, listing_complete: bool,
                      max_delete_ratio: float = 0.2) -> dict:
        """Remove nodes of sources that disappeared. Refuses when the listing is not known complete
        or when it would delete more than max_delete_ratio of sources (likely a partial listing)."""
        if not listing_complete:
            raise PruneRefused("LISTING_INCOMPLETE_NO_DELETE")
        graph = self.load(project_id)
        if graph is None:
            return {"ok": True, "removed_sources": 0}
        current = {s["path"] for s in graph["sources"]}
        gone = current - set(active_paths)
        if current and len(gone) / len(current) > max_delete_ratio:
            raise PruneRefused(f"MASS_DELETE_REFUSED:{len(gone)}/{len(current)}")
        if not gone:
            return {"ok": True, "removed_sources": 0}
        g = copy.deepcopy(graph)
        g["sources"] = [s for s in g["sources"] if s["path"] not in gone]
        g["nodes"] = [n for n in g["nodes"] if n["source_path"] not in gone]
        ids = {n["id"] for n in g["nodes"]}
        g["edges"] = [e for e in g["edges"] if e["from"] in ids and e["to"] in ids]
        used = {n["provenance_id"] for n in g["nodes"]} | {e["provenance_id"] for e in g["edges"]}
        g["provenance"] = [r for r in g["provenance"] if r["id"] in used]
        self.commit(g)
        return {"ok": True, "removed_sources": len(gone)}
