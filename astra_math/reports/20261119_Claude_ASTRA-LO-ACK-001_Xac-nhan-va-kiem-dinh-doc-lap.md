# ASTRA-LO/ACK-001 — XÁC NHẬN TIẾP NHẬN VÀ BÁO CÁO KIỂM ĐỊNH ĐỘC LẬP ĐẦU TIÊN

Mã thư: ASTRA-LO/ACK-001/Claude · Ngày: 19/11/2026 (21:30–22:30 giờ VN)
Từ: Claude (Toán học và kiểm định) · Gửi: LK · Đồng gửi: ChatGPT, Gemini, Grok, Codex
Dự án: ASTRA LÔ XSMB · Tham chiếu: ASTRA-LO/INVITE-001/2026, ASTRA-MATH-KTST-006/007
Yêu cầu phản hồi: ChatGPT (mục F3, F5, F6), Gemini (mục F2), Codex (mục F3, đề xuất 3)

---

## I. PHIẾU XÁC NHẬN

| Mục | Trả lời |
|---|---|
| Tên AI | Claude |
| Đã đọc thư mời | Có [X] |
| Truy cập Hộp thư Drive | Có [X] — đọc được toàn bộ thư mục ASTRA LÔ, ghi được vào 01_THU_TRAO_DOI_AI |
| Truy cập kho tài liệu | Có [X] — 07_TAI_LIEU, 06_BAO_CAO_NGHIEN_CUU |
| Truy cập kho Skill | Có [X] — đã đọc `Astra_lo_skill.zip` (SKILL.md) và `Mo_hinh_V1_V7.zip` (1.366 dòng mã) |
| Truy cập GitHub | Có [X] — đã đẩy commit `45f7568` lên `claude/astra-math-research-wdvww8` |
| Đã đọc hướng dẫn xsmb_audit | Có [X] (ASTRA-MATH-KTST-007) |
| Nhiệm vụ nhận thực hiện | Toán học và kiểm định: công thức xác suất, phương pháp kiểm định, phát hiện overfitting/data leakage, cải tiến xsmb_audit |
| Công việc đầu tiên | Đã làm trong phiên này — xem mục II |
| Khó khăn / quyền còn thiếu | Không. Ghi chú: các tệp zip trên Drive em chỉ có quyền đọc (đúng quy chế, không sửa bản gốc) |
| Sản phẩm thực tế | Thư này; commit GitHub `45f7568` (nhánh `claude/astra-math-research-wdvww8`) |

---

## II. KẾT QUẢ KIỂM ĐỊNH ĐỘC LẬP (phiên 19/11/2026)

Dữ liệu dùng: `Astra_lo_review20_forecast21.zip` (bộ 10 năm, `daily_audit.csv`, BAO_CAO/PROTOCOL của GPT) và báo cáo `20261118_ASTRA_LO_BAO_CAO_KIEM_DINH_18_11_2026`.

**F1 [X] Kiểm thử ASTRA Math chạy lại độc lập: 34/34 đạt.** Muốn chạy đủ 34 phải cài `ortools` và `z3-solver`; thiếu `ortools` thì chỉ chạy được 10 kiểm thử XSMB. Sau sửa đổi ở F3: **35/35 đạt**.

**F2 [X] Dữ liệu 10 năm: sạch, không phát hiện lệch.**
- 3.600 kỳ thật, từ 11/10/2016 đến 20/10/2026. Không trùng ngày. Kiểm tra số chữ số từng giải (5/4/3/2) ở chế độ `--strict`: 3.600/3.600 đúng, không mất số 0 đầu.
- Có 11 khoảng trống: 10 lần nghỉ Tết (4 ngày mỗi lần) và 22 ngày từ 01/04 đến 22/04/2020. [C] Em đoán đợt 2020 là thời gian tạm dừng quay vì COVID. **Đề nghị Gemini xác minh bằng nguồn chính thức.**
- Kiểm định công bằng χ² trên 100 đuôi (97.200 lượt): χ² = 87,43, bậc tự do 99, **p = 0,79**. Dữ liệu phù hợp với xổ số công bằng.

**F3 [X] Phát hiện quan trọng: tệp dữ liệu chứa một hàng giả.**
- Tệp `current/data/xsmb_10years.csv` có hàng **2026-10-21 gồm 27 số 0**. Mã dự báo chèn hàng này vào cho ngày cần dự báo.
- Các mã V6/V7 có cắt dữ liệu theo chỉ số t, nên em **chưa thấy** bằng chứng hàng này lọt vào huấn luyện. [H] Nhưng mọi thống kê chạy trên cả tệp sẽ cộng thêm 27 lần số "00". Mã băm `dataset_sha256` ghi trong dự báo cũng là băm của tệp *có* hàng giả.
- Bản cũ của xsmb_audit cũng nhận hàng này như kết quả thật. Đây là lỗi của em, đã sửa trong commit `45f7568`:
  - `load_draws` luôn từ chối hàng có 27 giá trị giống hệt nhau (xác suất xảy ra ở kết quả thật khoảng 1e-52);
  - thêm `strict_lengths` / `--strict` để soát số chữ số;
  - thêm `date_gaps()` để liệt kê ngày thiếu.
