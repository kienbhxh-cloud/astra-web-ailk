"""Hashing, sensitive-content scan and source path policy (fail closed)."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath

SENSITIVE_PATTERNS = [
    ("GITHUB_PAT", re.compile(r"(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("OPENAI_KEY", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{20,}")),
    ("ANTHROPIC_KEY", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
    ("BEARER_LITERAL", re.compile(r"(?i)authorization:\s*bearer\s+[A-Za-z0-9._\-]{24,}")),
    ("BHXH_DENY_KEYWORD", re.compile(
        r"(?i)(danh sách chi trả lương hưu|biên bản xử phạt hành chính|hồ sơ giải quyết chế độ"
        r"|mã số bhxh\s*[:=]\s*\d{10}|số cccd\s*[:=]\s*\d{12})")),
]

# Paths never ingested, whatever the allowlist says.
DENY_PARTS = {".git", ".env", "node_modules", "graphify-out", "__pycache__", ".venv", "venv"}
DENY_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".env", ".sqlite", ".db"}
DENY_NAME_RE = re.compile(r"(?i)(secret|credential|token|password|\.env)")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_sensitive_content(text: str) -> list[str]:
    return [label for label, pat in SENSITIVE_PATTERNS if pat.search(text or "")]


def path_allowed(rel_path: str, allow_prefixes: list[str]) -> bool:
    """A relative POSIX path is allowed only if under an allowed prefix and not denied."""
    p = PurePosixPath(rel_path)
    if p.is_absolute() or ".." in p.parts:
        return False
    if any(part in DENY_PARTS for part in p.parts):
        return False
    if p.suffix.lower() in DENY_SUFFIXES or DENY_NAME_RE.search(p.name):
        return False
    s = p.as_posix()
    return any(s == pre.rstrip("/") or s.startswith(pre.rstrip("/") + "/") for pre in allow_prefixes)
