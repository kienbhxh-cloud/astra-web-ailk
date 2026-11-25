"""Validation against the OFFICIAL schemas (fail closed, no minimal schema)."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROVENANCE_SCHEMA = REPO_ROOT / "skills" / "astra-graphify" / "provenance-v1.2.schema.json"
GRAPH_SCHEMA = Path(__file__).resolve().parent / "schemas" / "astra-graph-v1.schema.json"


class SchemaUnavailable(RuntimeError):
    """Raised when a schema or the validator library is missing: callers must refuse to write."""


@lru_cache(maxsize=None)
def _validator(schema_path: str):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:  # fail closed
        raise SchemaUnavailable("JSONSCHEMA_LIB_MISSING_FAIL_CLOSED") from exc
    checker = FormatChecker()
    if checker.conforms("not-a-date", "date-time"):
        # jsonschema silently skips date-time without rfc3339-validator: refuse instead
        raise SchemaUnavailable("DATE_TIME_FORMAT_CHECKER_MISSING_FAIL_CLOSED")
    p = Path(schema_path)
    if not p.is_file():
        raise SchemaUnavailable(f"SCHEMA_REQUIRED_FAIL_CLOSED:{p.name}")
    schema = json.loads(p.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=checker)


def _errors(schema_path: Path, instance) -> list[str]:
    v = _validator(str(schema_path))
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in sorted(v.iter_errors(instance), key=lambda e: list(map(str, e.absolute_path)))]


def provenance_errors(record: dict, schema_path: Path = PROVENANCE_SCHEMA) -> list[str]:
    return _errors(schema_path, record)


def graph_errors(graph: dict, schema_path: Path = GRAPH_SCHEMA) -> list[str]:
    return _errors(schema_path, graph)
