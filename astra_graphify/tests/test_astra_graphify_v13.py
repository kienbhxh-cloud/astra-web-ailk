"""Regression suite for ASTRA Graphify 1.3 (integration of ChatGPT v1.2 schema,
Gemini v1.1/v1.2 engine design and the upstream Graphify AST graph).

Uses the OFFICIAL provenance-v1.2 schema, not a minimal stand-in.
Run: python -m unittest discover -s astra_graphify/tests -v
"""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from astra_graphify import validator  # noqa: E402
from astra_graphify.api import handle_request  # noqa: E402
from astra_graphify.drive_connector import ReadOnlyDriveConnector  # noqa: E402
from astra_graphify.engine import AuthorizedReader, KnowledgeStore, SourceBatch  # noqa: E402
from astra_graphify.graphify_adapter import convert  # noqa: E402
from astra_graphify.mcp_server import McpServer  # noqa: E402
from astra_graphify.security import AuthError, CallerAuthRegistry, sha256_str  # noqa: E402

TOKEN_A = "fixture-token-A-" + "x" * 32
TOKEN_B = "fixture-token-B-" + "y" * 32
H = "a" * 64


def node(pid, nid, label="Thing", layer="EXTRACTED", node_type="SYMBOL", **prov):
    p = dict(id=nid, project_id=pid, source_url="https://example.org/f.py", source_revision="r1",
             updated_at_utc="2026-11-25T00:00:00Z", source_kind="FILE", sha256=H, locator="f.py:L1",
             evidence_kind="EXTRACTED", verification_status="UNVERIFIED", execution_status="MOCK")
    p.update(prov)
    return {"record": {"id": nid, "project_id": pid, "kind": "node", "label": label,
                       "node_type": node_type, "knowledge_layer": layer, "snippet": f"def {label}():"},
            "provenance": p}


def edge(pid, eid, s, t, rel="calls", layer="EXTRACTED", **prov):
    p = dict(id=eid, project_id=pid, source_url="https://example.org/f.py", source_revision="r1",
             updated_at_utc="2026-11-25T00:00:00Z", source_kind="FILE", sha256=H, locator="f.py:L2",
             evidence_kind="EXTRACTED", verification_status="UNVERIFIED", execution_status="MOCK",
             relation={"from": s, "to": t, "type": rel})
    p.update(prov)
    return {"record": {"id": eid, "project_id": pid, "kind": "edge", "source": s, "target": t,
                       "relation": rel, "knowledge_layer": layer}, "provenance": p}


def registry():
    return CallerAuthRegistry({
        "agent_a": {"token_sha256": sha256_str(TOKEN_A), "allowed_projects": ["PA"]},
        "agent_b": {"token_sha256": sha256_str(TOKEN_B), "allowed_projects": ["PA", "PB"]},
    })


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.store = KnowledgeStore(self.dir / "store")

    def tearDown(self):
        self.tmp.cleanup()

    def seed(self):
        res = self.store.apply_build("PA", [SourceBatch("PA|f.py", "s1", [
            node("PA", "PA:a", "alpha"), node("PA", "PA:b", "beta"), edge("PA", "PA:e1", "PA:a", "PA:b")])])
        self.assertTrue(res["ok"], res)
        res = self.store.apply_build("PB", [SourceBatch("PB|g.py", "s1", [node("PB", "PB:secret", "alpha")])])
        self.assertTrue(res["ok"], res)


