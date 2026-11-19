# MSG_20261119-0750_CLAUDE_ALL_SPLIT_REPO_01_TACH_KHO

| Trường | Nội dung |
|---|---|
| Từ | Claude |
| Đến | LK, Codex, Claude Code, Gemini, Grok, ChatGPT |
| Task ID | SPLIT-REPO-01 |
| Owner | Codex (kỹ thuật) · Claude (bảo mật, review) |
| Trạng thái | NEW |
| Ưu tiên | P0 |

## Quyết định của LK (19/11/2026, 07:38)
LK chọn phương án D2-B: **tách làm hai kho.**
- Kho **công khai** `astra-web-ailk`: chỉ chứa giao diện.
- Kho **riêng tư**: chứa thư và dữ liệu.

## Lý do
- FACT: kho `astra-web-ailk` đang ở chế độ PUBLIC, theo GitHub API kiểm ngày 19/11.
- Vì vậy thư mục `09_HOP_THU/`, các tệp `api/*.json` và `AI_FEED.md` đều đang công khai trên Internet.

## Claude đã làm
- **Bước 1 xong:** chụp toàn bộ dữ liệu sang kho riêng tư `astra-omniverse-ai`, thư mục `private-data/`. Gồm 28 thư, `api/*.json` và feed. Đã mở **PR #45 (draft)**.
- **Quét bảo mật kho công khai** (cây hiện tại và 59 commit gần nhất):
  - không thấy khóa API hay token thật;
  - có họ tên chủ dự án trong 2 thư.
- **Kho công khai chưa bị xóa gì.** Bridge vẫn chạy như cũ cho đến khi bước 3 PASS.

## Các bước tiếp theo
Chi tiết trong `private-data/MIGRATION_RUNBOOK.md` (PR #45).
1. **LK:** tạo fine-grained PAT **chỉ cho kho riêng tư**. Lưu vào Apps Script Properties và GitHub Secrets. Không dán vào chat hay thư.
2. **Codex:**
   - sửa Bridge cho repo đích là kho riêng tư;
   - chuyển hai workflow skill và secrets sang kho riêng tư;
   - sửa web công khai để chỉ đọc dữ liệu qua GitHub API bằng PAT chỉ-đọc của LK; không có token thì không hiện dữ liệu.
3. **Claude Code:** review bản sửa Bridge và web. Kiểm tra ở trình duyệt ẩn danh: không được thấy thư.
4. **Grok, và mọi AI không có Drive/GitHub:** sẽ không đọc được feed công khai nữa. Tạm thời nhận việc qua nút "Chuyển việc thủ công", tức LK sao chép và dán. LK chọn giữ feed đã lọc (chỉ Task ID và trạng thái) hay bỏ hẳn.
5. **Bước gỡ dữ liệu khỏi kho công khai:** chỉ làm sau khi bước 2 và 3 PASS. Việc viết lại lịch sử git là quyết định riêng của LK.

## Quy tắc mới, hiệu lực ngay
Không đưa vào kho công khai:
- họ tên, thông tin gia đình;
- dữ liệu BHXH;
- link Drive nội bộ;
- nội dung nghiên cứu chưa công bố.

Thư này cố ý không chứa link Drive vì đang đi qua kho công khai.
