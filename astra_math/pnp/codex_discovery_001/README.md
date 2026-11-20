# ASTRA DISCOVERY 001 — APDE 0.1 (20/11/2026)

Bàn giao thực tế: engine.py, PROTOCOL.json, tests, 30 ứng viên hồi cứu, 12 stress runs, nguồn cũ được bảo tồn và registry. Không là bộ dự đoán đã có lợi thế; không phải toàn bộ chương trình A–I đã hoàn thành.

Python 3.12.14. Cài môi trường riêng: `python -m pip install -r requirements.txt`. Engine chỉ cần numpy; z3 dùng cho bộ kiểm thử PNP trong 05_PNP_SOURCE.

Chạy từ thư mục gói:

```sh
python -m unittest discover -s . -p test_engine.py -v
python engine.py --csv 01_ARCHIVE/1yPT3W8am6MxHffqb35XDYelB6_WZ8l49__xsmb_2005-10-01_to_2026-11-19_clean_v2_fix20060921.csv --protocol PROTOCOL.json --out replay_new
python gemini_cli_bridge.py --self-test
```

Không ghi đè 02_RUN_001. Run mới giữ tên khác. Khi chạy run_controls.py, mặc định từ chối nếu 04_CONTROLS đã có FREEZE; dùng API run(Path('new_controls')) để tái lập sang thư mục khác. Không đổi seed chỉ để có kết quả đẹp.

02_RUN_001 chứa FREEZE trước thực nghiệm, SELECTED_BEFORE_EVALUATION, ledger đầy đủ, bảng so sánh, kết quả JSON và dự báo hồi cứu NPZ. Tệp NPZ không là dự báo đã khóa trước giờ quay trong thực tế. 04_CONTROLS lưu mọi hệ số/selection loss cho 360 lần fit bổ sung. Tổng lần fit ứng viên mới: 390 (30 lịch sử +360 kiểm thử stress), không tính fit baseline như một công thức phát hiện mới.

MODEL_REGISTER.json có 101 đơn vị nguồn/nhóm và nguyên mã của 120 hàm/lớp, gồm tiện ích; không phải 101/120 mô hình độc lập. Đã lưu ZIP V1–V7, Skill v2, 003–007,009–011 tìm được; Đã tìm thấy LOCK-008 trong thư mục dự báo khóa và bảo tồn mã/JSON/README; chưa kiểm chứng độc lập thời điểm khóa. Hai ZIP AUDIT-007 khác nhau được giữ riêng. Một số model cũ không có đủ tham số/nguồn/đánh giá; registry giữ trạng thái chưa tái lập.

Giới hạn: nguồn sửa dữ liệu dựa vào source register dự án, chưa tự chụp lại cả hai website gốc trong phiên này; CI/p-value bootstrap là xấp xỉ và chỉ hiệu chỉnh trong họ mới; lịch sử toàn bộ đã từng được xem. Không có tuyên bố đạt G2/G3 toàn chương trình. Xem REPORT.md, ARCHITECTURE.md và ISSUES.md.
