"""Secrets/PII guard and authenticated caller registry.

The caller's identity is established ONLY from a secret token whose SHA-256
digest is registered server-side. A project_id supplied by the caller is a
request, never a grant: it is checked against the identity's allowed set.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional

MIN_TOKEN_LEN = 32

SENSITIVE_PATTERNS = [
    ("GITHUB_PAT", re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("OPENAI_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("GOOGLE_API_KEY", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
    # character classes accept text with or without Vietnamese diacritics
    ("BHXH_ID_NUMBER", re.compile(r"(?i)(?:s[oố]\s*s[oổ]\s*bhxh|m[aã]\s*s[oố]\s*bhxh|cccd|cmnd)\s*[:\-]?\s*\d{9,12}")),
    ("BHXH_DENY_KEYWORD", re.compile(
        r"(?i)(?:danh\s+s[aá]ch\s+chi\s+tr[aả]\s+l[uư][oơ]ng\s+h[uư]u"
        r"|bi[eê]n\s+b[aả]n\s+x[uử]\s+ph[aạ]t\s+h[aà]nh\s+ch[ií]nh"
        r"|h[oồ]\s+s[oơ]\s+gi[aả]i\s+quy[eế]t\s+ch[eế]\s+[dđ][oộ])")),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_str(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_sensitive(text: str) -> List[str]:
    return [label for label, pat in SENSITIVE_PATTERNS if pat.search(text or "")]


@dataclass(frozen=True)
class Principal:
    caller_id: str
    allowed_projects: FrozenSet[str]


class AuthError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class CallerAuthRegistry:
    """{caller_id: {"token_sha256": "<64 hex>", "allowed_projects": [...]}}"""

    def __init__(self, principals: Dict[str, Dict]):
        self._principals: Dict[str, tuple] = {}
        for caller_id, meta in principals.items():
            digest = str(meta.get("token_sha256", "")).lower()
            if not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise ValueError(f"INVALID_TOKEN_DIGEST:{caller_id}")
            projects = frozenset(meta.get("allowed_projects", []))
            self._principals[caller_id] = (digest, projects)

    @classmethod
    def from_env(cls, var: str = "ASTRA_GRAPHIFY_PRINCIPALS") -> "CallerAuthRegistry":
        """Value is JSON, or a path to a JSON file kept OUTSIDE the repository."""
        raw = os.environ.get(var, "").strip()
        if not raw:
            return cls({})  # fail-closed: nobody is authorized
        if raw.startswith("{"):
            return cls(json.loads(raw))
        return cls(json.loads(Path(raw).read_text(encoding="utf-8")))

    def authenticate(self, raw_token: Optional[str]) -> Principal:
        if not raw_token or len(raw_token) < MIN_TOKEN_LEN:
            raise AuthError("UNAUTHORIZED_CALLER")
        digest = sha256_str(raw_token)
        match = None
        for caller_id, (expected, projects) in self._principals.items():
            # compare against every entry: no early exit timing signal
            if hmac.compare_digest(digest, expected):
                match = Principal(caller_id, projects)
        if match is None:
            raise AuthError("UNAUTHORIZED_CALLER")
        return match

    @staticmethod
    def authorize(principal: Principal, requested_project_id: Optional[str]) -> str:
        if not requested_project_id:
            if len(principal.allowed_projects) == 1:
                return next(iter(principal.allowed_projects))
            raise AuthError("PROJECT_ID_REQUIRED")
        if requested_project_id not in principal.allowed_projects:
            raise AuthError("PROJECT_ACCESS_DENIED")
        return requested_project_id
