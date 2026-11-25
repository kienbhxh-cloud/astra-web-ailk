"""Read-only MCP server over stdio (MCP revision 2025-06-18, newline-delimited JSON-RPC 2.0).

Lifecycle: initialize -> notifications/initialized -> tools/list | tools/call | ping.
Caller identity: ASTRA_GRAPHIFY_TOKEN (env) authenticated against the principals file;
the project_id argument is checked against that principal's allowlist.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Callable

from . import VERSION
from .auth import AuthError, Authenticator, Principal, authorize
from .query import neighbors, search, stats
from .store import GraphStore

SUPPORTED_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS = -32700, -32600, -32601, -32602

_PROJECT = {"type": "string", "description": "Project to read; must be allowed for the caller"}
TOOLS = [
    {"name": "graph_search", "title": "Search ASTRA knowledge graph",
     "description": "Keyword search over node labels and paths with provenance for each hit.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["query"],
                     "properties": {"query": {"type": "string", "minLength": 1}, "project_id": _PROJECT,
                                    "top_k": {"type": "integer", "minimum": 1, "maximum": 50}}},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "graph_neighbors", "title": "Neighbors of a node",
     "description": "Edges in/out of one node with provenance.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["node_id"],
                     "properties": {"node_id": {"type": "string", "minLength": 1}, "project_id": _PROJECT}},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "graph_stats", "title": "Graph statistics",
     "description": "Counts, build revision and provenance status breakdown.",
     "inputSchema": {"type": "object", "additionalProperties": False, "properties": {"project_id": _PROJECT}},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
]


class McpServer:
    def __init__(self, store: GraphStore, principal: Principal | None):
        self.store, self.principal, self.initialized = store, principal, False

    @staticmethod
    def _err(rid, code: int, message: str) -> dict:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}

    @staticmethod
    def _ok(rid, result: dict) -> dict:
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def handle_line(self, line: str) -> dict | None:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return self._err(None, PARSE_ERROR, "Parse error")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method"), str):
            if isinstance(msg, dict) and "method" not in msg and ("result" in msg or "error" in msg):
                return None  # a response to us; we never send requests, ignore
            return self._err(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "Invalid Request")
        method, params = msg["method"], msg.get("params") or {}
        if "id" not in msg:  # notification: never answered
            if method == "notifications/initialized":
                self.initialized = True
            return None
        rid = msg["id"]
        if not isinstance(params, dict):
            return self._err(rid, INVALID_PARAMS, "params must be an object")
        if method == "initialize":
            requested = params.get("protocolVersion")
            version = requested if requested in SUPPORTED_VERSIONS else SUPPORTED_VERSIONS[0]
            return self._ok(rid, {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "astra-graphify", "title": "ASTRA GRAPHIFY (read-only)", "version": VERSION},
                "instructions": "Read-only. Every result carries provenance; INFERRED edges are never VERIFIED."})
        if method == "ping":
            return self._ok(rid, {})
        handlers: dict[str, Callable[[Any, dict], dict]] = {"tools/list": self._tools_list, "tools/call": self._tools_call}
        if method not in handlers:
            return self._err(rid, METHOD_NOT_FOUND, f"Method not found: {method}")
        return handlers[method](rid, params)

    def _tools_list(self, rid, params: dict) -> dict:
        return self._ok(rid, {"tools": TOOLS})

    def _tool_result(self, rid, payload: dict, is_error: bool) -> dict:
        return self._ok(rid, {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}],
                              "structuredContent": payload, "isError": is_error})

    def _tools_call(self, rid, params: dict) -> dict:
        name, args = params.get("name"), params.get("arguments") or {}
        tool = next((t for t in TOOLS if t["name"] == name), None)
        if tool is None:
            return self._err(rid, INVALID_PARAMS, f"Unknown tool: {name}")
        if not isinstance(args, dict):
            return self._err(rid, INVALID_PARAMS, "arguments must be an object")
        allowed = set(tool["inputSchema"]["properties"])
        missing = [k for k in tool["inputSchema"].get("required", []) if not args.get(k)]
        extra = sorted(set(args) - allowed)
        if missing or extra:
            return self._err(rid, INVALID_PARAMS, f"missing={missing} unexpected={extra}")
        try:
            if self.principal is None:
                raise AuthError("UNAUTHENTICATED")
            project = authorize(self.principal, args.get("project_id"))
            graph = self.store.load(project)
            if graph is None:
                return self._tool_result(rid, {"ok": False, "error": "GRAPH_NOT_BUILT", "project_id": project}, True)
            if name == "graph_search":
                res = search(graph, str(args["query"]), top_k=int(args.get("top_k", 10)))
            elif name == "graph_neighbors":
                res = neighbors(graph, str(args["node_id"]))
            else:
                res = stats(graph)
            return self._tool_result(rid, res, not res.get("ok", False))
        except AuthError as exc:
            return self._tool_result(rid, {"ok": False, "error": exc.code}, True)
        except Exception as exc:  # integrity failure etc.: report, never crash the server
            return self._tool_result(rid, {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:300]}, True)


def main() -> None:
    store = GraphStore(os.environ.get("ASTRA_GRAPHIFY_DATA", "graphify-data"))
    principal = None
    try:
        principal = Authenticator.from_file().authenticate(os.environ.get("ASTRA_GRAPHIFY_TOKEN"))
    except AuthError as exc:
        print(f"[astra-graphify] auth: {exc.code} — tool calls will be refused", file=sys.stderr)
    server = McpServer(store, principal)
    for line in sys.stdin:
        if not line.strip():
            continue
        out = server.handle_line(line)
        if out is not None:
            sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
