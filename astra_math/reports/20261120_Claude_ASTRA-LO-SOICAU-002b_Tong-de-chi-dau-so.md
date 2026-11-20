# ASTRA-LO/SOICAU-002b — Bổ sung: "thường là ĐẦU số" (LK làm rõ lúc 20:59 ngày 20/11/2026)

- **Mã:** `astra_math/pnp/soicau/quy_luat_tong_de_dau.py` · **Dữ liệu:** bản v2, 7.622 kỳ.
- **Mốc ngẫu nhiên:** một chữ số d nằm ở đầu đề với xác suất 10% mỗi kỳ. Trong 7 kỳ: 1 − 0,9⁷ = **52,17%**.

| Cách hiểu | Đầu số | Đít số |
|---|---|---|
| A. Tổng 2 số cuối < 10 (đúng lời bạn LK) | **52,24%** (z = +0,10) | 52,39% (z = +0,28) |
| B. Tổng 2 số cuối mod 10 | 53,08% (z = +1,59) | 52,03% (z = −0,25) |
| C. Cộng dồn 5 chữ số | 51,63% (z = −0,94) | 53,38% (z = +2,12) |

**Kết luận:**
- Đúng lời bạn LK (cách A, đầu số): **52,24% so với 52,17% nếu chọn ngẫu nhiên. Không có tác dụng.**
- Giá trị z lớn nhất (+2,12) là ở cách C, lại rơi vào **đít số** chứ không phải đầu số.
- Có 6 phép thử, và các cửa sổ 7 kỳ chồng lên nhau làm z bị thổi phồng. Sau hiệu chỉnh Holm, **không phép nào đạt**.
- **Trạng thái:** đã kiểm, bác bỏ.

**Claude** (KTST)
