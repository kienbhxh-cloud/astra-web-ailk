"""Dual-schema, fail-closed validation.

* record      -> astra_graphify/schemas/record-v1.3.schema.json
* provenance  -> skills/astra-graphify/provenance-v1.2.schema.json (official, ChatGPT)

Fail-closed rules: a missing schema file, a missing jsonschema library, or a
jsonschema build that cannot check ``format: date-time`` (needs
rfc3339-validator) rejects every envelope instead of silently passing.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
RECORD_SCHEMA = Path(__file__).resolve().parent / "schemas" / "record-v1.3.schema.json"
PROVENANCE_SCHEMA = ROOT / "skills" / "astra-graphify" / "provenance-v1.2.schema.json"


class ValidationUnavailable(Exception):
    pass


@lru_cache(maxsize=8)
def _validator(schema_path: str):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:  # pragma: no cover - exercised via monkeypatch
        raise ValidationUnavailable("JSONSCHEMA_LIB_MISSING_FAIL_CLOSED") from exc
    path = Path(schema_path)
    if not path.is_file():
        raise ValidationUnavailable(f"SCHEMA_MISSING_FAIL_CLOSED:{path.name}")
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    checker = FormatChecker()
    if "date-time" not in checker.checkers:
        raise ValidationUnavailable("DATE_TIME_FORMAT_CHECKER_MISSING_FAIL_CLOSED:install rfc3339-validator")
    return Draft202012Validator(schema, format_checker=checker)


def derive_layer(record: Dict[str, Any], prov: Dict[str, Any]) -> str:
    """Deterministic knowledge layer: source data / extracted / inferred / verified."""
    if prov.get("verification_status") == "REJECTED":
        return "REJECTED"
    if record.get("kind") == "node" and record.get("node_type") == "FILE":
        return "SOURCE"  # raw source data; VERIFIED here means its hash was re-checked
    if prov.get("evidence_kind") == "INFERRED":
        return "INFERRED"
    if prov.get("verification_status") == "VERIFIED":
        return "VERIFIED"
    return "EXTRACTED"


def validate_envelope(
    envelope: Dict[str, Any],
    record_schema: Optional[Path] = RECORD_SCHEMA,
    provenance_schema: Optional[Path] = PROVENANCE_SCHEMA,
) -> Tuple[bool, List[str]]:
    if not isinstance(envelope, dict):
        return False, ["INVALID_ENVELOPE_STRUCTURE"]
    record, prov = envelope.get("record"), envelope.get("provenance")
    if not isinstance(record, dict) or not isinstance(prov, dict):
        return False, ["INVALID_ENVELOPE_STRUCTURE"]
    if set(envelope) - {"record", "provenance"}:
        return False, ["UNEXPECTED_ENVELOPE_KEYS"]
    if record_schema is None or provenance_schema is None:
        return False, ["SCHEMA_REQUIRED_FAIL_CLOSED"]
    try:
        rv = _validator(str(record_schema))
        pv = _validator(str(provenance_schema))
    except ValidationUnavailable as exc:
        return False, [str(exc)]

    errors: List[str] = []
    errors += [f"RECORD_SCHEMA:{e.json_path}:{e.message}" for e in rv.iter_errors(record)]
    errors += [f"PROVENANCE_SCHEMA:{e.json_path}:{e.message}" for e in pv.iter_errors(prov)]
    if errors:
        return False, errors

    if prov["id"] != record["id"]:
        errors.append("ID_MISMATCH_RECORD_PROVENANCE")
    if prov["project_id"] != record["project_id"]:
        errors.append("PROJECT_ID_MISMATCH_RECORD_PROVENANCE")
    expected_layer = derive_layer(record, prov)
    if record["knowledge_layer"] != expected_layer:
        errors.append(f"KNOWLEDGE_LAYER_MISMATCH:{record['knowledge_layer']}!={expected_layer}")
    if prov["verification_status"] == "VERIFIED" and prov["execution_status"] != "ACTUAL":
        errors.append("VERIFIED_REQUIRES_ACTUAL_EXECUTION")
    if record["kind"] == "edge":
        rel = prov.get("relation")
        want = {"from": record["source"], "to": record["target"], "type": record["relation"]}
        if rel != want:
            errors.append("EDGE_PROVENANCE_RELATION_MISMATCH")
    elif "relation" in prov:
        errors.append("NODE_MUST_NOT_CARRY_RELATION")
    return not errors, errors
