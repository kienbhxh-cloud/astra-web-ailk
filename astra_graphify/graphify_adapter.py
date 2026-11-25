"""Convert an upstream Graphify ``graph.json`` into ASTRA envelopes.

Upstream: https://github.com/Graphify-Labs/graphify, package ``graphifyy``
(Apache-2.0), pinned in requirements-graphify.lock. Only the AST path
(``graphify extract --code-only``) is used: no language-model calls, no API
keys, nothing leaves the runner.

What this layer adds that Graphify does not have:
* provenance v1.2 for every node and edge (file sha256, revision, locator);
* allowlist / denylist of source paths and a secret/BHXH content guard;
* knowledge layers SOURCE / EXTRACTED / INFERRED / VERIFIED;
* a mechanical verification pass (hash + line check) that is the only way a
  record becomes VERIFIED — INFERRED edges are never verified.
"""
from __future__ import annotations

import fnmatch
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .engine import SourceBatch
from .security import scan_sensitive, sha256_bytes, sha256_str
from .validator import derive_layer

EXTERNAL_SOURCE = "__external__"


def load_allowlist(path: Path) -> Dict[str, Any]:
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    for key in ("project_id", "include", "exclude"):
        if key not in cfg:
            raise ValueError(f"ALLOWLIST_MISSING_KEY:{key}")
    return cfg


def path_allowed(rel: str, cfg: Dict[str, Any]) -> bool:
    rel = rel.replace("\\", "/")
    if rel.startswith("/") or ".." in rel.split("/"):
        return False
    if any(fnmatch.fnmatch(rel, pat) for pat in cfg["exclude"]):
        return False
    return any(fnmatch.fnmatch(rel, pat) for pat in cfg["include"])


def _symbol_name(label: str) -> str:
    name = label.strip()
    name = re.sub(r"\(.*\)$", "", name)
    return name.lstrip(".").split(".")[-1]


def _line(lines: List[str], loc: Optional[str]) -> Optional[str]:
    m = re.fullmatch(r"L(\d+)", loc or "")
    if not m:
        return None
    n = int(m.group(1))
    return lines[n - 1] if 1 <= n <= len(lines) else None


