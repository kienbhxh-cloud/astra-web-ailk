# PREREG_STATISTICS v1.2 (HỢP NHẤT) — chương trình PNP, ASTRA LÔ XSMB

- **Phiên bản:** 1.2 · **Ngày:** 20/11/2026 · **Người giữ bút:** Claude KTST (phiên chat). Claude Code đồng tác giả §1–2, §5.
- **Thay thế:**
  - Claude_PREREG_STATISTICS_PNP_20261120 (v1.0, KTST);
  - 20261120_Claude_PNP_PREREG_STATISTICS_v1 và v1.1 (Claude Code);
  - mục 2 của thư PNP-QD-001.

  Các bản cũ được giữ nguyên, không xóa.
- **Đây cũng là STAT_PROTOCOL_REVIEW.md** mà thư PNP-ACTION-006 yêu cầu.
- **Mã:** `astra_math/xsmb_audit.py`, nhánh `claude/astra-math-research-wdvww8`, commit `00aaf39`. 46/46 kiểm thử đạt [X].
- **Trạng thái:** DRAFT. ChatGPT đưa vào PROTOCOL_MASTER. Khóa ở cổng G3; sau khi khóa, mọi thay đổi phải ra phiên bản mới.

## 1. Giả thuyết gốc và con số chuẩn [X]

**H0:** 27 giải của mỗi kỳ độc lập; hai số cuối của mỗi giải đều trên 00–99; các kỳ độc lập với nhau.

| Đại lượng | Giá trị chính xác |
|---|---|
| Một số về ≥ 1 nháy | 1 − 0,99²⁷ = 23,7657% |
| Bộ 5 số cố định có ≥ 1 số về | 1 − 0,95²⁷ = **74,9656%**. Đồng nhất thức Σ_u P(u)·[1 − C(100−u,5)/C(100,5)] đã kiểm bằng phân số chính xác |
| Mốc của từng kỳ khi chấm | p0_t = 1 − C(100−u_t, 5)/C(100, 5). Hàm `p_set_hit_given_u` |
| Số nháy mỗi kỳ của bộ 5 số | X ~ Nhị thức(27; 0,05): kỳ vọng 1,35, phương sai 1,2825 |
| Brier score của dự báo hằng số, 1 biến hiện diện | 0,1811763 |
| **Giá đã chốt (LK, 20/11)** | **22.500đ/điểm**, trả 80.000đ/điểm/nháy |
| Lời/lỗ kỳ vọng | −900đ/điểm (−4,00%). Bộ 5 số × 5 điểm: −22.500đ/kỳ, độ lệch chuẩn khoảng 453.000đ/kỳ |
| Hòa vốn | 1,40625 nháy/kỳ, tức cao hơn ngẫu nhiên **4,17%** |

**Chỉ số chính của lời/lỗ là tổng số nháy, không phải tỷ lệ kỳ trúng.** F3 bắt buộc báo cáo cả hai.

## 2. Mức lợi thế nhỏ nhất phát hiện được (MDE) [X]

Bảng dưới để LK biết giới hạn, **không** phải số kỳ khóa trước. α = 0,05/6, lực thống kê 80%.

| Chỉ số | Số kỳ cần để phát hiện |
|---|---|
| Tỷ lệ kỳ trúng ≥ 1 số (F3) | +1 điểm %: 19.570 kỳ · +2 điểm %: 4.835 · +5 điểm %: 754 · +9,8 điểm %: 180 |
| Số nháy | hòa vốn (+4,17%): 4.244 · +10%: 737 · +20%: 185 |
| Brier (F1/F2), độ lệch xác suất δ | δ = 0,005: khoảng 2.780 · δ = 0,01: khoảng 726 · δ = 0,022: khoảng 147 |

- **Hệ quả 1:** ngưỡng F3 "+1 điểm %" và ngưỡng Brier 0,0005 của Codex **bị bỏ**. Thay bằng §3.
- **Hệ quả 2:** dữ liệu 10 năm đã loại trừ một độ lệch **cố định** δ = 0,022 (khoảng 3,1 sai số chuẩn cho mỗi số; χ² cho p = 0,79). Chỉ còn độ lệch **thay đổi theo thời gian** là chưa bị loại trừ.

## 3. Xác nhận tương lai: e-process (LK duyệt phương án A ngày 20/11) [X]

Phương án này thay cho cả 180 kỳ cố định lẫn các phương án SPRT / O'Brien–Fleming trong v1.1 của Claude Code.

- **Chỉ số chính, số nháy của bộ 5 số đã khóa.**
  - Kiểm định H0: E[Y_t | quá khứ] ≤ 1,35.
  - W_t = trung bình theo λ ∈ {0,01; 0,02; 0,044; 0,1; 0,2} của tích Π(1 + λ(Y_s − 1,35)).
  - Hàm `eprocess_mean`.
- **Chỉ số phụ, bộ 5 có ≥ 1 số về.**
  - W_t = trung bình theo λ ∈ {0,05; 0,1; 0,2; 0,5; 1} của tích Π(1 + λ(hit_t − p0_t)/p0_t).
  - Hàm `eprocess_any_hit`.
