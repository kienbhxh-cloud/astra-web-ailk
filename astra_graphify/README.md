# ASTRA GRAPHIFY AI — bản hợp nhất 1.3.0

Kiến trúc: **DRIVE FIRST – GITHUB COMPUTE – MULTI-AI KNOWLEDGE**. Hợp nhất:

| Nguồn | Phần được tiếp nhận |
|---|---|
| ChatGPT | `skills/astra-graphify/provenance-v1.2.schema.json` (chuẩn chính thức, giữ nguyên) |
| Gemini v1.1/v1.2 | thiết kế `CallerAuthRegistry`, schema kép, Drive read-only theo allowlist, chặn prune khi listing dở dang |
| Grok | xác minh upstream `graphifyy==0.9.119` (Apache-2.0), chỉ dùng đường AST `--code-only` |

## Cấu trúc

```
astra_graphify/
  security.py          chặn bí mật/BHXH, xác thực token -> danh tính -> dự án
  validator.py         schema kép fail-closed + lớp tri thức SOURCE/EXTRACTED/INFERRED/VERIFIED
  engine.py            kho giao dịch: stage -> kiểm tra hết -> ghi nguyên tử, snapshot, rollback, journal
  graphify_adapter.py  graph.json của Graphify -> envelope provenance v1.2 + kiểm chứng máy (hash + dòng)
  drive_connector.py   liệt kê Drive chỉ đọc, listing_complete chỉ True khi chứng minh được đủ
  mcp_server.py        MCP stdio theo đặc tả 2025-06-18 (initialize, tools/list, tools/call…)
  api.py               HTTP loopback chỉ đọc, Bearer token
  cli.py               build / stats / rollback / export-public / mcp / serve
  sources.public.json  allowlist cho đồ thị công khai của repo này
  requirements.lock, requirements-graphify.lock   khóa phiên bản chính xác
  tests/               33 ca hồi quy, dùng schema chính thức
```

## Chạy

```bash
pip install -r astra_graphify/requirements.lock
python -m unittest discover -s astra_graphify/tests -t . -v

python -m venv /tmp/gvenv && /tmp/gvenv/bin/pip install -r astra_graphify/requirements-graphify.lock
GRAPHIFY_QUERY_LOG_DISABLE=1 /tmp/gvenv/bin/graphify extract . --code-only --no-cluster
python -m astra_graphify build --graph graphify-out/graph.json \
  --allowlist astra_graphify/sources.public.json --data .astra-graphify-store --prune
python -m astra_graphify export-public --data .astra-graphify-store \
  --allowlist astra_graphify/sources.public.json --out docs/graph/astra-web-ailk.public.json
```

MCP (chỉ đọc), cấu hình ngoài repo:

```bash
export ASTRA_GRAPHIFY_PRINCIPALS=/duong/dan/ngoai/repo/principals.json   # {"claude":{"token_sha256":"<64hex>","allowed_projects":["ASTRA_WEB_AILK_PUBLIC"]}}
export ASTRA_GRAPHIFY_TOKEN=...   # token thật, >= 32 ký tự, không commit
python -m astra_graphify mcp --data .astra-graphify-store
```

## Khôi phục

* Dữ liệu: `python -m astra_graphify rollback --data <store>` trả về snapshot trước (giữ 10 bản).
* Mã: bản trước 1.3.0 là commit `0a3a6a8` (chỉ có skill + schema). `git revert <commit>` gỡ toàn bộ gói.
* Đồ thị web: `docs/graph/astra-web-ailk.public.json` là tệp có phiên bản trong git.

## Quy tắc dữ liệu

Repo này công khai. Chỉ đưa lên đồ thị **mã nguồn đã theo dõi trong git** theo allowlist. Đồ thị dựng từ
tài liệu Drive/BHXH/thư nội bộ phải ghi vào thư mục ngoài repo (`--data` riêng tư) và **không** chạy
`export-public` (lệnh này từ chối allowlist không có `"public": true`). Không gửi tài liệu qua lượt mô hình của Graphify.

## Trạng thái (25/11/2026)

| Hạng mục | Nhãn |
|---|---|
| Unit test 33 ca (Python 3.13 cục bộ, jsonschema 4.23.0 + rfc3339-validator) | ACTUAL PASS |
| Graphify 0.9.119 `extract --code-only` trên repo này, nhập vào kho, xuất đồ thị web | ACTUAL PASS (cục bộ) |
| Workflow `astra-graphify-build.yml` / `astra-graphify-validation.yml` trên GitHub | xem báo cáo, chạy khi push |
| MCP stdio với client MCP thật (Claude Code/Gemini CLI) | NOT_TESTED |
| Drive connector với Drive API thật | MOCK PASS (client giả lập) — chưa có service account |
| Đồ thị tri thức tài liệu Drive riêng tư | DESIGN — chờ quyết định nơi lưu riêng tư |
| MCP thường trực trên cloud | DESIGN — chưa phát sinh chi phí |
| Tiết kiệm token | NOT_MEASURED |