def convert(
    graph: Dict[str, Any],
    repo_root: Path,
    cfg: Dict[str, Any],
    source_revision: str,
    repo_slug: str,
    verify: bool = True,
) -> Tuple[List[SourceBatch], Dict[str, Any]]:
    project = cfg["project_id"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report = defaultdict(int)
    report["blocked_files"] = []

    files: Dict[str, Dict[str, Any]] = {}

    def file_info(rel: str) -> Optional[Dict[str, Any]]:
        if rel in files:
            return files[rel]
        info = None
        p = (repo_root / rel)
        if path_allowed(rel, cfg) and p.is_file():
            data = p.read_bytes()
            text = data.decode("utf-8", errors="replace")
            flags = scan_sensitive(text)
            if flags:
                report["blocked_files"].append({"file": rel, "flags": flags})
            else:
                info = {"sha256": sha256_bytes(data), "lines": text.splitlines()}
        elif not path_allowed(rel, cfg):
            report["files_outside_allowlist"] += 1
        files[rel] = info
        return info

    def nid(gid: str) -> str:
        return f"{project}:{gid}"

    def url(rel: str, loc: Optional[str]) -> str:
        frag = f"#{loc}" if loc and re.fullmatch(r"L\d+", loc) else ""
        return f"https://github.com/{repo_slug}/blob/{source_revision}/{rel}{frag}"

    nodes_by_src: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    kept_nodes: Dict[str, Dict[str, Any]] = {}
    for n in graph.get("nodes", []):
        gid, label = str(n["id"]), str(n.get("label") or n["id"])[:512]
        rel = n.get("source_file")
        loc = n.get("source_location") or "L1"
        if rel:
            info = file_info(rel)
            if info is None:
                report["nodes_skipped_source"] += 1
                continue
            is_file = Path(rel).name == label
            line = _line(info["lines"], loc)
            verified = False
            if verify:
                verified = True if is_file else bool(line and _symbol_name(label) and _symbol_name(label) in line)
            record = {"id": nid(gid), "project_id": project, "kind": "node", "label": label,
                      "node_type": "FILE" if is_file else "SYMBOL", "source_file": rel}
            if line and not is_file:
                record["snippet"] = line.strip()[:200]
            prov = {"id": nid(gid), "project_id": project, "source_url": url(rel, loc),
                    "source_revision": source_revision, "updated_at_utc": now, "source_kind": "FILE",
                    "sha256": info["sha256"], "locator": f"{rel}:{loc}", "evidence_kind": "EXTRACTED",
                    "verification_status": "VERIFIED" if verified else "UNVERIFIED",
                    "execution_status": "ACTUAL"}
            src = rel
        else:
            record = {"id": nid(gid), "project_id": project, "kind": "node", "label": label,
                      "node_type": "EXTERNAL"}
            prov = {"id": nid(gid), "project_id": project, "source_url": f"external:{label}",
                    "source_revision": source_revision, "updated_at_utc": now,
                    "source_kind": "EXTERNAL_REFERENCE", "sha256": None, "locator": gid,
                    "evidence_kind": "EXTRACTED", "verification_status": "UNVERIFIED",
                    "execution_status": "ACTUAL"}
            src = EXTERNAL_SOURCE
        record["knowledge_layer"] = derive_layer(record, prov)
        env = {"record": record, "provenance": prov}
        nodes_by_src[src].append(env)
        kept_nodes[gid] = env

    edges_by_src: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    seen_edges = set()
    for e in graph.get("edges", graph.get("links", [])):
        s, t, rel_type = str(e["source"]), str(e["target"]), str(e.get("relation", "related"))[:80]
        if s not in kept_nodes or t not in kept_nodes:
            report["edges_dropped_endpoint"] += 1
            continue
        rel = e.get("source_file") or kept_nodes[s]["record"].get("source_file")
        info = file_info(rel) if rel else None
        if info is None:
            report["edges_dropped_source"] += 1
            continue
        loc = e.get("source_location") or "L1"
        eid_raw = f"{s}|{rel_type}|{t}|{loc}"
        if eid_raw in seen_edges:
            report["edges_duplicate"] += 1
            continue
        seen_edges.add(eid_raw)
        conf = str(e.get("confidence", "EXTRACTED")).upper()
        evidence = "EXTRACTED" if conf == "EXTRACTED" else "INFERRED"
        verified = False
        if verify and evidence == "EXTRACTED":
            line = _line(info["lines"], loc)
            tname = _symbol_name(kept_nodes[t]["record"]["label"])
            tname = Path(tname).stem if kept_nodes[t]["record"]["node_type"] == "FILE" else tname
            verified = bool(line and tname and tname.split("/")[-1] in line)
        eid = f"{project}:e:{sha256_str(eid_raw)[:24]}"
        record = {"id": eid, "project_id": project, "kind": "edge", "source": nid(s),
                  "target": nid(t), "relation": rel_type}
        prov = {"id": eid, "project_id": project, "source_url": url(rel, loc),
                "source_revision": source_revision, "updated_at_utc": now, "source_kind": "FILE",
                "sha256": info["sha256"], "locator": f"{rel}:{loc}", "evidence_kind": evidence,
                "verification_status": "VERIFIED" if verified else "UNVERIFIED",
                "execution_status": "ACTUAL",
                "relation": {"from": nid(s), "to": nid(t), "type": rel_type}}
        record["knowledge_layer"] = derive_layer(record, prov)
        edges_by_src[rel].append({"record": record, "provenance": prov})

    batches = []
    for src in sorted(set(nodes_by_src) | set(edges_by_src)):
        envs = nodes_by_src.get(src, []) + edges_by_src.get(src, [])
        if src == EXTERNAL_SOURCE:
            sha = sha256_str(json.dumps(sorted(x["record"]["id"] for x in envs)))
        else:
            # content hash + revision-independent: unchanged file => skipped (incremental)
            sha = sha256_str(files[src]["sha256"] + "|" + sha256_str(json.dumps(
                sorted(x["record"]["id"] for x in envs))))
        batches.append(SourceBatch(f"{project}|{src}", sha, envs))
    report["source_batches"] = len(batches)
    report["nodes_in"] = len(graph.get("nodes", []))
    report["edges_in"] = len(graph.get("edges", graph.get("links", [])))
    report["nodes_out"] = len(kept_nodes)
    report["edges_out"] = sum(len(v) for v in edges_by_src.values())
    return batches, dict(report)
