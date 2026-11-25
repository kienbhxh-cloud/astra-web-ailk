import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        schema = json.loads(Path("skills/astra-graphify/provenance-v1.2.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        self.validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.record = dict(id="fixture-1", project_id="PUBLIC_FIXTURE", source_url="https://example.org/source", source_revision="fixture", updated_at_utc="2026-11-25T00:00:00Z", source_kind="FILE", sha256="a"*64, locator="L1", evidence_kind="EXTRACTED", verification_status="VERIFIED", execution_status="MOCK")
    def test_valid(self):
        self.assertTrue(self.validator.is_valid(self.record))
    def test_missing_hash(self):
        self.assertFalse(self.validator.is_valid(dict(self.record, sha256=None)))
    def test_inferred_verified(self):
        self.assertFalse(self.validator.is_valid(dict(self.record, evidence_kind="INFERRED")))
    def test_external(self):
        self.assertTrue(self.validator.is_valid(dict(self.record, source_kind="EXTERNAL_REFERENCE", sha256=None, verification_status="UNVERIFIED")))
    def test_external_verified(self):
        self.assertFalse(self.validator.is_valid(dict(self.record, source_kind="EXTERNAL_REFERENCE", sha256=None)))
    def test_invalid_date(self):
        self.assertFalse(self.validator.is_valid(dict(self.record, updated_at_utc="invalid")))
    def test_invalid_relation(self):
        self.assertFalse(self.validator.is_valid(dict(self.record, relation={"from":"a"})))
if __name__ == "__main__":
    unittest.main()
