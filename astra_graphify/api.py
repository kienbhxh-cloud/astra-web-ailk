"""Loopback-only, read-only HTTP API with Bearer authentication.

GET /api/graph/stats?project_id=...
GET /api/graph/search?q=...&project_id=...&top_k=...
GET /api/graph/node?id=...&project_id=...

Identity comes from ``Authorization: Bearer <token>`` only; ``project_id`` in
the query string is checked against that identity. Binding to anything but a
loopback address is refused.
"""
from __future__ import annotations

import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple
from urllib.parse import parse_qs, urlparse

from .engine import AuthorizedReader
from .security import AuthError

ROUTES = {"/api/graph/stats": "stats", "/api/graph/search": "search", "/api/graph/node": "node"}


def handle_request(reader: AuthorizedReader, method: str, path: str, headers) -> Tuple[int, dict]:
    if method != "GET":
        return 405, {"ok": False, "status": "READ_ONLY_API"}
    parsed = urlparse(path)
    op = ROUTES.get(parsed.path)
    if not op:
        return 404, {"ok": False, "status": "NOT_FOUND"}
    auth = headers.get("Authorization", "")
    token = auth[7:].strip() if auth.startswith("Bearer ") else ""
    try:
        principal = reader.registry.authenticate(token)
    except AuthError as exc:
        return 401, {"ok": False, "status": exc.code}
    qs = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    args = {"project_id": qs.get("project_id")}
    if op == "search":
        args["query"] = qs.get("q", "")
        try:
            args["top_k"] = int(qs.get("top_k", 8))
        except ValueError:
            return 400, {"ok": False, "status": "INVALID_TOP_K"}
    if op == "node":
        args["node_id"] = qs.get("id", "")
    res = reader.call(principal, op, args)
    if res.get("ok"):
        return 200, res
    return (403 if res.get("status") == "PROJECT_ACCESS_DENIED" else 400), res


def serve(reader: AuthorizedReader, host: str = "127.0.0.1", port: int = 3001) -> None:
    if not ipaddress.ip_address(host).is_loopback:
        raise SystemExit("REFUSED_NON_LOOPBACK_BIND")

    class Handler(BaseHTTPRequestHandler):
        def _reply(self):
            code, body = handle_request(reader, self.command, self.path, self.headers)
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        do_GET = do_POST = do_PUT = do_DELETE = _reply

        def log_message(self, fmt, *args):  # no query strings (may contain search terms) in logs
            pass

    ThreadingHTTPServer((host, port), Handler).serve_forever()
