# [CLUB:ROUNDTABLE] Phiên thử nghiệm số 01 — Kiểm chứng phối hợp AI có bằng chứng
- Người triệu tập: LK (theo chỉ đạo P0 ngày 21/11/2026)
- Chủ đề: Cách tổ chức AI đọc thư, xác minh ACK và bàn giao kết quả có bằng chứng trên Web AI-LK Cloud
- Phạm vi: Đề xuất kỹ thuật công khai, không dùng dữ liệu cá nhân, không chứa thông tin BHXH hay secret
- Task ID: CLUB-TEST-001
- Chế độ kiểm thử mặc định: FIXTURE/SIMULATION nếu chưa được bật LIVE
- Tiêu chí: 3 vòng có riêng 1A/1B, 2A/2B, 3; tạo biên bản trong 09_HOP_THU; nếu vượt 85 điểm phải có AUTO skill nhưng gắn nhãn chưa review

## Câu hỏi cho hội đồng
Làm thế nào xây dựng quy trình giao nhiệm vụ và ACK có thể kiểm chứng, chi phí thấp, tránh nhầm lẫn giữa thông điệp được gửi và tác vụ thực sự đã thực hiện?

Yêu cầu ở vòng một phải có hai góc nhìn độc lập theo vai trò. Vòng hai phải có ít nhất một lỗ hổng và một bản vá cho mỗi bên. Vòng ba phải đưa ra quyết nghị, đánh giá theo thang 100 và đề xuất skill có tiêu chí kiểm thử. Không được tự nhận Claude, Gemini, Grok, Codex đã tham gia thật khi chỉ dùng fixture hoặc một API.
