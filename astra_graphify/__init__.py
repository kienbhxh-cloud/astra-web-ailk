"""ASTRA GRAPHIFY AI — integrated release.

Merges: ChatGPT provenance v1.2 schema (official contract), Gemini v1.1/v1.2
engine design (caller auth, dual schema, read-only Drive, listing guard), and
the upstream Graphify AST extractor audited by Grok (graphifyy==0.9.119).

Public repository rule: only code and public fixtures live here. Graphs built
from private Drive documents must be written outside the repository.
"""

VERSION = "1.3.0"
PROTOCOL_VERSION = "2025-06-18"  # MCP specification revision implemented by mcp_server
