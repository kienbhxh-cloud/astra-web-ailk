# ASTRA CLUB ROUNDTABLE PROTOCOL v0.1

## Phạm vi
Chủ đề công khai trong `09_HOP_THU/MSG_*.md` có thẻ `[CLUB:ROUNDTABLE]` hoặc `[CLUB:ARENA]`. Tuyệt đối không đăng dữ liệu BHXH, thông tin cá nhân hoặc secret.

## 3 vòng
1. **Blind Perspective:** hai vai trò kiến trúc và kiểm toán nhận cùng chủ đề, không thấy bài của nhau. Hai vai trò không đồng nghĩa hai AI độc lập.
2. **Cross Critique:** mỗi bên đọc bài của đối phương, chỉ ít nhất một lỗ hổng thực tế và một bản vá cụ thể.
3. **Skill Distillation:** điểm tối đa 100 (thực thi 40, đúng đắn 35, tiết kiệm tài nguyên 25). Điểm mô hình tự chấm không phải đánh giá độc lập.

Chỉ tạo đề xuất `10_SKILLS/AUTO_*.md` khi SCORE từ 85 trở lên, có SUMMARY và SKILL_RULE, phản biện đủ nội dung. Tệp chỉ có trạng thái DRAFT_REVIEW_REQUIRED hoặc FIXTURE_ONLY_NOT_VALIDATED, không được tự xem là skill đã được phê duyệt hay cập nhật trọng số AI.

## Các chế độ
- `node skills/club_roundtable.mjs --fixture --topic 09_HOP_THU/MSG_X.md`: kiểm thử mô phỏng, không gọi API AI.
- `node skills/club_roundtable.mjs --live --topic 09_HOP_THU/MSG_X.md`: chỉ khi có secret GEMINI_API_KEY và cho phép chi phí.
- Không ghi đè biên bản đã có, không công bố suy luận như kết quả độc lập. Mỗi biên bản lưu SHA nguồn, tên model/mode, lỗi và kết quả review.
- Drive webhook chỉ bật khi cấu hình HTTPS + BRIDGE_SECRET và phản hồi ok=true; còn không, trạng thái chưa đồng bộ Drive.
- Cổng GitHub Actions cần log thực, quyền ghi và các secrets hợp lệ; không mặc định tuyên bố PASS. Lịch GitHub Actions có thể trễ.
