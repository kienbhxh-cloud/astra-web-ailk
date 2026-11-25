"""Read-only queries over one authorized project snapshot. Sizes are reported in
characters (context_chars); token_count stays null until a real tokenizer is run."""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

_WORD = re.compile(r"[^\W_]+", re.UNICODE)  # split snake_case too


def _prov(graph: dict) -> dict:
    return {r["id"]: r for r in graph["provenance"]}


def _cite(rec: dict) -> dict:
    return {k: rec.get(k) for k in ("source_url", "source_revision", "sha256", "locator", "source_kind",
                                     "evidence_kind", "verification_status", "execution_status")}


def search(graph: dict, query: str, top_k: int = 10, max_chars: int = 4000) -> dict:
    top_k = max(1, min(int(top_k), 50))
    terms = set(t.lower() for t in _WORD.findall(query or ""))
    if not terms:
        return {"ok": False, "error": "EMPTY_QUERY"}
    prov = _prov(graph)
    degree = Counter()
    for e in graph["edges"]:
        degree[e["from"]] += 1
        degree[e["to"]] += 1
    scored = []
    for n in graph["nodes"]:
        hay = Counter(t.lower() for t in _WORD.findall(f"{n['label']} {n['source_path'] or ''} {n['id']}"))
        hits = [t for t in terms if hay[t]]
        if hits:
            scored.append((len(hits) + 0.1 * math.log1p(degree[n["id"]]), n))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    results, used = [], 0
    for score, n in scored[:top_k]:
        item = {"id": n["id"], "label": n["label"], "kind": n["kind"], "source_path": n["source_path"],
                "score": round(score, 3), "provenance": _cite(prov[n["provenance_id"]])}
        size = len(str(item))
        if used + size > max_chars:
            break
        used += size
        results.append(item)
    return {"ok": True, "project_id": graph["project_id"], "source_revision": graph["source_revision"],
            "total_hits": len(scored), "returned": len(results), "context_chars": used,
            "token_count": None, "results": results}


def neighbors(graph: dict, node_id: str, limit: int = 30) -> dict:
    ids = {n["id"]: n for n in graph["nodes"]}
    if node_id not in ids:
        return {"ok": False, "error": "NODE_NOT_FOUND"}
    prov = _prov(graph)
    out = []
    for e in graph["edges"]:
        if node_id in (e["from"], e["to"]):
            other = e["to"] if e["from"] == node_id else e["from"]
            out.append({"direction": "out" if e["from"] == node_id else "in", "type": e["type"],
                        "node": {"id": other, "label": ids[other]["label"]},
                        "provenance": _cite(prov[e["provenance_id"]])})
            if len(out) >= limit:
                break
    return {"ok": True, "node": {"id": node_id, "label": ids[node_id]["label"]}, "edges": out}


def stats(graph: dict) -> dict:
    by = defaultdict(Counter)
    for r in graph["provenance"]:
        by["evidence_kind"][r["evidence_kind"]] += 1
        by["verification_status"][r["verification_status"]] += 1
        by["source_kind"][r["source_kind"]] += 1
    return {"ok": True, "project_id": graph["project_id"], "source_revision": graph["source_revision"],
            "built_at_utc": graph["built_at_utc"], "generator": graph["generator"],
            "nodes": len(graph["nodes"]), "edges": len(graph["edges"]), "sources": len(graph["sources"]),
            "provenance": {k: dict(v) for k, v in by.items()}}
