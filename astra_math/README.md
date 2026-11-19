# ASTRA Math — bộ công cụ ứng dụng (v0.1.0, 19/11/2026)

Khai thác **kỹ thuật** của các kết quả bác bỏ ETH (đếm chính xác bằng co mạng tensor) và
**bộ công cụ** cùng hệ sinh thái (CP-SAT, Z3), áp dụng cho các dự án ASTRA.
Không module nào dựa vào thuật toán bác bỏ ETH chạy nhanh trong thực tế: theo phân tích của
Dias & Lima (arXiv 2611.00517), thuật toán đó chỉ thắng vét cạn ở kích thước không thể viết ra.

| Module | Tầng | Dùng cho | Làm gì |
|---|---|---|---|
| `wmc.py` | T2 | OMNIVERSE, INVENTOR, STOCK | Đếm/tính xác suất chính xác các kịch bản thỏa ràng buộc logic (#SAT có trọng số) bằng co tensor; số nguyên/phân số chính xác |
| `tail_risk.py` | T2 | ASTRA STOCK | P(≥k mã cùng giảm), phân phối lỗ, VaR/ES 99% **chính xác** trong mô hình thị trường→ngành→mã; phân rã nguyên nhân |
| `portfolio.py` | T3 | ASTRA STOCK | Tối ưu danh mục CP-SAT: lô 100, phí cố định + tỷ lệ, thanh khoản ADV20, trần ngành, cặp tương quan, tái cân bằng; kèm baseline tham lam và bộ kiểm tra độc lập |
| `hose_order.py` | T3 | ASTRA STOCK (bot) | Lưới an toàn lệnh: bước giá, lô, trần/sàn, hạn mức. **Đã chứng minh bằng Z3** cho mọi giá/ngân sách (`proofs/hose_order_z3.py`) |
| `scheduler.py` | T3 | Web ASTRA / điều phối AI | Xếp việc tối ưu cho nhóm AI: phụ thuộc, năng lực, cấm xung đột lợi ích, hạn chót |
| `xsmb_audit.py` | T2/T3 | ASTRA LÔ XSMB | Xác suất chính xác (lô, xiên, đề, nháy), hòa vốn, p-value nhị thức, Holm/BH/Šidák, chấm cầu walk-forward + hoán vị, kiểm tra công bằng χ², sổ đăng ký trước SHA-256. **Không dự đoán** |

## Cài và chạy

```bash
pip install ortools z3-solver numpy pytest
python3 -m pytest astra_math/tests -q          # 34 kiểm thử: so với vét cạn, Z3, ràng buộc
python3 -m astra_math.proofs.hose_order_z3     # in kết quả chứng minh
python3 -m astra_math.demo_stock               # quy trình đầu-cuối ASTRA STOCK
python3 -m astra_math.xsmb_audit --demo        # ASTRA LÔ XSMB: xác suất & kiểm định
python3 -m astra_math.xsmb_audit --csv ket_qua.csv --cau
```

## Kết quả quy trình mẫu (`demo_stock`, dữ liệu minh họa 30 mã)

- Tối ưu CP-SAT: OPTIMAL trong 0,02 giây; lợi nhuận kỳ vọng ròng **+5,5%** so với tham lam (cùng ràng buộc, 0 vi phạm).
- 4 lệnh mua đều qua lưới an toàn; lệnh lỗi mẫu (giá 50.050, KL 307) bị chặn với lý do cụ thể.
- Stress test: P(≥3 mã cùng giảm sâu) = 0,1435%, trong đó 97,5% đến từ nhánh sốc thị trường;
  P(cả 4 mã) = 8,3·10⁻⁵ (Monte Carlo 20.000 mẫu ra 0); VaR99 = 18 triệu, ES99 = 21,4 triệu đồng. Tính trong 0,4 ms.

## Giới hạn (bắt buộc đọc)

- Đầu vào minh họa: giá chưa ghi ngày/nguồn; `alpha` và xác suất giảm là **giả định**.
  Trước khi dùng thật: ước lượng tham số từ dữ liệu có ngày tháng, backtest walk-forward ngoài mẫu.
- Tối ưu không tạo ra alpha; nó chỉ phân bổ tốt nhất theo dự báo đưa vào.
- `tail_risk` chính xác **trong mô hình**; mô hình sai thì kết quả sai. Đếm chính xác chỉ nhanh khi phụ thuộc có cấu trúc (độ rộng nhỏ).
- Quy tắc HOSE trong `hose_order.py` là đặc tả giả định, cần đối chiếu văn bản hiện hành; chưa gồm lệnh bán đặc biệt, ATO/ATC, mã biên độ riêng.
- Không đưa dữ liệu cá nhân hoặc dữ liệu nghiệp vụ BHXH vào thư mục này (repo có thể công khai).