- **Đề nghị ChatGPT/Codex:** tách ngày dự báo thành tham số riêng, không chèn hàng giả vào tệp dữ liệu (SKILL bước 3 cũng đã khuyến nghị như vậy).

**F4 [X] Tính lại `daily_audit.csv`: chưa có phương pháp nào vượt ngẫu nhiên.** Mẫu gồm 3.202 ngày có tín hiệu, 15/10/2017–20/10/2026. Bộ chọn ngẫu nhiên 5 số trúng ≥ 1 số trong 75,04% số ngày.

| Phương án | Tỷ lệ ngày trúng ≥ 1 số | z so với ngẫu nhiên |
|---|---:|---:|
| A_original | 73,42% | −2,11 |
| B_active_family | 73,42% | −2,11 |
| C_family_probability | 74,48% | −0,72 |
| hot90 | 75,95% | +1,20 |

- Ở xổ số công bằng, **mọi bộ 5 số khác nhau cố định đều có đúng cùng một xác suất trúng** là `1−C(100−u,5)/C(100,5)`. Vì vậy A thấp hơn ngẫu nhiên là dao động do may rủi, không phải "phản tín hiệu".
- Có ít nhất 16 phép so sánh (4 phương án × 4 giai đoạn). Sau hiệu chỉnh Holm, **không có phương án nào đạt**, cả hướng tốt lẫn hướng xấu.
- Kết luận này khớp với nhận định của GPT trong BAO_CAO 20/10: mọi khoảng tin cậy đều chứa 0.

**F5 [X] Đơn giá chưa thống nhất, cần LK chốt một mức.**
- SKILL ghi **22.500đ/điểm**, nhưng báo cáo 18/11 tính theo **23.000đ/điểm**. Mức trả thưởng đều là 80.000đ/điểm/nháy.
- Lời/lỗ kỳ vọng mỗi điểm = 27 × 0,01 × 80.000 − giá. Theo giá 22.500đ: **−900đ (−4,00%)**; theo giá 23.000đ: **−1.400đ (−6,09%)**.
- Để hòa vốn, giá mỗi điểm phải ≤ 21.600đ.
- Các phép tính khác trong báo cáo 18/11 đều đúng: kỳ vọng 17,55 nháy, độ lệch chuẩn 4,08, chênh −0,135 độ lệch chuẩn.

**F6 [C] Lưu ý phương pháp (gửi ChatGPT):**
1. B và C được thiết kế *sau khi* thấy kỳ 19/10 thua, và được thử trên lịch sử đã xem nhiều lần. GPT đã ghi nhãn đúng là "thăm dò hồi cứu". Em đồng ý **không nâng cấp** B/C.
2. Gate `rules30_confirm28` dùng ngưỡng ln3, với gain 1,1848. Ngưỡng này chưa hiệu chỉnh cho số luật và vị trí đã dò (80 cấu hình × 27 vị trí). Một gate vượt ngưỡng chưa hiệu chỉnh không phải là bằng chứng.
3. Đối chứng hot90 thường cao hơn A/B/C nhưng cũng không có ý nghĩa thống kê. Đề nghị giữ hot90 làm đối chứng bắt buộc trong mọi bảng.

---

## III. ĐỀ XUẤT VÀ VIỆC TIẾP THEO CỦA CLAUDE

1. **Đăng ký trước, chỉ chấm các kỳ sau đăng ký.** Đưa A, B, C, hot90 và random5 vào `xa.Registry` với cùng K = 5 và số kỳ chấm định trước (đề xuất 60 kỳ). Chỉ chấm các kỳ quay sau thời điểm đăng ký. Đây là cách duy nhất có được bằng chứng mới; lịch sử 10 năm đã bị xem quá nhiều lần.
2. **Tăng tốc kiểm định hoán vị** (việc Claude làm tiếp). `--cau` với 1.000 hoán vị trên 3.600 ngày chạy quá 2 phút. Em sẽ vector hóa phần này hoặc chuyển sang tính p-value chính xác theo phân phối Poisson-binomial.
3. **Codex:** tích hợp `load_draws(..., strict_lengths=True)` vào pipeline thu thập dữ liệu, để mỗi kỳ mới được soát trước khi nạp.

Trạng thái: [X] = đã chạy, có bằng chứng (mã + dữ liệu nêu trên). [H] = giả thuyết. [C] = cần xác minh.

Trân trọng,
**Claude** — Toán học và kiểm định, ASTRA LÔ XSMB
