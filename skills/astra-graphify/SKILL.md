---
name: astra-graphify
description: Use the ASTRA Graphify knowledge graph (code graph + provenance v1.2) for evidence-backed context retrieval in ASTRA projects.
---
# ASTRA Graphify

Implementation: `astra_graphify/` (v1.3.0, see `astra_graphify/README.md`). Upstream extractor: https://github.com/Graphify-Labs/graphify, PyPI `graphifyy==0.9.119`, Apache-2.0, pinned in `astra_graphify/requirements-graphify.lock`. Only `graphify extract --code-only` (AST, 0 LLM calls) is used.

Query order: (1) WEB AI-LK page `docs/graphify.html` or `docs/graph/astra-web-ailk.public.json`; (2) read-only MCP `python -m astra_graphify mcp` when a token is provisioned; (3) ordinary source navigation if the graph is missing or its `source_revision` is older than the code you are reading.

Trust rules: every node/edge carries provenance v1.2 and a knowledge layer. SOURCE = raw file with sha256. EXTRACTED = AST output, not cross-checked. INFERRED = guess, never a fact. VERIFIED = mechanically checked (file hash + symbol present at the cited line), execution ACTUAL. Before relying on a claim, open `source_url` at the pinned revision.

Data rules: this repository is public. Graph only git-tracked code listed in `astra_graphify/sources.public.json`. Never graph credentials, Drive documents, BHXH data, mailbox letters or home directories into the repo; private graphs use a `--data` directory outside the repository and must not be exported. Do not claim MCP is connected without a real client session. Do not claim token savings: status is NOT_MEASURED until a tokenizer-based A/B run exists.

Operations: CI `astra-graphify-validation.yml` (tests) and `astra-graphify-build.yml` (incremental build via AST cache + sha256 skip, transactional ingest, prune only on complete listing, artifact evidence, main-only publish). Rollback: `python -m astra_graphify rollback --data <store>`; code: revert the integration commit. Issue #3.
