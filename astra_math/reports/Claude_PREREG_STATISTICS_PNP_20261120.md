# Claude — PREREG_STATISTICS.md (đăng ký trước phần thống kê cho chương trình PNP)

- **Mã:** ASTRA-LO/PNP-MASTER-005 · sản phẩm của Claude: PREREG_STATISTICS, xác suất chính xác, tiêu chí chứng nhận SAT
- **Ngày:** 20/11/2026 · **Từ:** Claude (phiên chat, KTST)
- **Trạng thái:** DRAFT để ChatGPT đưa vào PROTOCOL_MASTER. Văn bản chỉ được khóa khi LK duyệt; sau đó không sửa, mọi thay đổi phải ra phiên bản mới
- **Mã tái lập:** `astra_math/pnp/calc_prereg.py` (GitHub, nhánh `claude/astra-math-research-wdvww8`)

---

## 1. Các con số chuẩn khi H0 đúng [X]

Tất cả tính bằng phân số chính xác. Phân phối của u (số đuôi khác nhau trong 27 giải) tính bằng quy hoạch động.

| Đại lượng | Giá trị |
|---|---|
| P(một số về ≥ 1 lần trong kỳ) | 1 − 0,99²⁷ = **0,2376573** |
| E[u], số đuôi khác nhau mỗi kỳ | **23,7657** |
| P(bộ 5 số có ≥ 1 số về), trung bình theo u | **0,7496559** |
| Mốc từng kỳ cho bộ 5 số (dùng khi chấm) | 1 − C(100−u_t, 5)/C(100, 5) |
| Brier score của dự báo hằng số cho 1 biến hiện diện | p(1−p) = **0,1811763** |
| Số nháy mỗi kỳ của bộ 5 số: kỳ vọng / phương sai | **1,35 / 1,2825** |
| Số nháy mỗi kỳ cần để hòa vốn (5 số × 5 điểm) | **1,40625** nếu giá 22.500đ (cần hơn mốc **4,17%**); **1,4375** nếu giá 23.000đ (cần hơn mốc **6,48%**) |

## 2. Phân tích lực thống kê [X]

Mức ý nghĩa α = 0,05/6 một phía (Holm cho 6 so sánh chính theo MASTER-005, mục 4). Lực thống kê 80%.

**Chỉ số "bộ 5 có ≥ 1 số về":**

| Lợi thế thật so với mốc 74,97% | Số kỳ cần |
|---|---|
| +1 điểm % | 19.509 |
| +2 điểm % | 4.841 |
| +3 điểm % | 2.135 |
| +5 điểm % | 756 |

**Chỉ số số nháy (quyết định lời/lỗ):**

| Lợi thế thật | Số kỳ cần |
|---|---|
| Vừa đủ hòa vốn, giá 22.500đ (+4,17%) | **4.244** (khoảng 11,6 năm) |
| Vừa đủ hòa vốn, giá 23.000đ (+6,48%) | 1.754 |
| +10% | 737 |
| +20% | 185 |

**Lực thống kê thực tế để phát hiện lợi thế vừa đủ hòa vốn (giá 22.500đ):**

| Số kỳ chấm | Lực |
|---|---|
| 60 | 2,2% |
| 180 | 4,2% |
| 365 | 7,4% |
| 1.000 | 20,5% |

**Đính chính** [X]:
1. Mốc **60 kỳ** trong KTST-009 của em là **không đủ**. Em rút lại mốc này.
2. Mốc **180 kỳ** của MASTER-005 chỉ phát hiện được lợi thế từ khoảng **+20% số nháy** trở lên. Lợi thế như vậy lớn gần gấp 5 lần mức cần để hòa vốn.

**Đề xuất (LK quyết định):**
- **(A)** Chấm tương lai bằng **e-process** (giám sát liên tục, hợp lệ ở mọi thời điểm dừng). Không khóa số kỳ cố định. Dừng và bác bỏ H0 khi W_t ≥ 20 (α = 0,05 cho **một** thuật toán đã khóa), hoặc khi W_t ≥ 20 × số thuật toán được khóa song song (hiệu chỉnh Bonferroni). Đúng như ChatGPT đã nêu ở thư KTST-008.
- **(B)** Nếu giữ số kỳ cố định, phải ghi rõ **lợi thế nhỏ nhất đáng quan tâm**. Ví dụ "+20% nháy" thì cần 185 kỳ. Đồng thời phải nói thẳng: một kết quả âm trên 185 kỳ **không loại trừ** được lợi thế nhỏ hơn.

## 3. Phân bổ alpha cho toàn chương trình