class ValidationTests(Base):
    def test_official_schema_rejects_invalid_date(self):
        """Regression: Actions run 45534426217 failed because date-time was not checked."""
        ok, errs = validator.validate_envelope(node("PA", "PA:a", updated_at_utc="invalid"))
        self.assertFalse(ok)
        self.assertTrue(any("date-time" in e for e in errs), errs)

    def test_fail_closed_without_date_time_checker(self):
        validator._validator.cache_clear()
        from jsonschema import FormatChecker
        with mock.patch.object(FormatChecker, "checkers", {}):
            ok, errs = validator.validate_envelope(node("PA", "PA:a"))
        validator._validator.cache_clear()
        self.assertFalse(ok)
        self.assertIn("DATE_TIME_FORMAT_CHECKER_MISSING", errs[0])

    def test_fail_closed_missing_schema(self):
        ok, errs = validator.validate_envelope(node("PA", "PA:a"), provenance_schema=self.dir / "missing.json")
        self.assertFalse(ok)
        self.assertIn("SCHEMA_MISSING_FAIL_CLOSED", errs[0])

    def test_inferred_cannot_be_verified(self):
        ok, _ = validator.validate_envelope(edge("PA", "e", "a", "b", layer="VERIFIED", evidence_kind="INFERRED",
                                                 verification_status="VERIFIED", execution_status="ACTUAL"))
        self.assertFalse(ok)

    def test_external_reference_null_hash(self):
        env = node("PA", "PA:x", "fs", node_type="EXTERNAL", source_kind="EXTERNAL_REFERENCE", sha256=None)
        self.assertTrue(validator.validate_envelope(env)[0])
        env["provenance"]["verification_status"] = "VERIFIED"
        self.assertFalse(validator.validate_envelope(env)[0])

    def test_layer_must_match_evidence(self):
        ok, errs = validator.validate_envelope(node("PA", "PA:a", layer="VERIFIED"))
        self.assertFalse(ok)
        self.assertTrue(any("KNOWLEDGE_LAYER_MISMATCH" in e for e in errs))

    def test_verified_requires_actual(self):
        ok, errs = validator.validate_envelope(node("PA", "PA:a", layer="VERIFIED", verification_status="VERIFIED"))
        self.assertIn("VERIFIED_REQUIRES_ACTUAL_EXECUTION", errs)

    def test_layers_distinguish_source_extracted_inferred_verified(self):
        self.assertEqual(validator.derive_layer({"kind": "node", "node_type": "FILE"}, {"verification_status": "VERIFIED"}), "SOURCE")
        self.assertEqual(validator.derive_layer({"kind": "edge"}, {"evidence_kind": "EXTRACTED"}), "EXTRACTED")
        self.assertEqual(validator.derive_layer({"kind": "edge"}, {"evidence_kind": "INFERRED"}), "INFERRED")
        self.assertEqual(validator.derive_layer({"kind": "edge"}, {"evidence_kind": "EXTRACTED", "verification_status": "VERIFIED"}), "VERIFIED")

    def test_edge_provenance_relation_must_match(self):
        env = edge("PA", "e", "a", "b")
        env["provenance"]["relation"]["to"] = "c"
        self.assertIn("EDGE_PROVENANCE_RELATION_MISMATCH", validator.validate_envelope(env)[1])


