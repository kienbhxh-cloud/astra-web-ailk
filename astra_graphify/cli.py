"""CLI: build | verify | stats | rollback | prune | mcp | serve.

build: copy ONLY allowlisted files into a sanitized work dir, run Graphify AST-only
(no LLM, API keys stripped from env), convert to ASTRA graph + provenance v1.2,
skip if the source fingerprint is unchanged, else validate-then-commit atomically.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import VERSION
from .convert import convert, load_graphify
from .query import stats
from .security import path_allowed, scan_sensitive_content
from .store import GraphStore, PruneRefused

LLM_ENV = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY",
           "MISTRAL_API_KEY", "OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "XAI_API_KEY")


def _stage(src: Path, work: Path, allow: list[str]) -> dict:
    """Mirror allowlisted, non-sensitive files into work/src (removing stale ones)."""
    dst = work / "src"
    dst.mkdir(parents=True, exist_ok=True)
    wanted, blocked = set(), {}
    for p in sorted(src.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(src).as_posix()
        if not path_allowed(rel, allow):
            continue
        flags = scan_sensitive_content(p.read_text(encoding="utf-8", errors="replace"))
        if flags:
            blocked[rel] = flags
            continue
        wanted.add(rel)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != p.read_bytes():
            shutil.copy2(p, target)
    for p in sorted(dst.rglob("*"), reverse=True):
        rel = p.relative_to(dst).as_posix()
        if rel.startswith("graphify-out"):
            continue
        if p.is_file() and rel not in wanted:
            p.unlink()
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()
    return {"staged": sorted(wanted), "blocked": blocked}


def cmd_build(a) -> int:
    t0 = time.monotonic()
    src, data = Path(a.src).resolve(), Path(a.data).resolve()
    store = GraphStore(data)
    work = data / ".work" / a.project
    staged = _stage(src, work, a.allow)
    env = {k: v for k, v in os.environ.items() if k not in LLM_ENV}
    t1 = time.monotonic()
    proc = subprocess.run([a.graphify_bin, "update", ".", "--no-cluster", "--force"], cwd=work / "src",
                          env=env, capture_output=True, text=True, timeout=a.timeout)
    t_graphify = time.monotonic() - t1
    report = {"tool": "astra_graphify", "version": VERSION, "project_id": a.project,
              "source_revision": a.revision, "started_utc": datetime.now(timezone.utc).isoformat(),
              "staged_files": len(staged["staged"]), "blocked_sources": staged["blocked"],
              "graphify_returncode": proc.returncode, "graphify_seconds": round(t_graphify, 3),
              "graphify_log_tail": (proc.stdout + proc.stderr)[-2000:]}
    if proc.returncode != 0:
        report.update(status="BLOCKED", reason="GRAPHIFY_FAILED")
        return _finish(a, report, 2)
    result = convert(load_graphify(work / "src" / "graphify-out" / "graph.json"), project_id=a.project,
                     src_root=work / "src", source_revision=a.revision, source_url_base=a.url_base,
                     allow_prefixes=a.allow)
    graph = result["graph"]
    report.update(result["report"])
    old = store.load(a.project)
    if old is not None and GraphStore.fingerprint(old) == GraphStore.fingerprint(graph) and not a.force:
        report.update(status="SKIPPED_UNCHANGED", nodes=len(old["nodes"]), edges=len(old["edges"]))
    else:
        committed = store.commit(graph)
        report.update(status="ACTUAL", store_status=committed["status"], nodes=committed["nodes"],
                      edges=committed["edges"])
        report["previous_fingerprint"] = GraphStore.fingerprint(old) if old else None
    report["fingerprint"] = GraphStore.fingerprint(graph)
    report["total_seconds"] = round(time.monotonic() - t0, 3)
    report["stats"] = stats(store.load(a.project))
    return _finish(a, report, 0)


def _finish(a, report: dict, code: int) -> int:
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if getattr(a, "report", None):
        Path(a.report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.report).write_text(text, encoding="utf-8")
    print(text)
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="astra_graphify")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--src", required=True)
    b.add_argument("--project", required=True)
    b.add_argument("--data", default="graphify-data")
    b.add_argument("--revision", required=True)
    b.add_argument("--url-base", required=True)
    b.add_argument("--allow", action="append", required=True, help="allowed path prefix (repeatable)")
    b.add_argument("--report")
    b.add_argument("--graphify-bin", default="graphify")
    b.add_argument("--timeout", type=int, default=600)
    b.add_argument("--force", action="store_true")
    for name in ("verify", "stats", "rollback"):
        s = sub.add_parser(name)
        s.add_argument("--project", required=True)
        s.add_argument("--data", default="graphify-data")
    pr = sub.add_parser("prune", help="apply a complete Drive/listing manifest")
    pr.add_argument("--project", required=True)
    pr.add_argument("--data", default="graphify-data")
    pr.add_argument("--manifest", required=True, help='{"complete": true, "paths": [...]}')
    pr.add_argument("--max-delete-ratio", type=float, default=0.2)
    sub.add_parser("mcp")
    sv = sub.add_parser("serve")
    sv.add_argument("--port", type=int, default=3001)
    a = ap.parse_args(argv)

    if a.cmd == "build":
        return cmd_build(a)
    if a.cmd == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main()
        return 0
    if a.cmd == "serve":
        from .api import serve
        serve(port=a.port)
        return 0
    store = GraphStore(a.data)
    if a.cmd == "verify":
        g = store.load(a.project)  # load() runs full integrity check
        print(json.dumps({"ok": g is not None, "status": "VERIFIED" if g else "NOT_BUILT"}))
        return 0 if g else 1
    if a.cmd == "stats":
        g = store.load(a.project)
        print(json.dumps(stats(g) if g else {"ok": False, "error": "NOT_BUILT"}, ensure_ascii=False, indent=1))
        return 0 if g else 1
    if a.cmd == "rollback":
        res = store.rollback(a.project)
        print(json.dumps(res))
        return 0 if res["ok"] else 1
    if a.cmd == "prune":
        m = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        try:
            res = store.prune_sources(a.project, set(m.get("paths", [])), listing_complete=m.get("complete") is True,
                                      max_delete_ratio=a.max_delete_ratio)
        except PruneRefused as exc:
            res = {"ok": False, "status": "REFUSED", "reason": str(exc)}
        print(json.dumps(res))
        return 0 if res["ok"] else 3
    return 1


if __name__ == "__main__":
    sys.exit(main())
