# ASTRA-LO/ACK-001 — Claude xác nhận tham gia + rà soát `xsmb_audit` lần 1

- Mã thư: ASTRA-LO/ACK-001 · Mã nhiệm vụ: ASTRA-LO-MATH-001
- Ngày: 19/11/2026
- Từ: Claude (Toán học và kiểm định)
- Gửi: LK · Đồng gửi: ChatGPT, Gemini, Grok, Codex
- Dự án: ASTRA LÔ XSMB
- Tham chiếu: ASTRA-LO/INVITE-001/2026; ASTRA-MATH-KTST-006, KTST-007
- Yêu cầu phản hồi: LK duyệt các sửa đổi ở mục 3; Codex/Grok kiểm chứng lại độc lập.

## 1. Phiếu ACK

| Mục | Trả lời |
|---|---|
| Tên AI | Claude (phiên Claude Code trên cloud) |
| Đã đọc thư mời | Có |
| Truy cập Hộp thư Drive | Chưa xác định: đọc được tệp Drive khi có ID; **chưa được cấp đường dẫn thư mục Hộp thư ASTRA LÔ** |
| Truy cập kho tài liệu (Drive) | Chưa: chưa có đường dẫn thư mục |
| Truy cập kho Skill | Có (GitHub: `10_SKILLS/`, `skills/`); thư mục Skill trên Drive: chưa có đường dẫn |
| Truy cập GitHub | Có: đọc nhánh `claude/astra-math-research-wdvww8`, push nhánh `claude/adoring-noether-fzur6n` |
| Đã đọc hướng dẫn xsmb_audit | Có: đã đọc toàn văn tệp Drive `1R8cY3CTZW68UHMnXMNhTBc4hw4whfrPv` (KTST-007) |
| Nhiệm vụ nhận thực hiện | Mục V.2: Toán học và kiểm định (ASTRA Math, `xsmb_audit.py`) |
| Công việc đầu tiên | Kiểm chứng độc lập `xsmb_audit.py` và sửa lỗi (đã làm, xem mục 2–3) |
| Khó khăn / quyền còn thiếu | Cần đường dẫn các thư mục Drive: Hộp thư, Tài liệu, Skill và Mô hình, Kết quả nghiên cứu. Chưa có dữ liệu XSMB thật (chờ Gemini). |
| Sản phẩm thực tế | Nhánh `claude/adoring-noether-fzur6n`: `astra_math/xsmb_audit.py`, `astra_math/tests/test_xsmb_audit.py` và thư này |

## 2. Kết quả kiểm chứng độc lập

- [X] 10 kiểm thử XSMB gốc chạy lại đều đạt (Python 3, không cần thư viện ngoài).
- [X] Đã tính lại bằng tay: P(lô) = 1 − 0,99²⁷ = 23,7657%; xiên 2 = 1 − 2·0,99²⁷ + 0,98²⁷ = 5,4882%; hòa vốn lô trả theo nháy = 100/27 = 3,7037. Khớp với công cụ.
- [X] Công thức xiên k (bao hàm–loại trừ), phân phối nháy Nhị thức(27, 1/100) và Holm đều đúng.
- [!] Bộ 24 kiểm thử còn lại (`test_astra_math.py`) **không chạy được** ở môi trường này vì thiếu thư viện `ortools`. Con số "34 kiểm thử đạt" vì vậy mới được kiểm chứng một phần: 10/34 tại đây.

## 3. Lỗi phát hiện và đã sửa

| # | Mức | Lỗi | Sửa |
|---|---|---|---|
| 1 | **Nghiêm trọng** | `evaluate_strategy` dùng `binom_tail` tính bằng phân số chính xác, mẫu số cỡ 100^(27·n). `--demo` treo **hơn 2 phút** mà không in ra gì (đã đo). Với dữ liệu XSMB nhiều năm (n ≈ 3.650 trở lên), `--csv` thực tế **không bao giờ chạy xong**. | Thêm `binom_tail_float`, tính tổng trong không gian log. Lệch so với kết quả chính xác ≤ 1e-12. `--demo` còn **0,2 giây**; 3.650 ngày chấm dưới 5 giây. `binom_tail` chính xác vẫn giữ cho n nhỏ. |
| 2 | Phương pháp | KTST-007 mục 6 ghi: "Holm hoặc BH đúng cả khi các cầu tương quan". Điều này **sai với BH**: BH chỉ đảm bảo FDR khi các kiểm định độc lập hoặc phụ thuộc dương (PRDS). Holm thì đúng với mọi kiểu phụ thuộc. | Thêm `benjamini_yekutieli` (FDR dưới phụ thuộc tùy ý). Đề nghị sửa câu trong KTST-007. |

Kiểm thử mới: 3 bài (khớp chính xác/xấp xỉ, tốc độ trên 10 năm dữ liệu, BY ⊆ BH). Tổng cộng **13/13 kiểm thử XSMB đạt** [X].

## 4. Điểm yếu còn lại, chưa sửa (đề xuất)

- [C] **Sổ đăng ký trước chưa chống được người giữ tệp.** Thời điểm đăng ký do máy tự khai báo. Chuỗi băm có thể bị tính lại toàn bộ bởi chính người sửa. → Đề xuất neo mỗi bản ghi bằng một commit đã push lên GitHub; thời điểm push do máy chủ ghi nhận và các AI khác có thể kiểm chứng.
- [C] `Registry.evaluate` kiểm tra băm của `code_text` nhưng chạy hàm `strategy` truyền vào riêng, nên không bảo đảm hàm được chạy chính là mã đã đăng ký. → Đề xuất nạp `strategy` trực tiếp từ `code_text` đã băm.
- [C] `load_draws` bỏ qua các ô trống trước khi đếm 27 giải, nên một ô trống cộng một ô thừa có thể làm lệch cột mà không báo lỗi. → Đề xuất kiểm tra đúng 27 cột theo vị trí.
- [H] χ² trên 100 số chỉ phát hiện lệch tần suất. Cần thêm kiểm định phụ thuộc giữa các ngày (tự tương quan, runs test) trước khi nói dữ liệu "công bằng".

## 5. Lập trường khoa học

Với xổ số công bằng, mọi phương pháp chọn số đều có xác suất trúng như chọn ngẫu nhiên và lời/lỗ kỳ vọng âm theo tỷ lệ trả thưởng. Nhiệm vụ của Claude là bảo đảm công cụ đo **đúng**, để mọi tuyên bố "vượt ngẫu nhiên" đều phải qua: đăng ký trước, chấm trên kỳ quay mới, hiệu chỉnh đa kiểm định. Kết luận "không có cầu nào vượt ngẫu nhiên" cũng là một kết quả hợp lệ và sẽ được công bố đầy đủ.

## 6. Việc tiếp theo

1. LK cung cấp đường dẫn 4 thư mục Drive (Hộp thư, Tài liệu, Skill và Mô hình, Kết quả) để Claude lưu thư này lên Drive.
2. Khi Gemini có CSV thật: chạy `fairness_test` và chấm cầu mẫu, báo cáo [X].
3. Nếu LK duyệt: sửa 3 điểm yếu ở mục 4.

Trân trọng,
Claude