class StoreTests(Base):
    def test_update_is_transactional(self):
        """Regression (Gemini v1.1): state changed before validation finished."""
        self.seed()
        before = (self.dir / "store" / "graph.json").read_bytes()
        bad = SourceBatch("PA|f.py", "s2", [node("PA", "PA:a", "alpha2"), node("PA", "PA:z", updated_at_utc="bad")])
        res = self.store.apply_build("PA", [bad])
        self.assertFalse(res["ok"])
        self.assertEqual(res["status"], "REJECTED_NO_CHANGE")
        self.assertEqual((self.dir / "store" / "graph.json").read_bytes(), before)
        self.assertEqual(self.store.state["nodes"]["PA:a"]["record"]["label"], "alpha")

    def test_edge_endpoints_must_exist(self):
        res = self.store.apply_build("PA", [SourceBatch("PA|f.py", "s", [node("PA", "PA:a"), edge("PA", "PA:e", "PA:a", "PA:ghost")])])
        self.assertFalse(res["ok"])
        self.assertTrue(any("EDGE_ENDPOINT_MISSING" in e and "target" in e for e in res["errors"]))
        res = self.store.apply_build("PA", [SourceBatch("PA|f.py", "s", [node("PA", "PA:a"), edge("PA", "PA:e", "PA:ghost", "PA:a")])])
        self.assertTrue(any("EDGE_ENDPOINT_MISSING" in e and "source" in e for e in res["errors"]))
        self.assertEqual(self.store.state["nodes"], {})

    def test_cross_project_edge_denied(self):
        self.seed()
        res = self.store.apply_build("PA", [SourceBatch("PA|h.py", "s", [edge("PA", "PA:x", "PA:a", "PB:secret")])])
        self.assertFalse(res["ok"])
        self.assertTrue(any("CROSS_PROJECT_EDGE_DENIED" in e for e in res["errors"]))

    def test_incremental_skip_unchanged(self):
        self.seed()
        res = self.store.apply_build("PA", [SourceBatch("PA|f.py", "s1", [])])
        self.assertEqual(res["status"], "NO_CHANGE")
        self.assertEqual(res["sources_unchanged"], 1)

    def test_prune_aborts_on_incomplete_listing(self):
        self.seed()
        res = self.store.apply_build("PA", [], active_sources=set(), listing_complete=False)
        self.assertEqual(res["prune_status"], "PRUNE_ABORTED_INCOMPLETE_LISTING")
        self.assertIn("PA:a", self.store.state["nodes"])

    def test_prune_ratio_guard(self):
        self.seed()
        res = self.store.apply_build("PA", [], active_sources=set(), listing_complete=True)
        self.assertFalse(res["ok"])
        self.assertEqual(res["prune_status"], "PRUNE_ABORTED_RATIO_GUARD")
        self.assertIn("PA:a", self.store.state["nodes"])
        res = self.store.apply_build("PA", [], active_sources=set(), listing_complete=True, allow_mass_prune=True)
        self.assertTrue(res["ok"])
        self.assertNotIn("PA:a", self.store.state["nodes"])
        self.assertIn("PB:secret", self.store.state["nodes"])  # other project untouched

    def test_rollback_restores_previous(self):
        self.seed()
        self.store.apply_build("PA", [SourceBatch("PA|f.py", "s2", [node("PA", "PA:a", "renamed")])])
        self.assertNotIn("PA:b", self.store.state["nodes"])
        self.assertTrue(self.store.rollback()["ok"])
        self.assertIn("PA:b", self.store.state["nodes"])
        reopened = KnowledgeStore(self.dir / "store")
        self.assertEqual(reopened.state["nodes"]["PA:a"]["record"]["label"], "alpha")

    def test_duplicate_id_across_sources_rejected(self):
        self.seed()
        res = self.store.apply_build("PA", [SourceBatch("PA|other.py", "s", [node("PA", "PA:a")])])
        self.assertFalse(res["ok"])


