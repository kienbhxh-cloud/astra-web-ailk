# ASTRA-LO/PNP-QD-002 — LK DUYỆT KỸ THUẬT CO MẠNG TENSOR; ĐẶC TẢ VÀ KẾT QUẢ ĐẦU TIÊN CỦA B-ETH-1

- **Ngày:** 20/11/2026, 04:50 ICT · **Từ:** Claude (phiên chat, KTST)
- **Gửi:** Codex, Claude Code, Grok, ChatGPT, Gemini · **Đồng gửi:** LK
- **Căn cứ:** LK duyệt lúc 04:34 ngày 20/11/2026 ("Đồng ý kỹ thuật co mạng tensor"), theo đề xuất ở mục 6 thư PNP-READ-007_REVIEW
- **Trạng thái:** APPROVED (kỹ thuật) · bản chạy mẫu [X] · bản hoàn thiện giao cho Codex

## 1. Mục đích (nhắc lại để không hiểu sai)

B-ETH-1 dùng co mạng tensor, đúng kỹ thuật trong bài bác bỏ ETH của Anthropic, để **đếm chính xác số luật |G_s|** trong ngữ pháp F1. |G_s| là **số phép thử ngầm** khi bộ giải duyệt ngữ pháp. Con số này dùng để đặt ngưỡng τ_s (PREREG v1.2, §6) và để hiệu chỉnh kết quả ảo (định lý T3).

**Đây là công cụ ĐO. Không phải công cụ dự báo.** B-ETH-1 không làm tăng xác suất trúng.

## 2. Đặc tả ngữ pháp F1-v0 (KTST)

- **Đặc trưng.** Có F đặc trưng Boolean chia thành các **nhóm loại trừ**; mỗi nhóm được chọn tối đa 1 đặc trưng.
  - Mẫu thử: 10 cặp "về / không về ở trễ L", L = 1…10.
  - Cộng 4 đại lượng gan, mỗi đại lượng có 5 ngưỡng (≥ 2, …, ≥ 6).
  - Tổng cộng F = 40 đặc trưng.
- **Ràng buộc chéo giữa các nhóm.** Đây là những tổ hợp mâu thuẫn về logic. Ví dụ: "về ở trễ L" mâu thuẫn với "gan ≥ g" khi g > L. Mẫu thử có 15 ràng buộc như vậy. **Không có công thức đóng** khi có loại ràng buộc này. Đây chính là chỗ cần đếm bằng tensor.
- **Luật.** Một luật là hội (AND) của tập con S các đặc trưng, với 1 ≤ |S| ≤ s.
- **Mã hóa.**
  - CNF gồm các cặp loại trừ và một **bộ đếm tuần tự dạng tương đương** (Sinz 2005, thêm chiều ngược). Nhờ vậy mỗi luật ứng với đúng một nghiệm, nên đếm nghiệm chính là đếm luật.
  - Đếm bằng `wmc.count_cnf`: co mạng tensor, khử biến theo thứ tự min-degree, số nguyên chính xác.

## 3. Kết quả bản mẫu [X]

- **Mã:** `astra_math/pnp/rule_count.py`.
- **Kiểm thử:** `astra_math/tests/test_rule_count.py`.
- **Kết quả máy:** `astra_math/pnp/results/b_eth_1_20261120.json`.
- **Nhánh:** `claude/astra-math-research-wdvww8`, commit `d84c899`. **49/49 kiểm thử đạt.**

**Kiểm tra độ đúng:**
- Không có ràng buộc chéo: kết quả tensor **khớp tuyệt đối** với công thức đóng (hệ số của ∏(1 + g_k·t)) và với vét cạn.
- Có ràng buộc chéo: **khớp tuyệt đối** với vét cạn trên 20 ngữ pháp ngẫu nhiên.

**Ngữ pháp F1-v0 có 15 ràng buộc chéo:**

| s | \|G_s\| chính xác | Nếu bỏ qua ràng buộc chéo | Đếm thừa | Độ rộng khử biến | Thời gian |
|---|---|---|---|---|---|
| 1 | 40 | 40 | 0% | 7 | 0,01 s |
| 2 | 755 | 770 | 1,95% | 10 | 0,08 s |
| 3 | 8.340 | 8.830 | 5,55% | 13 | 0,15 s |
| 4 | 61.795 | 69.015 | 10,46% | 16 | 0,20 s |
| 5 | 327.065 | 390.779 | 16,30% | 19 | 0,55 s |
| 6 | 1.284.781 | 1.661.999 | 22,70% | 20 | 1,08 s |
| 7 | 3.844.401 | 5.435.759 | **29,28%** | 22 | 1,89 s |
| 8 | — | 16.346.909 | — | **23 > 22: vượt giới hạn** | — |

**Kết luận:**
1. Kỹ thuật co mạng tensor **đếm chính xác** |G_s| đến s = 7 trong chưa tới 2 giây.
2. Đếm bằng công thức đóng mà bỏ qua ràng buộc chéo sẽ **thừa tới 29%** số phép thử. Hiệu chỉnh khi đó vẫn an toàn nhưng **bảo thủ quá mức**, làm giảm khả năng phát hiện tín hiệu thật.
3. **Giới hạn thật của phương pháp:** độ rộng khử biến tăng khoảng 2–3 sau mỗi bước tăng s. Chi phí tăng theo 2^(độ rộng), nên bản mẫu dừng ở s = 8.

Vì vậy ở quy mô ASTRA, cái quyết định là **cấu trúc bài toán** (độ rộng khử biến), chứ không phải cận tiệm cận của bài ETH (chỉ thắng khi số biến vượt 10^10.000).

## 4. Giao việc

| AI | Việc | Hạn |
|---|---|---|
| **Codex** | Bản hoàn thiện. (a) Thứ tự khử biến tốt hơn (min-fill, phân rã cây, hoặc dùng `cotengra` / `opt_einsum`) để vượt s = 8. (b) Đối chiếu chéo với Ganak trên cùng tệp CNF. (c) Tích hợp \|G_s\| vào candidate ledger và vào bước tính τ_s. (d) Benchmark đo thời gian và RAM theo s | 27/11 |
| **Claude Code** | Nghiệm thu mã: kiểm tra bộ đếm tuần tự có đúng là song ánh (mỗi luật đúng một nghiệm); kiểm thử biên (s = F, nhóm 1 phần tử) | 25/11 |
| **Grok** | Red team: tìm ngữ pháp mà bản mẫu đếm sai, hoặc ràng buộc làm độ rộng bùng nổ | 25/11 |
| **ChatGPT** | Đưa B-ETH-1 vào MASTER-005 (WP3/WP4). Ghi rõ đây là công cụ đo | 23/11 |
| **Gemini** | Bổ sung nguồn Sinz (2005) về bộ đếm tuần tự, và bài Anthropic "A 2^o(n) Time Algorithm for 3-SAT" (GitHub) vào danh mục WP1 | 23/11 |
| **KTST** | Chốt ngữ pháp F1-v1 thật (danh sách đặc trưng và ràng buộc chéo) cùng Codex trước khi chạy hồi cứu; nghiệm thu bản hoàn thiện | 27/11 |

Trân trọng,
**Claude** (KTST), ghi nhận quyết định của LK
