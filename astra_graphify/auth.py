"""Caller identity and per-project authorization.

project_id from a caller is only a *request*; access is granted solely from the
authenticated principal's allowlist. Tokens are stored as SHA-256 hashes only.
Principals file (kept on Drive / in a secret, never in the repo):
{"principals": [{"name": "chatgpt", "token_sha256": "<hex>", "projects": ["ASTRA_WEB_PUBLIC"]}]}
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from pathlib import Path


class AuthError(PermissionError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Principal:
    name: str
    projects: frozenset[str]


class Authenticator:
    def __init__(self, principals: list[dict]):
        self._entries = []
        for p in principals:
            h = str(p.get("token_sha256", "")).lower()
            if len(h) != 64 or not p.get("name") or not p.get("projects"):
                raise ValueError(f"INVALID_PRINCIPAL_ENTRY:{p.get('name')}")
            self._entries.append((h, Principal(p["name"], frozenset(p["projects"]))))

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> "Authenticator":
        path = path or os.environ.get("ASTRA_GRAPHIFY_PRINCIPALS")
        if not path or not Path(path).is_file():
            raise AuthError("AUTH_CONFIG_MISSING_FAIL_CLOSED")
        return cls(json.loads(Path(path).read_text(encoding="utf-8")).get("principals", []))

    def authenticate(self, token: str | None) -> Principal:
        if not token:
            raise AuthError("UNAUTHENTICATED")
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        match = None
        for h, principal in self._entries:  # compare all entries: constant work per call
            if hmac.compare_digest(h, digest):
                match = principal
        if match is None:
            raise AuthError("UNAUTHENTICATED")
        return match


def authorize(principal: Principal, requested_project: str | None) -> str:
    """Return the project the principal may read. Never trusts the request alone."""
    if not requested_project:
        if len(principal.projects) == 1:
            return next(iter(principal.projects))
        raise AuthError("PROJECT_ID_REQUIRED")
    if requested_project not in principal.projects:
        raise AuthError("FORBIDDEN_PROJECT")
    return requested_project
