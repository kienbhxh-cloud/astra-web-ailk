# PREREG_STATISTICS — Xác suất chính xác, lực thống kê, phân bổ alpha

- Gói việc: PNP-MASTER-005 / WP2 + WP4 (phần thống kê) · Phiên bản 1.1 (giá 22.500đ đã chốt) (DRAFT, chờ ChatGPT khóa vào PROTOCOL_MASTER) · 20/11/2026
- Tác giả: Claude (Claude Code)
- Mã nguồn: `astra_math/xsmb_audit.py`, mục 5b–5d. Kiểm thử: `astra_math/tests/test_xsmb_audit.py` (17/17 đạt [X])
- Tái lập: `PYTHONPATH=. python3 PNP_XSMB_RESEARCH/power_analysis.py ket_qua_10nam.csv`

## 1. Xác suất chính xác [X]

Giả thuyết gốc (H0): 27 giải độc lập, 2 số cuối mỗi giải đều trên 00–99. Các con số dưới đây tính bằng phân số chính xác, không dùng mô phỏng.

| Đại lượng | Công thức | Giá trị |
|---|---|---|
| 1 số về ≥ 1 nháy | 1 − 0,99²⁷ | 23,7657% |
| Bộ 5 số cố định có ≥ 1 số về | 1 − 0,95²⁷ | 74,9656% |
| Phân phối số đuôi khác nhau u trong 1 kỳ | C(100,u)·u!·S(27,u)/100²⁷ (S là số Stirling loại 2) | E[u] = 23,7657; P(u = 23) = 21,46% |
| Mốc random-5 trên dữ liệu thật (dùng u của từng kỳ) | trung bình của 1 − C(100−u,5)/C(100,5) | 75,0539% trên 3.629 kỳ (2016–2026). Báo cáo V7: 75,0114% trên 1.724 kỳ |
| Đồng nhất thức kiểm tra | Σ_u P(u)·[1 − C(100−u,5)/C(100,5)] = 1 − 0,95²⁷ | đúng tuyệt đối (bằng Fraction) |
| **Giá mô phỏng đã chốt** | LK quyết định ngày 20/11/2026 | **22.500đ/điểm**, trả 80.000đ/điểm/nháy |
| Lãi/lỗ kỳ vọng mỗi điểm | 80.000 × 0,27 − 22.500 | −900đ (ROI −4,00%) |
| Bộ 5 số × 5 điểm: chi / kỳ vọng / độ lệch chuẩn mỗi kỳ | chi 562.500; lãi = 400.000·X − 562.500, với X ~ Nhị thức(27; 0,05) | chi 562.500đ; kỳ vọng −22.500đ/kỳ; độ lệch chuẩn ≈ 453.000đ/kỳ |
| Hòa vốn | 562.500 / 400.000 | 1,40625 nháy/kỳ = mỗi số 5,208% (cao hơn ngẫu nhiên 4,17%) |
| (Tham khảo, không dùng) giá cũ 23.000đ | 575.000 / 400.000 | 1,4375 nháy/kỳ; −35.000đ/kỳ; ROI −6,09% |

**Lưu ý cho F3:** tỷ lệ kỳ trúng ≥ 1 số **không** quyết định lời/lỗ. Tiền phụ thuộc vào tổng số nháy. Một bộ số có thể tăng tỷ lệ kỳ trúng mà giảm tổng số nháy (ví dụ chọn 5 số "ít trùng nhau"). Vì vậy, F3 bắt buộc báo cáo kèm tổng nháy/kỳ.

## 2. Lực thống kê (power) cho xác nhận tương lai [X]

**F3 (tỷ lệ kỳ trúng ≥ 1 của bộ 5).** Kiểm định nhị thức chính xác một phía; α = 0,05/6 (Bonferroni cho 6 so sánh chính); power 80%.

| Số kỳ tương lai | Tỷ lệ thật nhỏ nhất phát hiện được | Mức tăng so với 74,97% |
|---|---|---|
| 60 | 92,0% | +17,1 điểm % |
| **180** | **84,7%** | **+9,8 điểm %** |
| 365 | 82,1% | +7,1 điểm % |
| 1.000 | 79,3% | +4,4 điểm % |

Số kỳ cần có để phát hiện một mức tăng cho trước:

| Mức tăng | Số kỳ cần | Tương đương |
|---|---|---|
| +5 điểm % | 754 kỳ | ~2,1 năm |
| +2 điểm % | 4.835 kỳ | ~13 năm |
| +1 điểm % (ngưỡng Codex đề xuất) | **19.570 kỳ** | **~54 năm** |

**F1/F2 (Brier của 100 biến hiện diện).** Mô phỏng 400 lần × 180 kỳ. Giả định một mô hình "biết đúng" độ lệch thật ±δ của mọi số so với p0 = 0,2377.

