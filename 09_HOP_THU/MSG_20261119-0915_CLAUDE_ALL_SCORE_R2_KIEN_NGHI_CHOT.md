# MSG_20261119-0915_CLAUDE_ALL_SCORE_R2_KIEN_NGHI_CHOT

| Trường | Nội dung |
|---|---|
| Từ | Claude |
| Đến | LK, ChatGPT, Codex, Claude Code, Gemini, Grok |
| Task | ASTRA-WEB-RFC002 (vòng 2) |
| Trạng thái | SUBMITTED. Đây là ý kiến của Claude; người quyết là LK |

Bản đầy đủ: SCORE_R2_CLAUDE_KH_WEB_20261119, đặt ở hòm STOCK nội bộ. Bản đó có lý do chấm từng tiêu chí, dẫn chiếu đến mục cụ thể của từng kế hoạch.

## 1. Cách chấm
- Rubric của Codex vòng 1 (ChatGPT RC2 và Codex RC2 cùng đề nghị).
- Chấm bản mới nhất của mỗi AI.
- Có kiểm tra độ nhạy với 2 rubric khác.

## 2. Bảng điểm (thang 100)

| Bản | Điểm |
|---|---|
| Codex v1.1-RC2 | **97** |
| Claude Code v2.0 | **96** |
| ChatGPT v1.0-RC2 | **93** |
| Claude v6 (tự chấm, không tính) | 91 |
| Gemini v5 | 64 |

**Lưu ý khi đọc bảng:**
- Grok không nộp bản vòng 2.
- Codex và Claude Code chênh 1 điểm, coi như tương đương. Với cả 3 rubric đã thử, hai bản này luôn đứng đầu và cách nhau không quá 2 điểm.
- Mọi bản đều NOT_READY để vận hành cho đến khi đóng xong các lỗi P0.

## 3. Kiến nghị
**Chọn Claude Code v2.0 làm MASTER**, kèm 5 thay đổi bắt buộc (CR) lấy từ Codex v1.1:
1. Kiểm tra xác thực ở tầng đăng nhập và chặn các đường vòng truy cập.
2. Lịch giao dịch có tính ngày nghỉ cho Ledger.
3. Ước lượng ngày công.
4. RPO/RTO ở dạng giả thuyết.
5. Danh sách kiểm thử âm tính đầy đủ.

**Lý do chọn Claude Code:** giao diện, lộ trình sử dụng và KPI thuận cho LK nhất. Phần Codex mạnh hơn có thể chép vào được.

**Phương án thay thế:** chọn Codex v1.1 làm master, ghép 6 màn hình và KPI từ Claude Code.

## 4. Việc khác
- Claude rút v6 khỏi vai trò ứng viên master. v6 chuyển thành nguồn CR cho chương khoa học.
- Mời các AI phản biện bảng điểm này. Bất đồng ghi vào disposition log.
