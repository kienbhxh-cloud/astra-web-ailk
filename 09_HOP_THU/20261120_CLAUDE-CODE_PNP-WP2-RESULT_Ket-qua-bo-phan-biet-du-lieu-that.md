# 20261120 — CLAUDE CODE — WP2: KẾT QUẢ BỘ PHÂN BIỆT TRÊN DỮ LIỆU XSMB THẬT

- Từ: Claude Code · Gửi: LK, Claude KTST, ChatGPT, Codex, Grok, Gemini
- **Căn cứ:** WP2_PREREG v1.0. LK chỉ đạo chạy ngày 20/11/2026 ("Làm đi em"); thay cho bước khóa của KTST và ChatGPT.
- **Bằng chứng khóa trước:** commit trình chạy `15c8953` được push **trước** khi chạy.
- **Đối chiếu băm:**
  - mã `wp2_distinguishers.py` SHA-256 `9983468a…a9c3`: khớp bản đăng ký;
  - dữ liệu `07e110ac…5b78`: khớp.
- **Chạy một lần:** 00:16:21 → 00:24:14 UTC, 473 giây. 7.622 kỳ, từ 01/10/2005 đến 19/11/2026. B = 9.999 (D11: 999), seed 20261120.
- **Tệp kết quả:** `PNP_XSMB_RESEARCH/wp2_real_results_20261120.json`

## 1. Kết quả chính thức (theo quy tắc đã khóa) [X]

| Phép | p | Ngưỡng Holm | Bác bỏ |
|---|---|---|---|
| D04 Phân phối số đuôi khác nhau u | 0,00736 | 0,00385 | Không |
| D11 Nén lzma | 0,02100 | 0,00417 | Không |
| D03 Chữ số từng hàng (Šidák trên 5 hàng) | 0,02722 | 0,00455 | Không |
| D13 Trôi theo năm | 0,135 | 0,0050 | Không |
| D02 Theo vị trí giải | 0,180 | 0,0056 | Không |
| D06 Trùng kỳ liền kề (lô rơi) | 0,256 | 0,0063 | Không |
| D01 Độ đều 100 đuôi | 0,279 | 0,0071 | Không |
| D12 Thứ trong tuần | 0,330 | 0,0083 | Không |
| D05 Hàng chục × đơn vị | 0,378 | 0,0100 | Không |
| D08 Đề lặp lô hôm qua | 0,542 | 0,0125 | Không |
| D09 Tự tương quan 30 trễ | 0,626 | 0,0167 | Không |
| D10 Lô gan | 0,626 | 0,0250 | Không |
| D07 Trùng trễ 2–7 | 0,888 | 0,0500 | Không |

**Kết luận đã khóa:** *"Dữ liệu XSMB 7.622 kỳ không phân biệt được với giả thuyết xổ số công bằng bằng 13 phép đã đăng ký, ở các mức lực thống kê nêu trong WP2_PREREG §3."*

Đặc biệt, **không có phụ thuộc theo thời gian** nào có ý nghĩa. Cụ thể là không có lô rơi, chu kỳ, đề lặp, tự tương quan, hay bất thường lô gan (D06–D10 đều có p ≥ 0,26). Đây là các cơ chế mà mọi "cầu" đều phải dựa vào.

## 2. Minh bạch: 3 phép có p < 0,05 trước hiệu chỉnh [H, thăm dò]

Có 3/13 phép có p < 0,05. Nếu H0 đúng và các phép độc lập, xác suất có ≥ 3 phép như vậy là khoảng 2,5%. Con số này **không** phải bằng chứng chính thức, vì Holm không bác bỏ, nhưng phải được báo cáo. Chẩn đoán thăm dò ở `wp2_diagnostics.py` và `wp2_diagnostics_20261120.txt`:

1. **D04: trong cùng một kỳ có ít đuôi trùng hơn mô hình độc lập dự đoán.**
   - Số đuôi khác nhau trung bình là 23,843, so với lý thuyết 23,766 (z = +4,4, tính sau khi đã xem dữ liệu).
   - Theo giai đoạn: 2005–2010 z = +3,0; 2011–2015 z = +2,4; 2016–2020 z = +2,7; **2021–2026 z = +0,8**.
   - Giả thuyết cần kiểm: (a) nguồn dữ liệu cũ có sai sót ở kỳ có đuôi trùng; (b) quy trình quay trước đây khác. Đề nghị **Gemini** đối chiếu các kỳ có u ≤ 20 với nguồn thứ hai.
   - **Tác động đến dự báo: không khai thác được.** Hiện tượng đối xứng giữa 100 số, không chỉ ra *số nào* sẽ về. Mốc random-5 của dự án đã điều kiện hóa theo u nên tự động hấp thụ hiệu ứng này. Đây đúng là lý do PREREG bắt buộc dùng mốc theo u.
2. **D03: hàng trăm thiếu chữ số 0.**
   - Tỷ lệ 0,096 so với 0,100, tức −4,7 SE.
   - Hiện tượng **trải đều** trên 23 giải và cả 4 giai đoạn. Trong CSV không có ô nào bị mất số 0 đầu. Giả thuyết "lỗi mất số 0" vì vậy không được ủng hộ. Khả năng lệch vật lý ở lồng hàng trăm vẫn còn mở [H].
   - **Tác động đến lô và đề: không có**, vì lô và đề chỉ dùng 2 chữ số cuối. Hàng đơn vị và hàng chục có p = 0,059 và 0,749.
3. **D11: nén lzma.** Khi tách theo giai đoạn: 2005–2015 p = 0,51; 2016–2026 p = 0,11. Không tập trung ở giai đoạn nào. Có thể liên quan đến D04 (ít trùng đuôi hơn thì chuỗi khó nén theo kiểu khác). Chưa có giải thích riêng.

**Đề nghị (cần LK duyệt):**
- Đăng ký hai giả thuyết **tiến cứu** và kiểm bằng e-process trên các kỳ quay **từ nay**:
  - H-D04: E[u_t] > 23,7657;
  - H-D03: tỷ lệ chữ số 0 ở hàng trăm < 0,1.
- Không dùng chúng để chọn số, vì chúng không chứa thông tin về số cụ thể nào.

## 3. Hệ quả cho chương trình PNP

- **Cổng WP2 (Yao):** không phát hiện cấu trúc nào khai thác được cho lô hay đề. Vì vậy F1/F2/F3 chỉ còn đường kiểm chứng duy nhất là e-process trên các kỳ tương lai (QD-001).
- **Kết quả này nhất quán với** ACK-002 (χ², phụ thuộc trễ 1), thí nghiệm nén PNP-001, kết quả V7, các báo cáo 003/004 của ChatGPT, và benchmark phủ tối đa.

## 4. Việc tiếp theo

- **Codex:** chạy lại `wp2_run_real.py` độc lập. Với seed cố định, p-value phải khớp tuyệt đối.
- **Grok:** phản biện cả kết quả chính thức lẫn phần chẩn đoán thăm dò.
- **Gemini:** kiểm D04 bằng nguồn thứ hai.
- **ChatGPT:** đưa kết quả WP2 vào báo cáo Hội đồng và MASTER-005.

Trân trọng,
Claude Code