| δ (độ lệch xác suất thật) | Mức cải thiện Brier | Số kỳ cần để đạt power 80% |
|---|---|---|
| 0,005 | 0,000025 | ~2.780 |
| 0,010 | 0,000100 | ~726 |
| 0,022 | 0,00049 (≈ ngưỡng Codex 0,0005) | ~147 |

Mức cải thiện Brier tối đa có thể đạt ≈ δ² trung bình (đã kiểm bằng mô phỏng).

Ngưỡng 0,0005 của Codex đòi **mọi** số lệch ±0,022 so với p0, tức khoảng ±9% tương đối.

Một độ lệch **cố định** như vậy đã bị loại trừ trên dữ liệu 10 năm:
- sai số chuẩn của tỷ lệ hiện diện mỗi số qua 3.629 kỳ ≈ 0,0071, nên δ = 0,022 ≈ 3,1 SE cho từng số;
- trong khi đó kiểm định χ² trên dữ liệu 10 năm cho p = 0,79.

Chỉ có độ lệch **thay đổi theo thời gian** mới còn khả năng chưa bị loại trừ.

**Kết luận và đề xuất khóa:**
1. 180 kỳ chỉ đủ phát hiện các lợi thế **rất lớn** (F3 cao hơn khoảng 10 điểm %, F1 cần δ ≈ 0,022). Báo cáo cuối phải ghi rõ điều này. Nếu 180 kỳ không đạt, được kết luận "không phát hiện lợi thế ≥ mức tối thiểu phát hiện được", **không** được kết luận "không có lợi thế".
2. Đề nghị ChatGPT chọn một trong hai cách cho PROTOCOL_MASTER:
   - **(a)** giữ 180 kỳ và ghi rõ mức tối thiểu phát hiện được (MDE) như bảng trên;
   - **(b)** dùng **kiểm định tuần tự** (SPRT, hoặc chi tiêu alpha kiểu O'Brien–Fleming với 4 lần xem tại kỳ 180/365/730/1.095). Cách này cho phép dừng sớm khi có tín hiệu lớn, nhưng vẫn giữ đúng α.
3. Ngưỡng F3 "+1 điểm %" của Codex **không tương thích** với 180 kỳ (cần 19.570 kỳ). Đề nghị bỏ ngưỡng này, hoặc gắn nó với MDE.

## 3. Phân bổ alpha toàn chương trình

- **Họ giả thuyết chính:** 6 so sánh (F1, F2, F3, mỗi nhánh với 2 mốc). Dùng Holm với α = 0,05.
- **WP2 (bộ phân biệt):** họ riêng với α = 0,05, Holm trên tối đa 20 phép thử đã đăng ký trước. Kết quả WP2 là **cổng điều kiện**, không phải tuyên bố dự báo.
- **F1/F2 hồi cứu:** không tính p-value xác nhận. Chỉ báo cáo mô tả, kèm số ứng viên đã chấm (≤ 500/nhánh, ghi vào ledger).
- **Mốc so sánh bắt buộc cho F3:** random-5 chính xác theo u của từng kỳ (§1). **Không** dùng một lần bốc thăm ngẫu nhiên làm mốc.
- **Khoảng tin cậy:** bootstrap khối 14 kỳ chỉ dùng cho chỉ số phụ. Chỉ số chính dùng kiểm định chính xác (nhị thức) hoặc kiểm định hoán vị trên nguyên ngày.

## 4. Cổng G2: kiểm thử bắt buộc trước khi khóa

1. `leakage_check`: thay mọi kỳ ≥ t bằng dữ liệu giả; dự báo kỳ t phải giữ nguyên. Chạy trên ≥ 50 giá trị t ngẫu nhiên cho **toàn bộ** pipeline. [X] Hàm đã cài đặt, và kiểm thử cho thấy hàm bắt được cả lỗi dùng trực tiếp kỳ t lẫn lỗi dùng tần suất của toàn bộ dữ liệu.
2. Đối chứng âm (dữ liệu iid) và đối chứng dương (cài tín hiệu biết trước) cho mỗi nhánh F1–F3.
3. Dữ liệu (cổng G0) [X], Claude kiểm chéo:
   - CSV của Codex có SHA-256 `07e110ac…5b78`, khớp với thư Codex.
   - 7.618 kỳ chung với bản Claude tải độc lập (khiemdoan, SHA-256 `17495661…82e0`) **khớp 100%** cả 27 giải.
   - Codex có thêm 4 kỳ: 2009-06-09, 2011-04-26, 2011-04-27, 2026-11-19. Gemini cần xác minh nguồn của 3 kỳ lịch sử.
