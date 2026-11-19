# WP2_PREREG — Bộ phân biệt đăng ký trước (DRAFT v1.0, chờ KTST + ChatGPT khóa)

- Gói việc: PNP-MASTER-005 / WP2 (Claude Code + Codex) · 20/11/2026 · Tác giả: Claude Code
- Mã nguồn: `astra_math/wp2_distinguishers.py`, SHA-256 `9983468af4939b4982c2dd1a530dbc8e417d07879bdd160684b9d6398415a9c3`, cùng commit với tệp này.
- Kiểm thử: `astra_math/tests/test_wp2_distinguishers.py`. Toàn bộ `astra_math/tests` đạt **47/47**.
- **Trạng thái: CHƯA chạy trên dữ liệu XSMB thật.** Chỉ chạy **một lần** sau khi danh sách này được khóa.

## 1. Câu hỏi và giả thuyết

**Câu hỏi:** dữ liệu XSMB có phân biệt được với **H0** không? H0 phát biểu: 27 giải độc lập, mỗi chữ số của mỗi lồng đều trên 0–9, các ngày độc lập.

Theo Yao (1982), *không có bộ phân biệt hiệu quả ⇔ không có bộ dự báo hiệu quả*. WP2 vì vậy là **cổng điều kiện**:
- WP2 không bác bỏ H0 → mọi tuyên bố dự báo từ F1/F2/F3 phải được coi là [C], cho đến khi e-process tương lai chứng minh được.
- WP2 bác bỏ H0 → **trước hết** rà lỗi dữ liệu (WP0). Chỉ sau đó mới đăng ký một mô hình khai thác **đúng** cấu trúc đã tìm thấy, và kiểm chứng trên **tương lai** bằng e-process (QD-001).

## 2. Danh sách khóa: 13 phép, không thêm, không bớt

| Mã | Phép kiểm | Loại p-value | Phát hiện điều gì |
|---|---|---|---|
| D01 | χ² độ đều 100 đuôi, gộp 27 giải (df 99) | giải tích, hai phía | lệch tần suất chung |
| D02 | χ² 100 đuôi theo từng vị trí giải; Šidák min-p trên 27 phép | giải tích | lệch riêng một giải |
| D03 | χ² chữ số 0–9 theo từng hàng (đơn vị … chục nghìn); Šidák trên 5 phép | giải tích | **lệch vật lý một lồng cầu** |
| D04 | Phân phối số đuôi khác nhau u, so với phân phối chính xác C(100,u)·u!·S(27,u)/100²⁷ | giải tích | phụ thuộc giữa các giải trong cùng kỳ |
| D05 | Độc lập giữa hàng chục và hàng đơn vị (bảng 10×10, df 81) | giải tích | hai lồng liên quan nhau |
| D06 | Σ\|S_t ∩ S_{t−1}\| (trùng kỳ liền kề) | hoán vị ngày, hai phía | "lô rơi", lặp từ hôm qua |
| D07 | Σ_{k=2..7} Σ\|S_t ∩ S_{t−k}\| | hoán vị ngày, hai phía | chu kỳ ngắn |
| D08 | #{t: ĐB_t ∈ S_{t−1}} | hoán vị ngày, hai phía | cầu đề từ lô hôm qua |
| D09 | Q = Σ_{k=1..30}(Σ_i r_ik)², tự tương quan hiện diện | hoán vị ngày, một phía | phụ thuộc thời gian tổng quát |
| D10 | Phương sai độ dài khoảng gan | hoán vị ngày, hai phía | lô gan dài hoặc ngắn bất thường |
| D11 | Kích thước nén lzma theo thứ tự ngày | hoán vị ngày, một phía | cấu trúc tổng quát (cận trên Kolmogorov) |
| D12 | Bảng 100 đuôi × 7 thứ (df 594) | giải tích | hiệu ứng ngày trong tuần |
| D13 | Bảng 100 đuôi × năm | giải tích | trôi dần theo năm |

**Tham số khóa:**
- Holm với α = 0,05 trên **đúng 13** p-value.
- Số hoán vị: **B = 9.999** (D06–D10), **B = 999** (D11). Seed `20261120`.
- Dữ liệu: CSV `07e110ac…5b78`, cả **7.622 kỳ**, chỉ mục theo kỳ quay.
- Không bỏ phép nào, không đổi tham số sau khi xem kết quả.

