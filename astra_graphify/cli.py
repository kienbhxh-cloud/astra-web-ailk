"""Command line: python -m astra_graphify <command> ...

build          ingest an upstream Graphify graph.json (AST, --code-only) into the store
stats          print per-layer counts for a project
rollback       restore the previous snapshot
export-public  write a web-safe graph JSON (only for allowlists marked "public": true)
mcp            run the read-only MCP stdio server
serve          run the loopback read-only HTTP API
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import VERSION
from .engine import AuthorizedReader, KnowledgeStore
from .graphify_adapter import EXTERNAL_SOURCE, convert, load_allowlist, path_allowed
from .security import CallerAuthRegistry


def _git_rev(root: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "local-uncommitted"


def _allowed_files(root: Path, cfg) -> set:
    try:
        listed = subprocess.check_output(["git", "-C", str(root), "ls-files"], text=True).splitlines()
    except Exception:
        listed = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()]
    return {f for f in listed if path_allowed(f, cfg)}


def cmd_build(a) -> int:
    root = Path(a.repo_root).resolve()
    cfg = load_allowlist(Path(a.allowlist))
    graph = json.loads(Path(a.graph).read_text(encoding="utf-8"))
    rev = a.revision or _git_rev(root)
    batches, report = convert(graph, root, cfg, rev, a.repo)
    store = KnowledgeStore(Path(a.data))
    active = None
    if a.prune:
        # git ls-files is a complete local listing; Drive listings come from drive_connector
        files = _allowed_files(root, cfg)
        active = {f"{cfg['project_id']}|{f}" for f in files} | {f"{cfg['project_id']}|{EXTERNAL_SOURCE}"}
    result = store.apply_build(cfg["project_id"], batches, active_sources=active,
                               listing_complete=a.prune, source_revision=rev)
    out = {"engine_version": VERSION, "source_revision": rev, "adapter": report,
           "store": {k: v for k, v in result.items() if k != "errors"},
           "errors": result.get("errors", [])[:50], "stats": store.stats(cfg["project_id"])}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if a.report:
        Path(a.report).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["ok"] else 2


def cmd_stats(a) -> int:
    print(json.dumps(KnowledgeStore(Path(a.data)).stats(a.project), ensure_ascii=False, indent=2))
    return 0


def cmd_rollback(a) -> int:
    res = KnowledgeStore(Path(a.data)).rollback()
    print(json.dumps(res))
    return 0 if res["ok"] else 1


def cmd_export(a) -> int:
    cfg = load_allowlist(Path(a.allowlist))
    if cfg.get("public") is not True:
        print("REFUSED: allowlist is not marked public; private graphs must stay off the repository", file=sys.stderr)
        return 3
    store = KnowledgeStore(Path(a.data))
    pid = cfg["project_id"]
    nodes = sorted((e for e in store.state["nodes"].values() if e["record"]["project_id"] == pid),
                   key=lambda e: e["record"]["id"])
    edges = sorted((e for e in store.state["edges"].values() if e["record"]["project_id"] == pid),
                   key=lambda e: e["record"]["id"])
    stats = store.stats(pid)
    doc = {
        "format": "astra-graphify-public/1", "engine_version": VERSION, "project_id": pid,
        "exported_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_revision": (stats.get("last_build") or {}).get("source_revision"),
        "extractor": cfg.get("extractor", {}),
        "stats": stats,
        "token_savings": {"status": "NOT_MEASURED",
                          "note": "No tokenizer-based A/B measurement has been run. Do not quote a saving."},
        "nodes": nodes, "edges": edges,
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "nodes": len(nodes), "edges": len(edges)}))
    return 0


def cmd_mcp(a) -> int:
    from .mcp_server import build_from_env
    build_from_env(Path(a.data)).serve()
    return 0


def cmd_serve(a) -> int:
    from .api import serve
    serve(AuthorizedReader(KnowledgeStore(Path(a.data)), CallerAuthRegistry.from_env()), a.host, a.port)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="astra_graphify", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--graph", required=True, help="graphify-out/graph.json from `graphify extract --code-only`")
    b.add_argument("--allowlist", required=True)
    b.add_argument("--data", required=True, help="store directory (outside the repo for private projects)")
    b.add_argument("--repo-root", default=".")
    b.add_argument("--repo", default="kienbhxh-cloud/astra-web-ailk")
    b.add_argument("--revision")
    b.add_argument("--prune", action="store_true", help="remove sources no longer present (complete git listing)")
    b.add_argument("--report")
    b.set_defaults(fn=cmd_build)

    s = sub.add_parser("stats"); s.add_argument("--data", required=True); s.add_argument("--project", required=True)
    s.set_defaults(fn=cmd_stats)
    r = sub.add_parser("rollback"); r.add_argument("--data", required=True); r.set_defaults(fn=cmd_rollback)
    e = sub.add_parser("export-public")
    e.add_argument("--data", required=True); e.add_argument("--allowlist", required=True); e.add_argument("--out", required=True)
    e.set_defaults(fn=cmd_export)
    m = sub.add_parser("mcp"); m.add_argument("--data", required=True); m.set_defaults(fn=cmd_mcp)
    v = sub.add_parser("serve"); v.add_argument("--data", required=True)
    v.add_argument("--host", default="127.0.0.1"); v.add_argument("--port", type=int, default=3001)
    v.set_defaults(fn=cmd_serve)

    a = p.parse_args(argv)
    return a.fn(a)