class AuthTests(Base):
    def test_forged_project_denied_and_isolation(self):
        self.seed()
        reader = AuthorizedReader(self.store, registry())
        a = registry().authenticate(TOKEN_A)
        ok = reader.call(a, "search", {"query": "alpha", "project_id": "PA"})
        self.assertEqual(ok["returned"], 1)
        self.assertTrue(all(r["record"]["project_id"] == "PA" for r in ok["results"]))
        self.assertEqual(reader.call(a, "search", {"query": "alpha", "project_id": "PB"})["status"], "PROJECT_ACCESS_DENIED")
        self.assertEqual(reader.call(a, "search", {"query": "alpha"})["project_id"], "PA")  # single grant default
        b = registry().authenticate(TOKEN_B)
        self.assertEqual(reader.call(b, "stats", {})["status"], "PROJECT_ID_REQUIRED")

    def test_bad_tokens(self):
        for t in (None, "", "short", "z" * 64):
            with self.assertRaises(AuthError):
                registry().authenticate(t)

    def test_empty_registry_fails_closed(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(AuthError):
                CallerAuthRegistry.from_env().authenticate(TOKEN_A)


class FakeFiles:
    def __init__(self, pages=None, exc=None):
        self.pages, self.exc, self.calls = pages or [], exc, 0

    def list(self, **kw):
        if self.exc:
            raise self.exc
        page = self.pages[min(self.calls, len(self.pages) - 1)]
        self.calls += 1
        return mock.Mock(execute=lambda: page)


class DriveTests(Base):
    def test_allowlist_and_errors(self):
        c = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles(exc=ConnectionError("503")))
        self.assertEqual(c.list_project("PA", "F2").status, "FOLDER_NOT_IN_ALLOWLIST")
        self.assertEqual(c.list_project("PB", "F1").status, "FOLDER_NOT_IN_ALLOWLIST")
        l = c.list_project("PA", "F1")
        self.assertFalse(l.listing_complete)
        self.assertEqual(l.status, "LISTING_ERROR:ConnectionError")

    def test_incomplete_search_and_loop_and_cap(self):
        c = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles([{"files": [], "incompleteSearch": True}]))
        self.assertEqual(c.list_project("PA", "F1").status, "DRIVE_INCOMPLETE_SEARCH")
        c = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles([{"files": [{"id": "1"}], "nextPageToken": "t"}]))
        self.assertEqual(c.list_project("PA", "F1").status, "PAGINATION_LOOP")
        pages = [{"files": [{"id": str(i)}], "nextPageToken": f"t{i}"} for i in range(5)]
        c = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles(pages), max_pages=3)
        self.assertEqual(c.list_project("PA", "F1").status, "PAGE_CAP_REACHED")

    def test_complete_listing_then_prune(self):
        self.seed()
        pages = [{"files": [{"id": "d1", "name": "a"}], "nextPageToken": "t"}, {"files": [{"id": "d2"}]}]
        l = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles(pages)).list_project("PA", "F1")
        self.assertTrue(l.listing_complete)
        self.assertEqual(l.source_keys, {"PA|drive:d1", "PA|drive:d2"})
        broken = ReadOnlyDriveConnector({"PA": {"F1"}}, FakeFiles(exc=TimeoutError())).list_project("PA", "F1")
        self.store.apply_build("PA", [], active_sources=broken.source_keys, listing_complete=broken.listing_complete)
        self.assertIn("PA:a", self.store.state["nodes"])


