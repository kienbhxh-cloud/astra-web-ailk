"""Regression tests for astra_graphify v1.3 — run: python -m unittest discover -s astra_graphify/tests -v
Uses the OFFICIAL provenance-v1.2 schema from skills/astra-graphify (no minimal schema).
All data is synthetic; no network, no LLM."""
import copy
import hashlib
import json
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from astra_graphify import provenance
from astra_graphify.api import make_handler, serve
from astra_graphify.auth import AuthError, Authenticator, authorize
from astra_graphify.convert import IntegrityError, check_integrity, convert
from astra_graphify.mcp_server import McpServer
from astra_graphify.query import search
from astra_graphify.security import path_allowed
from astra_graphify.store import GraphStore, PruneRefused

P = "FIXTURE_A"
TOKEN_A, TOKEN_B = "token-alpha-fixture", "token-beta-fixture"


def gfy_graph():
    return {
        "nodes": [
            {"id": "a", "label": "a.py", "file_type": "code", "source_file": "src/a.py", "source_location": "L1"},
            {"id": "a_fn", "label": "run()", "file_type": "code", "source_file": "src/a.py", "source_location": "L3"},
            {"id": "b", "label": "b.js", "file_type": "code", "source_file": "src/b.js", "source_location": "L1"},
            {"id": "ref_os", "label": "ref_os", "file_type": "concept", "external": True, "source_file": ""},
        ],
        "links": [
            {"source": "a", "target": "a_fn", "relation": "contains", "confidence": "EXTRACTED",
             "source_file": "src/a.py", "source_location": "L3"},
            {"source": "a", "target": "ref_os", "relation": "imports", "confidence": "EXTRACTED",
             "source_file": "src/a.py", "source_location": "L1"},
            {"source": "a_fn", "target": "b", "relation": "calls", "confidence": "INFERRED",
             "source_file": "src/a.py", "source_location": "L4"},
            {"source": "a", "target": "ghost", "relation": "calls", "confidence": "EXTRACTED",
             "source_file": "src/a.py", "source_location": "L9"},
        ],
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "src").mkdir()
        (self.tmp / "src" / "a.py").write_text("import os\n\ndef run():\n    b()\n", encoding="utf-8")
        (self.tmp / "src" / "b.js").write_text("function b() {}\n", encoding="utf-8")
        self.store = GraphStore(self.tmp / "data")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, project=P, g=None):
        return convert(g or gfy_graph(), project_id=project, src_root=self.tmp, source_revision="fixture-rev",
                       source_url_base="https://example.org/blob/fixture-rev/", allow_prefixes=["src"],
                       built_at_utc="2026-11-25T00:00:00Z")


class TestSchemaFailClosed(Base):
    def test_missing_official_schema_refuses(self):
        with self.assertRaises(provenance.SchemaUnavailable):
            provenance.provenance_errors({}, self.tmp / "missing.schema.json")

    def test_invalid_datetime_rejected(self):
        g = Base.build(self)["graph"]
        bad = dict(g["provenance"][0], updated_at_utc="not-a-date")
        self.assertTrue(provenance.provenance_errors(bad))

    def test_uses_official_v12_schema(self):
        self.assertTrue(provenance.PROVENANCE_SCHEMA.name == "provenance-v1.2.schema.json")
        self.assertTrue(provenance.PROVENANCE_SCHEMA.is_file())


