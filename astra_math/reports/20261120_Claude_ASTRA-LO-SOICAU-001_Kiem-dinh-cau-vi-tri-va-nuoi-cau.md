# ASTRA-LO/SOICAU-001 — KIỂM ĐỊNH CÁC PHƯƠNG PHÁP SOI CẦU DÂN GIAN TRÊN 7.622 KỲ THẬT

- **Ngày:** 20/11/2026, 21:10 ICT · **Từ:** Claude (phiên chat, KTST) · **Gửi:** Hội đồng AI · **Đồng gửi:** LK
- **Căn cứ:** LK gửi bản tóm tắt các phương pháp soi cầu phổ biến (nuôi cầu chạy đều khung 2–3 ngày, ghép cầu theo vị trí, thống kê vị trí/cầu tròn) lúc 20:49 ngày 20/11/2026.
- **Dữ liệu:** bản v2 (SHA-256 `85aabd57…27535909`), 7.622 kỳ.
- **Mã:** `astra_math/pnp/soicau/cau_vitri.py`, `cau_ngay.py`.
- **Nhãn:** thăm dò hồi cứu. Đây là kiểm định một **tuyên bố có sẵn**, không phải đi tìm luật mới.

## 1. Cầu vị trí ("ghép cầu") [X]

- **Cách tạo cầu:** bảng kết quả mỗi kỳ có 107 chữ số. Mỗi cầu là một cặp vị trí (i, j) có thứ tự; lấy chữ số thứ i và thứ j của kỳ t ghép thành một số. Có **11.342 cầu** (đúng cách các trang soi cầu vẫn làm).
- **Cầu "ăn"** khi số ghép được về ở kỳ t + 1.
- **Kiểm định đúng đơn vị:** 11.342 cầu trong cùng một ngày đều chấm theo cùng một kết quả, nên không độc lập. Vì vậy em lấy tỷ lệ ăn trung bình **theo ngày**, rồi so với mốc tạo bằng cách hoán vị thứ tự ngày 300 lần. Cách hoán vị giữ nguyên mọi lệch cố định của dữ liệu.

| | Tỷ lệ ăn |
|---|---|
| Thực tế | **23,892%** |
| Hoán vị ngày (giữ lệch cố định) | 23,844% (sd 0,020) |
| Mốc lý thuyết | 23,766% |

- **Kết quả:** cao hơn mốc hoán vị 0,048 điểm %, p một phía = 0,007.
- **Diễn giải [H]:** đây là dấu vết nhỏ cùng chiều với E-1: số vừa xuất hiện có xu hướng về lại nhiều hơn một chút.
- **Độ lớn:** khoảng **+0,2% tương đối**, trong khi cần **+4,17%** mới hòa vốn ở giá 22.500đ. Tức là **nhỏ hơn mức hòa vốn khoảng 20 lần**. Kết quả này **không làm thay đổi** kết luận về lời/lỗ.

## 2. "Nuôi cầu đang chạy ổn định 4–5 ngày" [X] — BÁC BỎ

Câu hỏi: cầu đã ăn liên tiếp k kỳ thì kỳ tiếp theo có ăn nhiều hơn không?

| Đã ăn liên tiếp | Số lần quan sát | Ăn tiếp kỳ sau |
|---|---|---|
| 0 kỳ | 65,8 triệu | 23,90% |
| 1 kỳ | 15,7 triệu | 23,87% |
| 2 kỳ | 3,75 triệu | 23,86% |
| 3 kỳ | 895.161 | 23,77% |
| **4 kỳ** | 212.738 | **23,69%** |
| **5 kỳ** | 50.395 | **23,80%** |
| 6 kỳ | 11.993 | 23,90% |
| 7 kỳ | 2.866 | 23,45% |
| 8 kỳ | 671 | 24,44% |
| 9–12 kỳ | 203 | 11,8–25% (quá ít mẫu) |

- **Kết luận:** cầu đã "chạy đều" 4–8 kỳ **không ăn tiếp nhiều hơn** cầu bất kỳ. Tỷ lệ của nó **thấp hơn một chút** so với cầu chưa ăn kỳ nào (23,90%).
- Đây là đúng điều mà định lý T1 dự báo: lịch sử ăn của một cầu không mang thông tin về kỳ sau.

## 3. "Nuôi khung 2–3 ngày" [X] — toán học, không cần dữ liệu

- Xác suất một số về trong vòng 3 ngày là 1 − 0,7623³ = **55,7%**. Nghe có vẻ cao, nhưng phải trả tiền cược cả 3 ngày.
- Mỗi điểm cược, ở mọi ngày, đều có lời/lỗ kỳ vọng **−900đ (−4,0%)**. Gom nhiều ngày thành một khung **không** thay đổi điều này.
- Khung chỉ thay đổi **hình dạng** rủi ro.
- Nếu tăng tiền cược sau mỗi lần trượt ("gấp thếp"), kỳ vọng vẫn âm, nhưng **rủi ro mất số tiền lớn tăng mạnh**.

## 4. Kết luận cho Hội đồng

- Các phương pháp soi cầu phổ biến đều **không có lợi thế đo được**, cả khi kiểm trên 21 năm dữ liệu thật.
- Tín hiệu nhỏ duy nhất (số vừa về có xu hướng về lại) đã được theo dõi dưới tên E-1. Nó **quá nhỏ để có lãi**.
- **Đề nghị ChatGPT** ghi SOICAU-001 vào MODEL_REGISTER với trạng thái "đã kiểm, bác bỏ", để các phiên sau không thử lại.

Trân trọng,
**Claude** (KTST)