class McpTests(Base):
    def server(self, token=TOKEN_A):
        self.seed()
        reg = registry()
        try:
            principal = reg.authenticate(token)
        except AuthError:
            principal = None
        return McpServer(AuthorizedReader(self.store, reg), principal)

    @staticmethod
    def rpc(srv, method, params=None, mid=1):
        msg = {"jsonrpc": "2.0", "method": method}
        if mid is not None:
            msg["id"] = mid
        if params is not None:
            msg["params"] = params
        return srv.handle_line(json.dumps(msg))

    def init(self, srv):
        r = self.rpc(srv, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}})
        self.assertIsNone(self.rpc(srv, "notifications/initialized", mid=None))
        return r

    def test_lifecycle(self):
        srv = self.server()
        self.assertEqual(self.rpc(srv, "tools/list")["error"]["code"], -32002)
        self.assertEqual(self.rpc(srv, "ping")["result"], {})
        r = self.init(srv)
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        srv2 = self.server()
        r2 = self.rpc(srv2, "initialize", {"protocolVersion": "1999-01-01"})
        self.assertEqual(r2["result"]["protocolVersion"], "2025-06-18")

    def test_tools(self):
        srv = self.server()
        self.init(srv)
        tools = self.rpc(srv, "tools/list")["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"graph_search", "graph_node", "graph_stats"})
        self.assertTrue(all(t["annotations"]["readOnlyHint"] and t["inputSchema"]["type"] == "object" for t in tools))
        res = self.rpc(srv, "tools/call", {"name": "graph_search", "arguments": {"query": "alpha"}})["result"]
        self.assertFalse(res["isError"])
        self.assertEqual(res["content"][0]["type"], "text")
        self.assertEqual(json.loads(res["content"][0]["text"]), res["structuredContent"])
        self.assertEqual(res["structuredContent"]["returned"], 1)
        denied = self.rpc(srv, "tools/call", {"name": "graph_search", "arguments": {"query": "alpha", "project_id": "PB"}})["result"]
        self.assertTrue(denied["isError"])
        nd = self.rpc(srv, "tools/call", {"name": "graph_node", "arguments": {"node_id": "PA:a"}})["result"]["structuredContent"]
        self.assertEqual(nd["edge_total"], 1)

    def test_errors(self):
        srv = self.server()
        self.init(srv)
        self.assertEqual(srv.handle_line("{not json")["error"]["code"], -32700)
        self.assertEqual(srv.handle_line("[]")["error"]["code"], -32600)
        self.assertEqual(self.rpc(srv, "resources/list")["error"]["code"], -32601)
        self.assertEqual(self.rpc(srv, "tools/call", {"name": "graph_write", "arguments": {}})["error"]["code"], -32602)
        self.assertEqual(self.rpc(srv, "tools/call", {"name": "graph_search", "arguments": {}})["error"]["code"], -32602)
        self.assertEqual(self.rpc(srv, "tools/call", {"name": "graph_search", "arguments": {"query": "a", "x": 1}})["error"]["code"], -32602)
        self.assertIsNone(self.rpc(srv, "notifications/cancelled", {"requestId": 1}, mid=None))

    def test_unauthenticated_process(self):
        srv = self.server(token="wrong" * 10)
        self.init(srv)
        res = self.rpc(srv, "tools/call", {"name": "graph_stats", "arguments": {}})["result"]
        self.assertTrue(res["isError"])
        self.assertEqual(res["structuredContent"]["status"], "UNAUTHORIZED_CALLER")

    def test_stdio_serve(self):
        srv = self.server()
        lines = [json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}),
                 json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
                 json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})]
        out = io.StringIO()
        srv.serve(io.StringIO("\n".join(lines) + "\n"), out)
        replies = [json.loads(l) for l in out.getvalue().splitlines()]
        self.assertEqual([r["id"] for r in replies], [1, 2])


class ApiTests(Base):
    def test_http_auth(self):
        self.seed()
        reader = AuthorizedReader(self.store, registry())
        hdr = {"Authorization": f"Bearer {TOKEN_A}"}
        self.assertEqual(handle_request(reader, "GET", "/api/graph/stats?project_id=PA", {})[0], 401)
        self.assertEqual(handle_request(reader, "GET", "/api/graph/search?q=alpha&project_id=PB", hdr)[0], 403)
        code, body = handle_request(reader, "GET", "/api/graph/search?q=alpha&project_id=PA", hdr)
        self.assertEqual((code, body["returned"]), (200, 1))
        self.assertEqual(handle_request(reader, "POST", "/api/graph/search", hdr)[0], 405)
        self.assertEqual(handle_request(reader, "GET", "/api/graph/search?q=a&top_k=x", hdr)[0], 400)

    def test_refuse_public_bind(self):
        from astra_graphify.api import serve
        with self.assertRaises(SystemExit):
            serve(AuthorizedReader(self.store, registry()), host="0.0.0.0")


