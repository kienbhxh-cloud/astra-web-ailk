# ASTRA-LO/PNP-QD-001 — GHI NHẬN QUYẾT ĐỊNH CỦA LK VÀ PREREG_STATISTICS v1.1

- **Ngày:** 20/11/2026, 04:20 ICT · **Ghi nhận bởi:** Claude (phiên chat, KTST)
- **Gửi:** ChatGPT, Gemini, Grok, Codex, Claude Code · **Đồng gửi:** LK
- **Căn cứ:**
  - LK trả lời trực tiếp Claude lúc 04:09–04:15 ngày 20/11/2026;
  - MASTER-005, mục 9 (B, C);
  - Claude_PREREG_STATISTICS_PNP_20261120 (v1.0).
- **Trạng thái:** APPROVED theo quyết định của LK

## 1. Quyết định của LK [X]

| Mục | Quyết định |
|---|---|
| **Đơn giá mô phỏng** | **22.500đ/điểm**, trả 80.000đ/điểm/nháy. Từ nay bỏ kịch bản 23.000đ. Quy chế v1.0 và báo cáo 18/11 đang ghi 23.000đ: ChatGPT cập nhật khi ra phiên bản mới, giữ nguyên bản cũ |
| **Cách chấm tương lai** | **Phương án (A): e-process**. Giám sát liên tục, không khóa trước số kỳ, chỉ kết luận khi vượt ngưỡng đã khóa. Thay cho mốc 60 kỳ (KTST-009) và 180 kỳ (MASTER-005) |

**Con số tài chính chuẩn (giá 22.500đ):**
- Lời/lỗ kỳ vọng: **−900đ/điểm (−4,00%)**. Bộ 5 số × 5 điểm: **−22.500đ/kỳ**.
- Để hòa vốn cần trung bình **1,40625 nháy/kỳ** cho 5 số, tức hơn mốc ngẫu nhiên (1,35) **4,17%**.

## 2. PREREG_STATISTICS v1.1: đặc tả e-process (bổ sung cho v1.0, không thay thế)

- **Mã:** `xsmb_audit.eprocess_mean`, `eprocess_any_hit`, `p_set_any_given_u`. Commit trên nhánh `claude/astra-math-research-wdvww8`. 41/41 kiểm thử đạt.

**Chỉ số chính: số nháy mỗi kỳ của bộ 5 số đã khóa.**
- Giả thuyết gốc: E[Y_t | quá khứ] ≤ 1,35.
- Công thức: W_t = trung bình theo λ ∈ {0,01; 0,02; 0,044; 0,1; 0,2} của tích Π(1 + λ(Y_s − 1,35)).
- Mức λ = 0,044 là mức tối ưu cho lợi thế vừa đủ hòa vốn (δ/σ² = 0,05625/1,2825).

**Chỉ số phụ: bộ 5 có ≥ 1 số về.**
- Mốc từng kỳ: p0_t = 1 − C(100−u_t, 5)/C(100, 5).
- Công thức: W_t = trung bình theo λ ∈ {0,05; 0,1; 0,2; 0,5; 1} của tích Π(1 + λ(hit_t − p0_t)/p0_t).

**Quy tắc kết luận.**
- Theo bất đẳng thức Ville, xác suất W_t từng vượt 1/α khi H0 đúng không quá α. Vì vậy được xem kết quả bất cứ lúc nào, và dừng ở thời điểm nào cũng hợp lệ.
- Với **m** thuật toán khóa song song (tối đa 3, mỗi nhánh F1/F2/F3 một thuật toán): bác bỏ H0 cho một thuật toán khi **W_t ≥ 20m**. Với m = 3, ngưỡng là **60**.
- Danh sách λ và ngưỡng **khóa từ thư này**.
- Kết quả là **"không bác bỏ"** cho đến khi W_t vượt ngưỡng. Không có kết luận "thắng" ở chỉ số phụ khi chỉ số chính chưa đạt.

**Mô phỏng kiểm tra công cụ** [X] (100 lần cho mỗi mức lợi thế, tối đa 6.000 kỳ, ngưỡng 60):

| Lợi thế thật | Tỷ lệ phát hiện trong 6.000 kỳ | Trung vị số kỳ đến khi phát hiện |
|---|---|---|
| Không có (H0 đúng) | báo nhầm ≤ 5% (kiểm thử tự động: 1.000 kỳ, ngưỡng 20) | — |
| +4,17%, vừa đủ hòa vốn | 75% | khoảng **3.100 kỳ** (≈ 8,5 năm) |
| +10% | 100% | khoảng **630 kỳ** |
| +20% | 100% | khoảng **184 kỳ** |

**Ý nghĩa.**
- Cách (A) không làm giảm số kỳ cần để chứng minh một lợi thế nhỏ.
- Nhưng nó cho phép **phát hiện sớm nếu có lợi thế lớn**, và **không bao giờ bị phạt** vì xem kết quả nhiều lần.

## 3. Việc của từng AI theo quyết định này

| AI | Việc |
|---|---|
| ChatGPT | Đưa đơn giá 22.500đ và phương án (A) vào PROTOCOL_MASTER và MODEL_REGISTER; ra Quy chế v1.1 |
| Codex | Pipeline chấm tương lai gọi `eprocess_mean` và `eprocess_any_hit` mỗi kỳ; lưu đường đi W_t vào forecast log kèm mã băm |
| Grok | Phản biện đặc tả e-process ở mục 2 (red team: thử phá bằng dừng sớm, đổi λ, đổi chỉ số) |
| Gemini, Claude Code | Không đổi việc. Lưu ý dùng đơn giá 22.500đ trong mọi báo cáo |

Trân trọng,
**Claude** (KTST), ghi nhận quyết định của LK
