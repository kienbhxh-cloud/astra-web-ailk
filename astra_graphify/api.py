"""Loopback-only read API with Bearer auth. Binding to a non-loopback host is refused."""
from __future__ import annotations

import ipaddress
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .auth import AuthError, Authenticator, authorize
from .query import neighbors, search, stats
from .store import GraphStore

STATUS = {"UNAUTHENTICATED": 401, "AUTH_CONFIG_MISSING_FAIL_CLOSED": 503,
          "FORBIDDEN_PROJECT": 403, "PROJECT_ID_REQUIRED": 400}


def make_handler(store: GraphStore, auth: Authenticator, allow_origin: str = "http://localhost:3000"):
    class Handler(BaseHTTPRequestHandler):
        server_version = "astra-graphify"

        def log_message(self, *a):  # no request logging of query strings/tokens
            pass

        def _send(self, code: int, payload: dict):
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", allow_origin)
            self.send_header("Vary", "Origin")
            self.end_headers()
            self.wfile.write(raw)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", allow_origin)
            self.send_header("Access-Control-Allow-Headers", "Authorization")
            self.send_header("Access-Control-Allow-Methods", "GET")
            self.end_headers()

        def do_GET(self):
            u = urlparse(self.path)
            qs = {k: v[0] for k, v in parse_qs(u.query).items()}
            hdr = self.headers.get("Authorization", "")
            token = hdr[7:].strip() if hdr.lower().startswith("bearer ") else None
            try:
                project = authorize(auth.authenticate(token), qs.get("project_id"))
            except AuthError as exc:
                return self._send(STATUS.get(exc.code, 403), {"ok": False, "error": exc.code})
            graph = store.load(project)
            if graph is None:
                return self._send(404, {"ok": False, "error": "GRAPH_NOT_BUILT"})
            if u.path == "/api/graph/stats":
                res = stats(graph)
            elif u.path == "/api/graph/query":
                res = search(graph, qs.get("q", ""), top_k=int(qs.get("top_k", "10") or 10))
            elif u.path == "/api/graph/neighbors":
                res = neighbors(graph, qs.get("node_id", ""))
            else:
                return self._send(404, {"ok": False, "error": "NOT_FOUND"})
            self._send(200 if res.get("ok") else 400, res)

        def do_POST(self):
            self._send(405, {"ok": False, "error": "READ_ONLY"})
        do_PUT = do_DELETE = do_PATCH = do_POST

    return Handler


def serve(host: str = "127.0.0.1", port: int = 3001) -> None:
    if not ipaddress.ip_address(host).is_loopback:
        raise SystemExit("REFUSED_NON_LOOPBACK_BIND")
    store = GraphStore(os.environ.get("ASTRA_GRAPHIFY_DATA", "graphify-data"))
    ThreadingHTTPServer((host, port), make_handler(store, Authenticator.from_file())).serve_forever()
