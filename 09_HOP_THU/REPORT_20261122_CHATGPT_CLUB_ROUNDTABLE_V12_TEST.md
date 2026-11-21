# ASTRA OMNIVERSE AI | CLUB ROUNDTABLE v1.2 — BÁO CÁO KIỂM THỬ & BÀN GIAO
**Task:** CLUB-ROUNDTABLE-V1.2 / DEEPSEEK-ASTRA-002  
**Ngày:** 22/11/2026  
**Người thực hiện:** ChatGPT / KTS Trưởng  
**Nguồn chỉ đạo:** LK, kiểm toán DEEPSEEK-ASTRA-002 đã được LK xác nhận nghiệm thu  
**Nhánh:** `main` tại `kienbhxh-cloud/astra-web-ailk`  
**Trạng thái code:** COMMITTED / TESTED_LOCAL / CLOUD_ACTIONS_NOT_VERIFIED / LIVE_API_NOT_TESTED.

## 1. Bản mã đã cập nhật
- `skills/club_providers.mjs`: mọi lời gọi model trả về `{ok,intended_provider,actual_provider,model,status,error,latency_ms,trace}`, thêm `text` và trường tương thích. Trace ghi `SKIPPED: NO_KEY`, retry `429`/`503`, lỗi mạng/timeout, HTTP 200, đầu ra rỗng. Không đưa API key hoặc Authorization header vào log.
- `skills/club_providers.test.mjs`: ca (a) thiếu DEEPSEEK_API_KEY, (b) DeepSeek 429 rồi OpenRouter thành công, (c) mọi provider thất bại; thêm ca HTTP 200 nhưng rỗng.
- `skills/club_roundtable.mjs`: giới hạn 12.000 ký tự, chỉ nhận thẻ `[CLUB:ROUNDTABLE]` ở 20 dòng đầu; SCORE parse không hợp lệ thành `null` và trạng thái `REJECTED_NO_SCORE`; điểm >=85 chỉ sinh skill vào `10_SKILLS/_pending/` với nhãn `[SELF-REPORTED]` và `REVIEW_PENDING`.
- `skills/approved_skill_loader.mjs` + `skills/skill_agent.mjs`: từ chối nạp mọi skill thiếu `status=REVIEW_ACCEPT` hoặc reviewer_id hợp lệ; không duyệt tệp trực tiếp trong thư mục _pending.
- `skills/club_drive_sync.mjs`: webhook Google Drive tách riêng khỏi bộ sinh Roundtable.
- `.github/workflows/astra-club-roundtable.yml`: concurrency group `club-roundtable`, bot + [skip-club] guards, fixture-only, các khóa `DRIVE_WEBHOOK_URL`/`BRIDGE_SECRET` chỉ được truyền vào bước đồng bộ; commit workflow outputs có `[skip-club]`.
- `tests/club_roundtable.test.mjs`, `skills/approved_skill_loader.test.mjs`: thử nghiệm cách ly, chống chạy trùng, thiếu SCORE, thẻ sai vị trí, đầu vào quá dài.

## 2. Thực thi kiểm thử thực tế
**Môi trường thực thi:** container Linux, Node.js v22.16.0, không Internet, không khóa API thật. Đã thực sự chạy tại máy thực thi cục bộ của phiên ChatGPT:
```
node --test skills/club_providers.test.mjs
# 4 PASS / 0 FAIL
node --test skills/club_providers.test.mjs skills/approved_skill_loader.test.mjs tests/club_roundtable.test.mjs
# 9 PASS / 0 FAIL
node --check skills/club_roundtable.mjs
node --check skills/club_drive_sync.mjs
# exit 0
```
Mã nguồn dùng cho kiểm thử được so với nội dung nguồn GitHub bằng so sánh ký tự/hàm băm FNV-1a 32-bit, không chỉ kiểm tra tên tệp. Các tệp nguồn và test đã xác minh khớp.

**Phạm vi PASS:** Test unit với request giả lập; fixture 3 vòng; kiểm thử không dùng mạng hoặc gọi DeepSeek/Gemini/OpenRouter thật. Không coi test unit là nghiệm thu provider live.

## 3. Còn mở / chưa xác minh
- Chưa có `run_id`/job log GitHub Actions chứng minh workflow v1.2 thực thi thành công trên GitHub-hosted runner.
- Chưa thử provider API thật, fallback live, giới hạn phí và kết nối AI ngoài hệ thống.
- Chưa xác minh đồng bộ webhook Drive thật (chỉ có logic tạo và kiểm tra phản hồi).
- Chưa có reviewer độc lập ký duyệt skill _pending; không có việc cập nhật trọng số mô hình.
- Một số skill cũ trong `10_SKILLS/` không có metadata REVIEW_ACCEPT và reviewer_id sẽ bị từ chối cho đến khi được xét duyệt, đúng theo quy tắc an toàn mới.
- Tính đúng đắn của điểm tự chấm chưa được hội đồng nghiệm thu độc lập.

## 4. Kết luận
**SOURCE COMMITTED, LOCAL TEST PASS, CLOUD ACTIONS NOT VERIFIED, LIVE NOT TESTED.**
Không tự nhận toàn bộ hệ thống AI hoạt động 24/7 hoặc DeepSeek/Gemini đã tham gia cuộc thảo luận thực tế. Việc cấu hình API và thử live phải có quyền và trần phí được LK phê duyệt.

## 5. Nhật ký bài học cho skill astra-tao-bot
Khi cập nhật workflow tự động: cố định chế độ fixture mặc định, chỉ tiêm secret vào bước cần thiết, bảo vệ vòng lặp bot, test NO_KEY/429/fallback/all-fail/empty, không tự duyệt skill và so hash bản thử với bản đã push. Cần ghi nhận vào nhật ký thực nghiệm chính thức trên Drive và xác minh đã lưu.
