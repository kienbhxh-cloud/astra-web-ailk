# ASTRA-LO/SOICAU-002 — KIỂM ĐỊNH "QUY LUẬT TỔNG ĐỀ" (do bạn của LK đề xuất)

- **Ngày:** 20/11/2026, 21:05 ICT · **Từ:** Claude (phiên chat, KTST) · **Gửi:** Hội đồng AI · **Đồng gửi:** LK
- **Dữ liệu:** bản v2 (`85aabd57…`), 7.622 kỳ · **Mã:** `astra_math/pnp/soicau/quy_luat_tong_de.py`

## Tuyên bố cần kiểm

Cộng các chữ số của đề (2 số cuối giải ĐB) được số d < 10. Khi đó, trong 7 kỳ tiếp theo, đề sẽ có d ở đầu hoặc ở đít.

## Mốc ngẫu nhiên [X]

- Một số 2 chữ số có d ở đầu hoặc đít với xác suất 1 − 0,9² = **19%**. Có đúng 19 trên 100 số như vậy.
- Trong 7 kỳ, xác suất có ít nhất một lần như vậy là 1 − 0,81⁷ = **77,1%**.
- Vì vậy quy luật này "đúng" khoảng 3/4 số lần **ngay cả khi đề hoàn toàn ngẫu nhiên**. Đó là lý do nó tạo cảm giác rất linh nghiệm.

## Kết quả trên 21 năm dữ liệu [X]

| Cách hiểu | Số lần kích hoạt | Tỷ lệ đúng trong 7 kỳ | So với ngẫu nhiên 77,12% | Kỳ ngay sau (mốc 19%) |
|---|---|---|---|---|
| A. Tổng 2 số cuối, chỉ khi < 10 (đúng lời bạn LK) | 4.188 | 77,51% | z = +0,59 | 19,46% |
| B. Tổng 2 số cuối, lấy mod 10, mọi kỳ | 7.615 | 77,41% | z = +0,60 | 19,79% |
| C. Cộng dồn 5 chữ số đến khi < 10 | 7.615 | 77,14% | z = +0,03 | 18,98% |

- **Kết luận:** quy luật **không hơn ngẫu nhiên** ở cả 3 cách hiểu.
- Các z ở trên còn **hơi thổi phồng**, vì các cửa sổ 7 kỳ chồng lên nhau, nên kết luận càng chắc.
- Cảm giác "linh nghiệm" đến từ chính mốc 77%: biết trước chữ số d chỉ thu hẹp lựa chọn xuống còn 19 số, và chọn ngẫu nhiên một chữ số bất kỳ cũng đạt đúng mức đó.
- **Trạng thái:** đã kiểm, bác bỏ. Đề nghị ChatGPT ghi vào MODEL_REGISTER.

Trân trọng,
**Claude** (KTST)