- **Bác bỏ H0** cho một thuật toán khi W_t ≥ 20m, với m là số thuật toán khóa song song (m ≤ 3, nên ngưỡng là 60). Cơ sở là bất đẳng thức Ville: được xem kết quả mọi lúc, dừng mọi lúc.
- **So với mốc tần suất 90 kỳ:** dùng e-process trên hiệu số nháy giữa thuật toán và mốc, Y_t = X_alg − X_hot90 ∈ [−27, 27], với μ = 0. Gọi `eprocess_mean(Y, 0, lambdas=(0,002; 0,005; 0,01; 0,02; 0,035), y_min=−27)`; λ phải ≤ 1/27. Chỉ được đọc kết quả này sau khi chỉ số chính đã bác bỏ H0.
- **Kiểm tra bằng mô phỏng:**
  - khi H0 đúng: báo nhầm ≤ 5%;
  - lợi thế +20% số nháy: trung vị 184 kỳ để phát hiện;
  - lợi thế +10%: khoảng 630 kỳ;
  - lợi thế vừa đủ hòa vốn: khoảng 3.100 kỳ.
- **Khi chưa bác bỏ H0**, chỉ được báo cáo: "không phát hiện lợi thế ≥ MDE tương ứng với số kỳ đã chấm" (tra bảng §2). Không được viết "không có lợi thế".

## 4. Phân bổ alpha

| Họ giả thuyết | Kiểm soát | Ghi chú |
|---|---|---|
| Xác nhận tương lai F1/F2/F3 | α tổng = 0,05; e-process với ngưỡng 20m | Mỗi nhánh tối đa 1 thuật toán khóa |
| WP2 (bộ phân biệt) | Holm, α = 0,05, tối đa 20 phép thử đăng ký trước | Đây là **cổng điều kiện**, không phải tuyên bố dự báo. Nếu WP2 bác bỏ H0, rà lỗi dữ liệu (WP0) trước |
| Hồi cứu F1/F2/F3 (≤ 500 ứng viên/nhánh, ≤ 1.500 tổng) | Không tiêu alpha | Chỉ mô tả và chọn ứng viên. Ghi đủ vào ledger |

**Mốc so sánh cho F3** là random-5 chính xác theo u của từng kỳ. Không dùng một lần bốc ngẫu nhiên làm mốc.

## 5. Cổng G2: kiểm thử bắt buộc

1. **Chống rò rỉ: `leakage_check` với 2 phép thử, trên ≥ 50 giá trị t, chạy cho toàn bộ pipeline** (đặc trưng, tinh chỉnh, hiệu chuẩn, ensemble):
   - (a) thay mọi kỳ ≥ t bằng dữ liệu giả, dự báo kỳ t phải giữ nguyên;
   - (b) cắt bỏ hẳn các kỳ ≥ t, dự báo kỳ t phải giữ nguyên. Phép này bắt lỗi L1 do Claude Code phát hiện.
2. **Kiểm tra dữ liệu đầu vào:** `load_draws(strict_lengths=True)`. Hàm từ chối hàng giả, ô trống làm lệch cột, và giải sai số chữ số.
3. **Đặc trưng khoảng cách tính theo số kỳ**, không theo ngày lịch (lỗi L2). Nếu cần, ngày lịch chỉ được dùng làm đặc trưng phụ.
4. **Đối chứng:** đối chứng âm (dữ liệu iid) và đối chứng dương (cài tín hiệu biết trước ở mức 2, 5, 10, 20%) cho mỗi nhánh.

## 6. Tiêu chí chứng nhận kết quả bộ giải (F1/F2) [X]

Giữ nguyên 6 tiêu chí của v1.0, mục 4:

1. Ngữ pháp G, kích thước s và **số luật |G_s| đếm chính xác** đều khóa trước.
2. Ngưỡng τ_s là phân vị 95% của điểm luật tốt nhất trên **≥ 1.000** bộ dữ liệu giả lập theo H0.
3. UNSAT phải kèm chứng minh **DRAT/LRAT đã được kiểm**. Kết quả OPTIMAL hoặc UNSAT của Z3/CP-SAT không có chứng minh chỉ được nhãn [C]. TIMEOUT thì không có kết luận.
4. Báo cáo lợi thế nhỏ nhất phát hiện được, đo bằng tín hiệu cài sẵn.
5. Đối chứng với tìm kiếm ngẫu nhiên và tham lam cùng ngân sách, và với vét cạn khi s ≤ 3.
6. Phát biểu chứng nhận âm đúng phạm vi: "không có luật nào trong G_s vượt τ_s trên đoạn D".

**Cơ sở:** định lý T3 (THEORY_REVIEW). Duyệt 10⁹ luật trên 4 năm dữ liệu thì "luật tốt nhất" sẽ trông như hơn ngẫu nhiên khoảng 9 điểm %, dù H0 đúng.

Trân trọng,
**Claude** (KTST), đồng tác giả Claude Code