**Quy tắc độ phân giải:** phải có 1/(B+1) ≪ α/13 = 0,0038. Lúc hiệu chỉnh với B = 99, mọi phép hoán vị đều **không thể** bị bác bỏ dù tín hiệu rất mạnh. Lỗi này được phát hiện và sửa trong chính quá trình hiệu chỉnh (§3). Có kiểm thử tự động `test_resolution_rule` để chặn lỗi tái diễn.

## 3. Hiệu chỉnh trên dữ liệu giả lập [X]

**Sai lầm loại I.**

Lần 1: 120 bộ dữ liệu H0 × 1.500 kỳ (B rút gọn).

| | D01 | D02 | D03 | D04 | D05 | D06 | D07 | D08 | D09 | D10 | D11 | D12 | D13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tỷ lệ p < 0,05 | 0,058 | 0,075 | 0,092 | 0,058 | 0,058 | 0,033 | 0,067 | 0,042 | 0,033 | 0,025 | 0,017 | 0,050 | 0,050 |

- **FWER sau Holm = 0,017 ≤ 0,05.** Đạt.
- Kiểm lại D01–D03 trên 1.000 bộ × 400 kỳ:
  - D03 = 0,051 (giá trị 0,092 ở lần 1 là nhiễu);
  - D01 = 0,047;
  - D02 = 0,051, nhưng ở mức p < 0,01 lên tới 0,019. Lý do: χ² xấp xỉ kém khi kỳ vọng mỗi ô chỉ khoảng 4. Trên 7.622 kỳ, kỳ vọng mỗi ô của D02 khoảng 76, nên vấn đề này không còn.

**Lực phát hiện tín hiệu cài sẵn** (1.500 kỳ, Holm trên 13 phép):

| Tín hiệu cài | Mức | Tỷ lệ Holm bắt được | Phép bắt được |
|---|---|---|---|
| Thứ Hai: ĐB đuôi 00 với xác suất 0,3 | — | 10/10 | D02 (10), D12 (2) |
| Lồng hàng đơn vị G7 lệch về "7" | q = 0,2 / 0,4 | 3/10 / 10/10 | D02, D03, D01 |
| Mỗi ngày 1 giải lặp đuôi hôm qua (B = 999) | q = 0,15 / 0,3 / 0,6 | 0/6 / 3/6 / 6/6 | D06, rồi D09, D10 |

**Đọc kết quả:** bộ phân biệt bắt được các lệch **vật lý cỡ vài %**, và phụ thuộc thời gian cỡ "0,3 lượt lặp mỗi kỳ" trên 1.500 kỳ. Dữ liệu thật có 7.622 kỳ, nên lực sẽ cao hơn. Các lệch nhỏ hơn mức này **không** phát hiện được. Báo cáo cuối phải ghi rõ giới hạn đó.

## 4. Quy tắc diễn giải (khóa)

1. Không phép nào bị bác bỏ → kết luận: *"Không phân biệt được với H0 bằng 13 phép đã đăng ký, ở các mức lực thống kê ở §3."* **Không** được kết luận "XSMB chắc chắn công bằng".
2. Có phép bị bác bỏ → rà theo thứ tự:
   - (a) lỗi dữ liệu: số 0 đầu, thứ tự giải, nguồn của 4 kỳ Codex bổ sung;
   - (b) thay đổi quy trình quay theo năm (D13);
   - (c) chỉ sau hai bước trên mới đăng ký giả thuyết dự báo mới, kiểm chứng trên tương lai bằng e-process.
3. Kết quả của WP2 **không** được dùng để chọn tham số cho F1/F2/F3 trên cùng dữ liệu. Làm vậy là chọn mô hình sau khi xem kết quả.

## 5. Cần duyệt

- **KTST:** duyệt danh sách và quy tắc diễn giải.
- **ChatGPT:** đưa vào PROTOCOL_MASTER với một họ α riêng.
- **Codex:** chạy lại độc lập trên máy khác, so p-value. Với seed đã cố định, kết quả phải khớp chính xác.
- **Grok:** thử phá. Ví dụ: tìm một tín hiệu đơn giản mà cả 13 phép đều bỏ sót.
