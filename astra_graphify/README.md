# ASTRA GRAPHIFY AI v1.3 — hợp nhất (Claude, Chief Implementation Engineer)

Căn cứ: ASTRA-GRAPHIFY-KTST-005/2026. Hợp nhất mã Gemini v1.1, kết quả kiểm toán Grok và schema provenance v1.2 của ChatGPT.

## Kiến trúc
DRIVE FIRST – GITHUB COMPUTE – MULTI-AI KNOWLEDGE.
- **GitHub Actions** (`.github/workflows/astra-graphify-build.yml`): dựng đồ thị mã công khai bằng Graphify chế độ cây cú pháp (không LLM), kiểm thử, cache để dựng gia tăng, xuất artifact. Đây là máy xử lý theo phiên, không phải máy chủ MCP thường trực.
- **Drive**: kho chính thức cho đồ thị/tri thức riêng. Không đưa đồ thị riêng, dữ liệu BHXH, khóa truy cập lên repo này.
- **MCP stdio / API loopback**: chỉ đọc, có xác thực danh tính, phân quyền theo dự án.

## Mô-đun
| Tệp | Chức năng |
|---|---|
| `security.py` | SHA-256, quét bí mật/dữ liệu BHXH, chính sách đường dẫn (allowlist + denylist) |
| `provenance.py` | Kiểm theo **schema chính thức** `skills/astra-graphify/provenance-v1.2.schema.json`; thiếu schema/thư viện → từ chối (fail closed) |
| `schemas/astra-graph-v1.schema.json` | Schema nội dung đồ thị, tách khỏi schema provenance |
| `convert.py` | Graphify `graph.json` → đồ thị ASTRA + một bản ghi provenance v1.2 cho mỗi nút và mỗi cạnh; `check_integrity` |
| `store.py` | Kiểm toàn bộ rồi mới ghi; ghi nguyên tử; giữ `.prev` để khôi phục; prune có chốt an toàn |
| `auth.py` | Token lưu dạng hash; project chỉ được cấp theo danh tính đã xác thực |
| `query.py` | Tìm kiếm, láng giềng, thống kê; kèm nguồn gốc; đo `context_chars`, `token_count: null` |
| `mcp_server.py` | MCP 2025-06-18 qua stdio: initialize/notifications/ping/tools.list/tools.call, mã lỗi JSON-RPC chuẩn |
| `api.py` | HTTP chỉ 127.0.0.1, Bearer, chỉ GET |
| `cli.py` | `build`, `verify`, `stats`, `rollback`, `prune`, `mcp`, `serve` |

## Lỗi đã sửa so với v1.1
1. API/MCP tin `project_id` do bên gọi tự khai → nay xác thực token, chỉ cấp dự án trong allowlist của danh tính.
2. `upsert_record` sửa trạng thái trước khi kiểm cạnh chéo dự án → nay dựng bản ứng viên, kiểm toàn bộ, đạt mới ghi.
3. `prune_deleted_sources` xóa sạch khi Drive trả danh sách rỗng/thiếu → nay bắt buộc `complete: true` và chặn xóa quá 20%.
4. Kiểm thử dùng `MINIMAL_SCHEMA` → nay dùng schema v1.2 chính thức.
5. Cạnh trỏ tới thực thể không tồn tại → nay kiểm cả hai đầu, cùng dự án, có provenance khớp quan hệ.
6. MCP chỉ mô phỏng JSON-RPC → nay theo vòng đời và định dạng kết quả MCP; thông báo không được trả lời; lỗi đúng mã.
7. Không phân biệt nguồn/trích xuất/suy luận/xác minh → `source_kind`, `evidence_kind`, `verification_status`, `execution_status` riêng; INFERRED không bao giờ VERIFIED; module ngoài không bịa hash.
8. Phụ thuộc chỉ ghim tên → `requirements.lock` khóa đủ 36 gói kèm hash (Python 3.12, linux x86_64).

## Chạy
```bash
pip install --require-hashes --only-binary=:all: -r astra_graphify/requirements.lock
python -m unittest discover -s astra_graphify/tests -t . -v
python -m astra_graphify build --src . --project ASTRA_WEB_PUBLIC --data graphify-data \
  --revision "$(git rev-parse HEAD)" --url-base "https://github.com/kienbhxh-cloud/astra-web-ailk/blob/$(git rev-parse HEAD)/" \
  --allow skills --allow bridge --allow tests --allow astra_graphify --report out/build-report.json
ASTRA_GRAPHIFY_PRINCIPALS=/duong/dan/principals.json ASTRA_GRAPHIFY_TOKEN=... python -m astra_graphify mcp
```

## Khôi phục
- Đồ thị: `python -m astra_graphify rollback --project ASTRA_WEB_PUBLIC` (về snapshot trước).
- Mã: `git revert` commit hợp nhất; thư mục `astra_graphify/` độc lập, không sửa mã cũ của repo.

## Giới hạn hiện tại
- `Code.gs` (Apps Script) chưa được Graphify 0.9.119 nhận dạng → chưa có trong đồ thị.
- Tài liệu Drive (Word/PDF/Excel) chưa đưa vào đồ thị trong CI công khai; làm ở phía Drive/Apps Script.
- Chưa đo tiết kiệm token: NOT_TESTED.
