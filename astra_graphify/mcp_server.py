"""Read-only MCP server over stdio (Model Context Protocol, revision 2025-06-18).

Implements the lifecycle and tools surface of the specification rather than
an ad-hoc JSON-RPC echo:

* newline-delimited JSON-RPC 2.0 on stdin/stdout, logs only on stderr;
* ``initialize`` with protocol-version negotiation, ``notifications/initialized``;
* requests other than ``ping`` before initialization are refused;
* ``tools/list`` with JSON Schema ``inputSchema`` and ``readOnlyHint``;
* ``tools/call`` returning ``content`` + ``structuredContent`` and ``isError``;
* standard error codes (-32700, -32600, -32601, -32602, -32002);
* notifications never receive a response; batches are rejected (removed in 2025-06-18).

Identity: the caller token is read once from ``ASTRA_GRAPHIFY_TOKEN`` in the
server process environment and checked against ``ASTRA_GRAPHIFY_PRINCIPALS``.
A ``project_id`` tool argument is only a request, checked against that identity.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, TextIO

from . import PROTOCOL_VERSION, VERSION
from .engine import AuthorizedReader, KnowledgeStore
from .security import AuthError, CallerAuthRegistry, Principal

SUPPORTED_VERSIONS = (PROTOCOL_VERSION, "2025-03-26", "2024-11-05")

PARSE_ERROR, INVALID_REQUEST, METHOD_NOT_FOUND, INVALID_PARAMS, NOT_INITIALIZED = -32700, -32600, -32601, -32602, -32002

_PID = {"type": "string", "pattern": "^[A-Za-z0-9_-]{1,80}$",
        "description": "Project to read. Must be one the caller identity is allowed to read."}
TOOLS = [
    {"name": "graph_search", "title": "Search ASTRA knowledge graph",
     "description": "Keyword search over nodes of one authorized project. Every result carries provenance v1.2 and its knowledge layer (SOURCE/EXTRACTED/INFERRED/VERIFIED).",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string", "minLength": 1}, "project_id": _PID,
         "top_k": {"type": "integer", "minimum": 1, "maximum": 50}},
         "required": ["query"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "graph_node", "title": "Get node and its edges",
     "description": "Return one node with its incident edges (both endpoints are guaranteed to exist in the same project).",
     "inputSchema": {"type": "object", "properties": {
         "node_id": {"type": "string", "minLength": 1}, "project_id": _PID},
         "required": ["node_id"], "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
    {"name": "graph_stats", "title": "Graph statistics",
     "description": "Node/edge counts per knowledge layer and the last build record for one authorized project.",
     "inputSchema": {"type": "object", "properties": {"project_id": _PID}, "additionalProperties": False},
     "annotations": {"readOnlyHint": True, "openWorldHint": False}},
]
_OPS = {"graph_search": "search", "graph_node": "node", "graph_stats": "stats"}


def _check_args(tool: Dict[str, Any], args: Any) -> Optional[str]:
    if not isinstance(args, dict):
        return "arguments must be an object"
    schema = tool["inputSchema"]
    for req in schema.get("required", []):
        if req not in args:
            return f"missing required argument: {req}"
    for k, v in args.items():
        spec = schema["properties"].get(k)
        if spec is None:
            return f"unknown argument: {k}"
        if spec["type"] == "string" and (not isinstance(v, str) or len(v) < spec.get("minLength", 0)):
            return f"argument {k} must be a non-empty string"
        if spec["type"] == "integer" and (not isinstance(v, int) or isinstance(v, bool)
                                          or not spec["minimum"] <= v <= spec["maximum"]):
            return f"argument {k} out of range"
    return None


class McpServer:
    def __init__(self, reader: AuthorizedReader, principal: Optional[Principal], auth_error: Optional[str] = None):
        self.reader = reader
        self.principal = principal
        self.auth_error = auth_error or ("UNAUTHORIZED_CALLER" if principal is None else None)
        self.initialized = False
        self.negotiated: Optional[str] = None

    @staticmethod
    def _err(mid, code, message):
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    @staticmethod
    def _ok(mid, result):
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def handle_line(self, line: str) -> Optional[Dict[str, Any]]:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            return self._err(None, PARSE_ERROR, "Parse error")
        if isinstance(msg, list):
            return self._err(None, INVALID_REQUEST, "JSON-RPC batching is not supported in protocol 2025-06-18")
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or not isinstance(msg.get("method", ""), str):
            return self._err(msg.get("id") if isinstance(msg, dict) else None, INVALID_REQUEST, "Invalid Request")
        if "method" not in msg:
            return None  # a response from the client; this server sends no requests
        method, mid, is_note = msg["method"], msg.get("id"), "id" not in msg
        params = msg.get("params") or {}
        if is_note:
            if method == "notifications/initialized" and self.negotiated:
                self.initialized = True
            return None
        if method == "ping":
            return self._ok(mid, {})
        if method == "initialize":
            if not isinstance(params, dict) or not isinstance(params.get("protocolVersion"), str):
                return self._err(mid, INVALID_PARAMS, "initialize requires protocolVersion")
            req = params["protocolVersion"]
            self.negotiated = req if req in SUPPORTED_VERSIONS else PROTOCOL_VERSION
            return self._ok(mid, {
                "protocolVersion": self.negotiated,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "astra-graphify", "title": "ASTRA Graphify (read-only)", "version": VERSION},
                "instructions": "Read-only. Results are evidence pointers: check provenance.source_url and sha256 before relying on a claim. INFERRED is never a verified fact.",
            })
        if not self.initialized:
            return self._err(mid, NOT_INITIALIZED, "Server not initialized")
        if method == "tools/list":
            return self._ok(mid, {"tools": TOOLS})
        if method == "tools/call":
            if not isinstance(params, dict):
                return self._err(mid, INVALID_PARAMS, "params must be an object")
            name = params.get("name")
            tool = next((t for t in TOOLS if t["name"] == name), None)
            if tool is None:
                return self._err(mid, INVALID_PARAMS, f"Unknown tool: {name}")
            args = params.get("arguments", {})
            problem = _check_args(tool, args)
            if problem:
                return self._err(mid, INVALID_PARAMS, problem)
            if self.principal is None:
                data = {"ok": False, "status": self.auth_error}
            else:
                data = self.reader.call(self.principal, _OPS[name], args)
            return self._ok(mid, {
                "content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}],
                "structuredContent": data,
                "isError": not data.get("ok", False),
            })
        return self._err(mid, METHOD_NOT_FOUND, f"Method not found: {method}")

    def serve(self, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout) -> None:
        for line in stdin:
            if not line.strip():
                continue
            reply = self.handle_line(line)
            if reply is not None:
                stdout.write(json.dumps(reply, ensure_ascii=False, separators=(",", ":")) + "\n")
                stdout.flush()


def build_from_env(data_dir: Path) -> McpServer:
    registry = CallerAuthRegistry.from_env()
    reader = AuthorizedReader(KnowledgeStore(data_dir), registry)
    try:
        principal = registry.authenticate(os.environ.get("ASTRA_GRAPHIFY_TOKEN"))
        err = None
    except AuthError as exc:
        principal, err = None, exc.code
        print(f"astra-graphify mcp: {exc.code}; tools will return isError", file=sys.stderr)
    return McpServer(reader, principal, err)