- **Phần hồi cứu** (WP2, WP3, WP4 trên dữ liệu 2005–2026, dữ liệu đã bị xem): chỉ dùng để **mô tả và chọn ứng viên**. Không tiêu alpha. Không được dùng để tuyên bố bất kỳ kết quả nào.
- **Phần xác nhận tương lai:** α tổng = 0,05. Tối đa 3 thuật toán được khóa (mỗi nhánh F1, F2, F3 một thuật toán), mỗi thuật toán so với 2 mốc (uniform iid và tần suất 90 kỳ), tức 6 so sánh. Áp dụng Holm cho 6 so sánh này, hoặc e-process kèm Bonferroni nếu chọn (A).
- **WP2 (bộ phân biệt):** Holm riêng ở mức 0,05 trên tối đa 20 bộ đã đăng ký trước. Mục đích là **kiểm tra H0**, không phải dự báo. Nếu WP2 bác bỏ H0, việc **đầu tiên** là rà lỗi dữ liệu (WP0), chưa được khóa mô hình ngay.

## 4. Tiêu chí chứng nhận cho phép tìm kiếm SAT/MaxSAT/SMT (WP3, F1/F2)

Một kết quả của bộ giải chỉ được ghi nhãn [X] khi đạt đủ cả 6 điều sau:

1. **Ngữ pháp luật khóa trước.** Gồm ngữ pháp G, kích thước tối đa s và **số luật |G_s| đếm chính xác** (đếm bằng #SAT/WMC, `wmc.py`). Số |G_s| chính là số phép thử ngầm.
2. **Ngưỡng lấy từ mô phỏng ngẫu nhiên.**
   - Ngưỡng τ_s = phân vị 95% của "điểm trong mẫu của luật tốt nhất".
   - Tính trên **≥ 1.000 bộ dữ liệu giả lập theo H0**, cùng kích thước, cùng các ngày vắng.
   - Câu hỏi đưa cho bộ giải là: *"Có luật nào trong G_s đạt điểm > τ_s không?"*
   - Cách này tự động tính đến định lý T3 (THEORY_REVIEW, mục 4).
3. **Chứng nhận UNSAT phải có bằng chứng kiểm được.** Bộ giải phải xuất chứng minh DRAT/LRAT, và chứng minh đó phải được `drat-trim` hoặc `cake_lpr` kiểm. Kết quả OPTIMAL hay UNSAT của CP-SAT/MaxSAT mà **không có** chứng minh chỉ được nhãn [C]. TIMEOUT thì **không có kết luận**.
4. **Kiểm tra độ nhạy bằng tín hiệu cài sẵn.** Cài một quy luật đã biết vào dữ liệu giả lập, với các mức lợi thế 2, 5, 10, 20%. Báo cáo **lợi thế nhỏ nhất mà công cụ phát hiện được**. Một chứng nhận âm chỉ có nghĩa ở mức lợi thế từ ngưỡng đó trở lên.
5. **Đối chứng cùng ngân sách.** So bộ giải với tìm kiếm ngẫu nhiên và tham lam, cùng thời gian và RAM. So với vét cạn ở các bài nhỏ (s ≤ 3) để kiểm tính đúng của phép mã hóa.
6. **Phạm vi phát biểu của chứng nhận âm:** *"Không tồn tại luật nào trong G_s đạt điểm vượt τ_s trên đoạn dữ liệu D"*. Không mở rộng sang ngữ pháp khác, kích thước khác hay đoạn dữ liệu khác.

## 5. Chống rò rỉ (phối hợp WP5)

- Kiểm thử bắt buộc: thay toàn bộ dữ liệu từ ngày t trở đi bằng (a) dữ liệu giả lập, (b) hàng giả toàn số 0. Dự báo ngày t phải **giống từng bit** trong cả hai trường hợp.
- `xsmb_audit.load_draws` (commit `92c85a2`) đã từ chối hàng giả và ô trống làm lệch cột. Pipeline của Codex phải gọi hàm này với `strict_lengths=True`.

## 6. Việc KTST nghiệm thu

| Gói | Sản phẩm cần nộp | KTST kiểm |
|---|---|---|
| F1/F2 (Codex) | Ngữ pháp, \|G_s\|, τ_s từ mô phỏng, chứng minh DRAT, kết quả tín hiệu cài sẵn | Đủ 6 tiêu chí ở mục 4 |
| F3 / H3 (Codex) | `xsmb_exact.py` | Khớp từng chữ số với các con số ở mục 1 và với vét cạn |
| WP2 (Claude Code / Codex) | Danh sách ≤ 20 bộ phân biệt, khóa trước khi chạy | Holm; đối chiếu với kết quả nén của Claude Code (p sau hiệu chỉnh 0,09) |

Trân trọng,
**Claude** (KTST)
