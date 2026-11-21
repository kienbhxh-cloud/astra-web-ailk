# CLUB ROUNDTABLE — NHẬT KÝ THỰC NGHIỆM 21/11/2026

Liên quan skill cá nhân `astra-tao-bot`, nguồn thư `MSG_20261121-2342_GEMINI_ALL_CLUB_ROUNDTABLE_VA_LO_LUYEN_SIEU_AI.md` trong Drive `09_HOP_THU`. Không tự nhận cập nhật bản nhật ký cá nhân trên Drive.

## Phạm vi
- Repo đích: `kienbhxh-cloud/astra-web-ailk`, branch `main`.
- Mã: `skills/club_roundtable.mjs`, `.github/workflows/astra-club-roundtable.yml`, `docs/index.html`.
- Chủ đề công khai: `09_HOP_THU/MSG_20261121-2355_LK_ALL_CLUB_FIRST_ROUNDTABLE.md`, thẻ `[CLUB:ROUNDTABLE]`.

## Quan sát thực tế qua đọc lại GitHub
1. Chủ đề đã commit: `1950878012e7a8d434d5162c007c59a125409e2d`.
2. Biên bản xuất hiện: `09_HOP_THU/MSG_20261121-2355_LK_ALL_CLUB_FIRST_ROUNDTABLE_CLUB_MINUTES.md`, có đủ ROUND 1A, ROUND 1B, ROUND 2A, ROUND 2B, ROUND 3 và nhãn `FIXTURE_SIMULATION`.
3. Skill tạo ra: `10_SKILLS/AUTO_CLUB_EVIDENCE_GATE_2756ef9a.md`, trạng thái `FIXTURE_ONLY_NOT_VALIDATED`, điểm fixture 90/100, chưa được reviewer duyệt.
4. `AI_FEED.md` có mục bản ghi chủ đề và đường dẫn minutes/skill.
5. File test hồi quy: `tests/club_roundtable.test.mjs` commit `94bc3c39cd50a36f463a1ec7d9f25e93dcac58ac`. Chỉ xác minh nguồn đã commit, CHƯA XÁC MINH LƯỢT CHẠY TEST NÀY.
6. Trạng thái GitHub Actions job/log: chưa có mã run ID hoặc log đọc trực tiếp; xác minh artifact trên GitHub, không coi đó là nghiệm thu toàn pipeline.

## Bài học
- Code mẫu ban đầu dùng `git diff-tree HEAD` để phát hiện một tệp có thể bỏ sót chủ đề; thay bằng workflow chọn path từ sự kiện, script nhận `--topic`.
- Điểm tự chấm của LLM không được coi là nghiệm thu. Skill chỉ là đề xuất cần review.
- Chế độ fixture không gọi LLM; LIVE chỉ khi `CLUB_LIVE_ENABLED=true` và `GEMINI_API_KEY` có cấu hình.
- Chống tạo bản trùng bằng biên bản cố định theo tên chủ đề và SHA đầu vào, giữ dấu vết mô phỏng/real.
- Không tuyên bố Drive webhook thành công nếu chưa có phản hồi xác nhận.

## Còn mở
- Kiểm chứng GitHub Actions log và tự động chạy bộ `node --test tests/club_roundtable.test.mjs`.
- Thử nghiệm LIVE với quyền/chấp thuận phí, ghi số token/chi phí và giới hạn.
- Kiểm chứng đồng bộ Google Drive bằng webhook, không chỉ ghi GitHub.
- Phê duyệt thủ công nội dung skill trước khi cho agent nạp sử dụng.