class AdapterTests(Base):
    def make_repo(self):
        repo = self.dir / "repo"
        (repo / "src").mkdir(parents=True)
        (repo / "src" / "a.py").write_text("import os\n\ndef run():\n    helper()\n\ndef helper():\n    pass\n", encoding="utf-8")
        (repo / "src" / "leak.py").write_text("KEY = 'ghp_" + "A" * 30 + "'\ndef leak():\n    pass\n", encoding="utf-8")
        (repo / "private").mkdir()
        (repo / "private" / "p.py").write_text("def p():\n    pass\n", encoding="utf-8")
        graph = {"nodes": [
            {"id": "src_a", "label": "a.py", "source_file": "src/a.py", "source_location": "L1"},
            {"id": "src_a_run", "label": "run()", "source_file": "src/a.py", "source_location": "L3"},
            {"id": "src_a_helper", "label": "helper()", "source_file": "src/a.py", "source_location": "L6"},
            {"id": "ref_os", "label": "os"},
            {"id": "src_leak", "label": "leak.py", "source_file": "src/leak.py", "source_location": "L1"},
            {"id": "priv_p", "label": "p()", "source_file": "private/p.py", "source_location": "L1"}],
            "edges": [
            {"source": "src_a", "target": "src_a_run", "relation": "contains", "confidence": "EXTRACTED", "source_file": "src/a.py", "source_location": "L3"},
            {"source": "src_a_run", "target": "src_a_helper", "relation": "calls", "confidence": "EXTRACTED", "source_file": "src/a.py", "source_location": "L4"},
            {"source": "src_a_run", "target": "src_a_helper", "relation": "uses", "confidence": "INFERRED", "source_file": "src/a.py", "source_location": "L4"},
            {"source": "src_a", "target": "ref_os", "relation": "imports", "confidence": "EXTRACTED", "source_file": "src/a.py", "source_location": "L1"},
            {"source": "src_a_run", "target": "src_leak", "relation": "calls", "confidence": "EXTRACTED", "source_file": "src/a.py", "source_location": "L4"},
            {"source": "src_a_run", "target": "priv_p", "relation": "calls", "confidence": "EXTRACTED", "source_file": "src/a.py", "source_location": "L4"}]}
        cfg = {"project_id": "PA", "include": ["src/*.py"], "exclude": ["private/*"]}
        return repo, graph, cfg

    def test_convert_and_ingest(self):
        repo, graph, cfg = self.make_repo()
        batches, rep = convert(graph, repo, cfg, "rev1", "o/r")
        self.assertEqual(rep["blocked_files"][0]["file"], "src/leak.py")
        self.assertEqual(rep["edges_dropped_endpoint"], 2)  # to blocked and to non-allowlisted node
        res = self.store.apply_build("PA", batches)
        self.assertTrue(res["ok"], res)
        nodes, edges = self.store.state["nodes"], self.store.state["edges"]
        self.assertEqual(nodes["PA:src_a"]["record"]["knowledge_layer"], "SOURCE")
        self.assertEqual(nodes["PA:src_a_run"]["record"]["knowledge_layer"], "VERIFIED")
        self.assertEqual(nodes["PA:ref_os"]["provenance"]["source_kind"], "EXTERNAL_REFERENCE")
        layers = {e["record"]["relation"]: e["record"]["knowledge_layer"] for e in edges.values()}
        self.assertEqual(layers["uses"], "INFERRED")
        self.assertEqual(layers["calls"], "VERIFIED")
        self.assertNotIn("PA:priv_p", nodes)
        self.assertTrue(all("ghp_" not in json.dumps(e) for e in nodes.values()))
        # second identical build is incremental: nothing rewritten
        batches2, _ = convert(graph, repo, cfg, "rev2", "o/r")
        self.assertEqual(self.store.apply_build("PA", batches2)["status"], "NO_CHANGE")

    def test_wrong_line_not_verified(self):
        repo, graph, cfg = self.make_repo()
        graph["nodes"][1]["source_location"] = "L7"
        batches, _ = convert(graph, repo, cfg, "rev1", "o/r")
        self.store.apply_build("PA", batches)
        self.assertEqual(self.store.state["nodes"]["PA:src_a_run"]["record"]["knowledge_layer"], "EXTRACTED")

    def test_path_traversal_refused(self):
        from astra_graphify.graphify_adapter import path_allowed
        cfg = {"include": ["*"], "exclude": []}
        self.assertFalse(path_allowed("../etc/passwd", cfg))
        self.assertFalse(path_allowed("/etc/passwd", cfg))


if __name__ == "__main__":
    unittest.main()