class TestConvert(Base):
    def test_status_separation(self):
        g = self.build()["graph"]
        prov = {r["id"]: r for r in g["provenance"]}
        for n in g["nodes"]:
            r = prov[n["provenance_id"]]
            if n["source_path"]:
                self.assertEqual((r["source_kind"], r["verification_status"]), ("FILE", "VERIFIED"))
                self.assertEqual(r["sha256"], hashlib.sha256((self.tmp / n["source_path"]).read_bytes()).hexdigest())
            else:
                self.assertEqual((r["source_kind"], r["sha256"], r["verification_status"]),
                                 ("EXTERNAL_REFERENCE", None, "UNVERIFIED"))
        inferred = [prov[e["provenance_id"]] for e in g["edges"] if e["type"] == "calls"]
        self.assertTrue(inferred and all(r["evidence_kind"] == "INFERRED" and r["verification_status"] == "UNVERIFIED"
                                         for r in inferred))
        for r in g["provenance"]:
            self.assertEqual(provenance.provenance_errors(r), [])

    def test_dangling_edge_dropped(self):
        res = self.build()
        self.assertEqual(res["report"]["dropped_edges"], 1)
        self.assertFalse(any("ghost" in e["to"] for e in res["graph"]["edges"]))

    def test_integrity_rejects_dangling_both_ends(self):
        g = self.build()["graph"]
        for end in ("from", "to"):
            bad = copy.deepcopy(g)
            bad["edges"][0][end] = f"{P}::nope"
            with self.assertRaisesRegex(IntegrityError, f"DANGLING_{end.upper()}"):
                check_integrity(bad)

    def test_integrity_rejects_cross_project(self):
        g = self.build()["graph"]
        bad = copy.deepcopy(g)
        bad["nodes"][0]["project_id"] = "OTHER"
        with self.assertRaisesRegex(IntegrityError, "CROSS_PROJECT"):
            check_integrity(bad)
        bad = copy.deepcopy(g)
        bad["provenance"][0]["project_id"] = "OTHER"
        with self.assertRaisesRegex(IntegrityError, "CROSS_PROJECT"):
            check_integrity(bad)

    def test_inferred_cannot_be_verified(self):
        g = self.build()["graph"]
        bad = copy.deepcopy(g)
        r = next(r for r in bad["provenance"] if r["evidence_kind"] == "INFERRED")
        r["verification_status"] = "VERIFIED"
        with self.assertRaises(IntegrityError):
            check_integrity(bad)

    def test_sensitive_source_blocked(self):
        (self.tmp / "src" / "b.js").write_text("const t='ghp_" + "A" * 30 + "';\n", encoding="utf-8")
        res = self.build()
        self.assertIn("src/b.js", res["report"]["blocked_sources"])
        self.assertNotIn("src/b.js", [s["path"] for s in res["graph"]["sources"]])
        self.assertFalse(any(n["source_path"] == "src/b.js" for n in res["graph"]["nodes"]))

    def test_path_policy(self):
        self.assertTrue(path_allowed("src/a.py", ["src"]))
        for bad in ("src/../etc/passwd", "/src/a.py", "src/.env", "src/secret_keys.py", "other/a.py",
                    "src/node_modules/x.js", "srcx/a.py"):
            self.assertFalse(path_allowed(bad, ["src"]), bad)


class TestStore(Base):
    def test_validate_before_write_and_rollback(self):
        g1 = self.build()["graph"]
        self.store.commit(g1)
        bad = copy.deepcopy(g1)
        bad["edges"][0]["to"] = f"{P}::missing"
        with self.assertRaises(IntegrityError):
            self.store.commit(bad)
        self.assertEqual(self.store.load(P), json.loads(json.dumps(g1, sort_keys=True)))  # untouched
        g2 = copy.deepcopy(g1)
        g2["source_revision"] = "rev-2"
        self.store.commit(g2)
        self.assertEqual(self.store.load(P)["source_revision"], "rev-2")
        self.assertTrue(self.store.rollback(P)["ok"])
        self.assertEqual(self.store.load(P)["source_revision"], "fixture-rev")

    def test_tampered_snapshot_rejected_on_load(self):
        self.store.commit(self.build()["graph"])
        p = self.tmp / "data" / f"{P}.graph.json"
        g = json.loads(p.read_text())
        g["provenance"][0]["sha256"] = "zz"
        p.write_text(json.dumps(g))
        with self.assertRaises(IntegrityError):
            self.store.load(P)

    def test_prune_guards(self):
        self.store.commit(self.build()["graph"])
        with self.assertRaisesRegex(PruneRefused, "LISTING_INCOMPLETE"):
            self.store.prune_sources(P, set(), listing_complete=False)
        with self.assertRaisesRegex(PruneRefused, "MASS_DELETE"):
            self.store.prune_sources(P, set(), listing_complete=True)
        res = self.store.prune_sources(P, {"src/a.py"}, listing_complete=True, max_delete_ratio=0.5)
        self.assertEqual(res["removed_sources"], 1)
        g = self.store.load(P)
        self.assertFalse(any(n["source_path"] == "src/b.js" for n in g["nodes"]))
        check_integrity(g)

    def test_fingerprint_stable(self):
        g = self.build()["graph"]
        self.assertEqual(GraphStore.fingerprint(g), GraphStore.fingerprint(copy.deepcopy(g)))

    def test_invalid_project_id_path(self):
        with self.assertRaises(ValueError):
            self.store.load("../etc")


def principals_file(tmp: Path) -> Path:
    p = tmp / "principals.json"
    p.write_text(json.dumps({"principals": [
        {"name": "alpha", "token_sha256": hashlib.sha256(TOKEN_A.encode()).hexdigest(), "projects": [P]},
        {"name": "beta", "token_sha256": hashlib.sha256(TOKEN_B.encode()).hexdigest(), "projects": ["FIXTURE_B", "FIXTURE_C"]},
    ]}))
    return p


