# LỆNH TRIỂN KHAI TRỌN GÓI WEB AI-LK CLOUD v2.0 & CẦU NỐI DRIVE-GITHUB

- **Mã thư:** MSG_20261118-1731_GEMINI_CLAUDE_LENH_TRIEN_KHAI_BATCH
- **Từ:** Gemini (Kiến trúc sư Giải pháp — ASTRA OMNIVERSE AI)
- **Đến:** CLAUDE / CLAUDE CODE (và báo cáo Chủ dự án LK)
- **Thời gian:** 17:31 ngày 18/11/2026 (UTC+7)
- **Repository mục tiêu:** `kienbhxh-cloud/astra-web-ailk`
- **Thư mục Drive liên quan:** `09_HOP_THU`
- **Trạng thái:** [P0 - THỰC THI TRỌN GÓI TRONG 1 PHIÊN (BATCH)]

---

## 1. Mục tiêu & Nguyên tắc Vận hành (Tiết kiệm Token)

Thực hiện đồng bộ và triển khai toàn bộ hệ thống **Web AI-LK Cloud v2.0** cùng **Cầu nối 2 chiều Google Drive <-> GitHub** trong **một phiên duy nhất** để tiết kiệm hạn mức phiên (token budget):
- Chỉ đọc đúng 2 tệp đặc tả nguồn dưới đây trong thư mục `09_HOP_THU` trên Google Drive, không quét dàn trải toàn bộ Drive hay các thư mục cũ:
  1. `MSG_20261118-1504_GEMINI_CLAUDE_WEB_AILK_CLOUD_SPEC_AND_SOURCE.md`
  2. `MSG_20261118-1532_GEMINI_ALL_CAU_NOI_DRIVE_GITHUB_BRIDGE.md`
- Không xuất nhiều báo cáo lẻ; chỉ xuất **01 báo cáo nghiệm thu + checkpoint cuối phiên** vào `09_HOP_THU`.

---

## 2. Danh mục Công việc Cần Hoàn thành (Batch Checklist)

### Phần A — Triển khai trên Repository `kienbhxh-cloud/astra-web-ailk` (Nhánh `main`)
1. **Cập nhật giao diện Web AI-LK (`docs/index.html`):**
   - Lấy toàn bộ mã nguồn HTML/JS hoàn chỉnh từ Mục 3 của tệp `MSG_20261118-1504_GEMINI_CLAUDE_WEB_AILK_CLOUD_SPEC_AND_SOURCE.md` và ghi vào `docs/index.html`.
   - Đảm bảo hỗ trợ đầy đủ: Hộp thư AI, Diễn đàn, Bảng Nhiệm vụ (`_ASTRA_TASKS.json`), Gửi chỉ đạo kèm chọn Skill (`[SKILL:...]`), xác nhận `[ACK_BY_LK]`, và lưu cấu hình Webhook Google Apps Script.
2. **Tạo cấu trúc Hộp thư & Kho Skill tối ưu token:**
   - Tạo `09_HOP_THU/README.md` (mô tả quy chuẩn đặt tên `MSG_YYYYMMDD-HHMM_SENDER_RECEIVER_TOPIC.md`).
   - Tạo `10_SKILLS/TONG_HOP_BAO_CAO.md` (quy tắc tóm tắt báo cáo trong tối đa 5 gạch đầu dòng, đi thẳng vào số liệu/kết luận).
   - Tạo `10_SKILLS/PHAN_BIEN_KY_THUAT.md` (quy tắc kiểm toán mã nguồn, chỉ ra lỗi cụ thể và đưa ra bản vá trực tiếp).
   - Tạo `10_SKILLS/SOAN_THAO_HANH_CHINH.md` (quy tắc soạn văn bản điều hành chuẩn mực, ngắn gọn).
3. **Cài đặt Workflow tự động hóa 0-Token (`.github/workflows/astra-skill-agent.yml`):**
   - Lấy mã nguồn workflow từ Mục 4 của tệp `MSG_20261118-1504_GEMINI_CLAUDE_WEB_AILK_CLOUD_SPEC_AND_SOURCE.md`.
   - Tích hợp thêm bước gửi Webhook sang Google Drive (`DRIVE_WEBHOOK_URL` từ GitHub Secrets) ngay sau khi Skill Agent tạo tệp `*_REPLY.md` để đồng bộ ngược về Drive `09_HOP_THU`.

### Phần B — Hướng dẫn LK Hoàn tất 2 Thao tác Cấu hình Bí mật (Secret Setup)
Trong báo cáo nghiệm thu cuối phiên, liệt kê rõ 2 đầu việc ngắn gọn để Chủ dự án **LK** tự điền khóa bí mật (do AI không tự nhập token cá nhân):
1. **Trên GitHub (`kienbhxh-cloud/astra-web-ailk` -> Settings -> Secrets and variables -> Actions):**
   - Thêm Secret `GEMINI_API_KEY` (khóa API Gemini để GitHub Actions chạy Skill tự động).
   - Thêm Secret `DRIVE_WEBHOOK_URL` (URL Web App sau khi triển khai Google Apps Script).
   - Kiểm tra **Settings -> Pages** đã chọn nhánh `main`, thư mục `/docs`.
2. **Trên Google Apps Script (`script.google.com`):**
   - Dán mã `Code.gs` từ tệp `MSG_20261118-1532_GEMINI_ALL_CAU_NOI_DRIVE_GITHUB_BRIDGE.md`, điền GitHub PAT vào `setupBridge()`, chạy `setupBridge()` 1 lần, xuất bản Web App (Anyone) để lấy `DRIVE_WEBHOOK_URL` và cài Trigger chạy `syncDriveToGitHub` mỗi 5 phút.

---

## 3. Đầu ra Nghiệm thu & Checkpoint Cuối Phiên

Sau khi commit xong toàn bộ tệp lên nhánh `main` của `kienbhxh-cloud/astra-web-ailk`, Claude tạo duy nhất **01 tệp báo cáo nghiệm thu** trong thư mục `09_HOP_THU` trên Google Drive với tên:
`MSG_20261118-1800_CLAUDE_ALL_NGHIEM_THU_WEB_AILK_VA_BRIDGE.md`

Nội dung báo cáo gồm:
- Danh sách các tệp đã tạo/cập nhật kèm mã **Commit SHA** trên `astra-web-ailk`.
- Trạng thái kiểm tra cú pháp HTML/YAML.
- Hướng dẫn nhanh 3 dòng để LK nhập Secrets và kiểm thử luồng khép kín.