class TestAuth(Base):
    def test_identity_not_self_declared(self):
        auth = Authenticator.from_file(principals_file(self.tmp))
        with self.assertRaises(AuthError):
            auth.authenticate("wrong")
        with self.assertRaises(AuthError):
            auth.authenticate(None)
        beta = auth.authenticate(TOKEN_B)
        with self.assertRaisesRegex(AuthError, "FORBIDDEN_PROJECT"):
            authorize(beta, P)  # asking for another project is refused
        with self.assertRaisesRegex(AuthError, "PROJECT_ID_REQUIRED"):
            authorize(beta, None)
        self.assertEqual(authorize(auth.authenticate(TOKEN_A), None), P)

    def test_missing_config_fail_closed(self):
        with self.assertRaisesRegex(AuthError, "AUTH_CONFIG_MISSING"):
            Authenticator.from_file(self.tmp / "none.json")


class TestQuery(Base):
    def test_search_has_provenance_and_char_count(self):
        res = search(self.build()["graph"], "run")
        self.assertTrue(res["ok"] and res["returned"] >= 1)
        self.assertIsNone(res["token_count"])
        self.assertGreater(res["context_chars"], 0)
        self.assertIn("sha256", res["results"][0]["provenance"])


class TestMcp(Base):
    def setUp(self):
        super().setUp()
        self.store.commit(self.build()["graph"])
        auth = Authenticator.from_file(principals_file(self.tmp))
        self.srv = McpServer(self.store, auth.authenticate(TOKEN_A))

    def rpc(self, obj):
        return self.srv.handle_line(json.dumps(obj) if not isinstance(obj, str) else obj)

    def test_lifecycle(self):
        r = self.rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                      "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", r["result"]["capabilities"])
        r = self.rpc({"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "1999-01-01"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIsNone(self.rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        self.assertEqual(self.rpc({"jsonrpc": "2.0", "id": 3, "method": "ping"})["result"], {})

    def test_errors(self):
        self.assertEqual(self.rpc("{bad json")["error"]["code"], -32700)
        self.assertEqual(self.rpc([{"jsonrpc": "2.0", "id": 1, "method": "ping"}])["error"]["code"], -32600)
        self.assertEqual(self.rpc({"jsonrpc": "2.0", "id": 1, "method": "resources/write"})["error"]["code"], -32601)
        self.assertEqual(self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                   "params": {"name": "graph_delete", "arguments": {}}})["error"]["code"], -32602)
        self.assertEqual(self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                   "params": {"name": "graph_search", "arguments": {}}})["error"]["code"], -32602)

    def test_tools(self):
        tools = self.rpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["result"]["tools"]
        self.assertTrue(all("inputSchema" in t and t["annotations"]["readOnlyHint"] for t in tools))
        ok = self.rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                       "params": {"name": "graph_search", "arguments": {"query": "run"}}})["result"]
        self.assertFalse(ok["isError"])
        self.assertEqual(ok["content"][0]["type"], "text")
        self.assertTrue(ok["structuredContent"]["ok"])
        denied = self.rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                           "params": {"name": "graph_stats", "arguments": {"project_id": "FIXTURE_B"}}})["result"]
        self.assertTrue(denied["isError"])
        self.assertEqual(denied["structuredContent"]["error"], "FORBIDDEN_PROJECT")

    def test_unauthenticated_server_refuses_calls(self):
        srv = McpServer(self.store, None)
        r = srv.handle_line(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                        "params": {"name": "graph_stats", "arguments": {}}}))
        self.assertTrue(r["result"]["isError"])


class TestApi(Base):
    def setUp(self):
        super().setUp()
        self.store.commit(self.build()["graph"])
        from http.server import ThreadingHTTPServer
        auth = Authenticator.from_file(principals_file(self.tmp))
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store, auth))
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        super().tearDown()

    def get(self, path, token=None, method="GET"):
        req = urllib.request.Request(self.base + path, method=method)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_auth_and_readonly(self):
        self.assertEqual(self.get("/api/graph/stats")[0], 401)
        self.assertEqual(self.get("/api/graph/stats", TOKEN_B)[0], 400)  # beta has 2 projects, none chosen
        self.assertEqual(self.get(f"/api/graph/stats?project_id={P}", TOKEN_B)[0], 403)
        code, body = self.get("/api/graph/query?q=run", TOKEN_A)
        self.assertEqual(code, 200)
        self.assertTrue(body["ok"])
        self.assertEqual(self.get("/api/graph/stats", TOKEN_A, "POST")[0], 405)

    def test_non_loopback_refused(self):
        with self.assertRaises(SystemExit):
            serve(host="0.0.0.0", port=0)


if __name__ == "__main__":
    unittest.main()
