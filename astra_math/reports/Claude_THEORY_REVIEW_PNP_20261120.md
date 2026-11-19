# Claude — THEORY_REVIEW.md (WP1: Lý thuyết và kiểm toán tuyên bố)

- **Mã:** ASTRA-LO/PNP-MASTER-005 · WP1 · sản phẩm của Claude
- **Ngày:** 20/11/2026 · **Từ:** Claude (phiên chat, KTST) · **Phối hợp:** Grok (CLAIM_AUDIT.md)
- **Trạng thái:** REVIEWED, chờ Grok phản biện
- **Nhãn:** [X] đã chứng minh hoặc có nguồn kiểm được · [H] giả thuyết · [C] tuyên bố cần xác minh

---

## 1. Định lý T1: giới hạn thông tin

**Phát biểu.**
- Gọi X_t là bộ 27 giải của kỳ t, và F_{t−1} là mọi thông tin có trước giờ quay: lịch sử, dữ liệu ngoài, kết quả của bất kỳ máy tính nào.
- Giả sử X_t độc lập với F_{t−1}, và 27 giải độc lập, đều trên 00–99 (giả thuyết H0).
- Khi đó, với **mọi** chiến lược S (kể cả ngẫu nhiên hóa, sức tính vô hạn, có "nhà tiên tri" giải mọi bài NP) chọn tập A_t gồm k số khác nhau dựa trên F_{t−1}:
  - P(ít nhất 1 số của A_t về) = 1 − C(100−u, k)/C(100, k), với u là số đuôi khác nhau của kỳ t. Trung bình theo u, với k = 5: **74,9656%**.
  - Kỳ vọng số nháy = 27k/100. Với k = 5: **1,35**.
  - Lời/lỗ kỳ vọng mỗi điểm = 27 × 0,01 × 80.000 − giá: **−900đ** (giá 22.500đ) hoặc **−1.400đ** (giá 23.000đ).

**Chứng minh** [X].
1. A_t chỉ phụ thuộc F_{t−1}, mà X_t độc lập với F_{t−1}. Do đó, với điều kiện F_{t−1}, phân phối của X_t không đổi.
2. Theo H0, phân phối của X_t bất biến khi hoán vị 100 số. Vì vậy P(X_t ∩ A ≠ ∅ | F_{t−1}) chỉ phụ thuộc |A| = k, không phụ thuộc A là tập nào.
3. Lấy kỳ vọng theo F_{t−1} thì được đúng giá trị trên. Sức tính của S **không xuất hiện ở bất kỳ bước nào**. ∎

**Hệ quả.**
- Câu hỏi "P = NP có giúp dự báo không" quy về đúng một câu hỏi: **H0 có sai không?**
- Đây là câu hỏi **thống kê, kiểm định được**. Nó không phải câu hỏi về độ phức tạp tính toán.
- Mọi nghiên cứu trong WP2–WP4 đều là cách kiểm tra H0.

## 2. Định lý T2: dự báo được ⟺ phân biệt được (Yao, 1982) [X]

- Với một nguồn dữ liệu **lấy mẫu được bằng thuật toán hiệu quả**, các điều sau tương đương:
  - (a) tồn tại thuật toán thời gian đa thức đoán được ký hiệu kế tiếp tốt hơn ngẫu nhiên một lượng không bỏ qua được;
  - (b) tồn tại bộ phân biệt (distinguisher) hiệu quả, tách được nguồn đó khỏi nguồn ngẫu nhiên thật.
- **Áp dụng cho ASTRA:** WP2 (bộ phân biệt) và WP3 (tìm luật dự báo) là **hai mặt của cùng một phép kiểm định**. Nếu WP2 không tìm được bộ phân biệt nào, thì WP3 không có gì để tìm, trong phạm vi các lớp đã thử. Hai gói nên chia chung ngân sách alpha (xem PREREG_STATISTICS).
- **Giới hạn:** T2 nói về thuật toán hiệu quả. Nếu nguồn là lồng cầu vật lý thì không có chương trình sinh số nào để "đảo ngược". Lúc đó chỉ còn T1: dữ liệu có lệch vật lý hay không.

## 3. Nếu P = NP thì được gì (kịch bản giả định, "thế giới Algorithmica" của Impagliazzo 1995) [X]

| Năng lực | Có ích cho XSMB không |
|---|---|
| Phá mọi bộ sinh số giả ngẫu nhiên và hàm một chiều | Chỉ khi XSMB dùng bộ sinh số. Đang chờ Gemini xác minh cơ chế quay (WP0). Nếu quay bằng lồng cầu vật lý thì **không có ích** |
| Tìm giả thuyết ngắn nhất khớp dữ liệu (học theo nguyên lý Occam) | Tìm **nhanh hơn** luật khớp nhất. Nhưng trên dữ liệu ngẫu nhiên, luật khớp nhất là luật **quá khớp** (định lý T3) |
| Ước lượng độ phức tạp Kolmogorov có giới hạn thời gian (meta-complexity) | Cho phép kiểm tra "dữ liệu có nén được không" một cách tối ưu. Đây là phiên bản lý tưởng của WP2 |

## 4. Định lý T3: tìm kiếm mạnh hơn không làm luật tốt hơn (giới hạn Occam/Hoeffding) [X]

- Giả sử thử |G| luật trên n kỳ. Với xác suất ≥ 1 − δ, **mọi** luật đều có điểm trong mẫu lệch so với điểm thật không quá √(ln(|G|/δ)/(2n)).
- Trường hợp chỉ số "trúng ít nhất 1 số", δ = 0,05:

| Số luật thử \|G\| | n = 1.460 kỳ (4 năm) | n = 2.190 kỳ (6 năm) |
|---|---|---|
| 1.000 | 5,8 điểm % | 4,8 điểm % |
| 10⁶ | 7,6 điểm % | 6,2 điểm % |
| 10⁹ | 9,0 điểm % | 7,4 điểm % |

- **Diễn giải.** Bộ giải SAT có thể duyệt hết 10⁹ luật. Khi đó "luật tốt nhất trong mẫu" sẽ hơn ngẫu nhiên đến khoảng 7–9 điểm %, **dù H0 đúng**. Mức này lớn hơn mọi lợi thế khả dĩ.
- **Hệ quả:** tìm kiếm càng mạnh (SAT, ETH sai, P = NP) thì kết quả trong mẫu càng **vô nghĩa**, trừ khi ngưỡng được hiệu chỉnh theo |G|. Đây là cơ sở của tiêu chí chứng nhận ở PREREG_STATISTICS, mục 4.

## 5. Tình trạng tuyên bố "ETH sai" (MASTER-005 đã gắn nhãn [C])

| Mục | Nội dung | Nhãn |
|---|---|---|
| Công bố | Ngày 26/10/2026, OpenAI ("The Exponential Time Hypothesis is False", 67 trang) và Anthropic cùng công bố. Mỗi bên nói mô hình nội bộ tìm ra thuật toán ngày 16/10. Cả hai đã kiểm bằng Lean | [X] việc công bố đã xảy ra |
| Thuật toán | Thuật toán tất định cho 3-SAT, thời gian 2^O(n·loglog n/√log n). Thời gian này vẫn có dạng 2^(n^(1−o(1))) | [X] theo trích dẫn lại trong tài liệu học thuật |
| Thẩm định | Nhóm Impagliazzo–Paturi–Williams (hai trong ba người đề xuất ETH) đang thẩm định. **Chưa có xác nhận chính thức** | [C] |
| P vs NP | **Vẫn là bài toán mở.** ETH sai không kéo theo P = NP | [X] |
| Ích lợi thực tế cho ASTRA | Lợi thế tiệm cận chỉ đáng kể khi n rất lớn. Với bài H1/F1 (vài trăm đến vài nghìn biến), hiệu năng do bộ giải CDCL thực tế quyết định | [H] |

**Ý kiến KTST:**
- Dùng bác bỏ ETH làm **giả định làm việc** theo chỉ đạo của LK, gắn nhãn [C]. Em đồng ý với ChatGPT là **không** dùng nó làm tiền đề cho bất kỳ kết luận dự báo nào.
- Theo T1, kể cả khi bác bỏ ETH được xác nhận, kết luận về XSMB **không đổi**.

## 6. Bảng kiểm toán tuyên bố ban đầu (Grok bổ sung các tuyên bố tìm được trên mạng)

| Tuyên bố | Nhãn | Lý do |
|---|---|---|
| "AI dùng P = NP để dự đoán xổ số" | [C], mặc định sai | Chưa ai chứng minh P = NP. Kể cả nếu có, T1 vẫn chặn khả năng dự báo |
| "Bộ giải SAT tìm được cầu thắng trên lịch sử" | [C] | T3: điểm trong mẫu bị thổi phồng theo ln\|G\| |
| "Tối ưu bộ số làm tăng xác suất trúng" | sai [X] | T1: mọi tập k số khác nhau có cùng xác suất. Tối ưu chỉ thay đổi rủi ro |
| "Dữ liệu XSMB không nén được, nên XSMB công bằng" | sai về logic [X] | "Không bác bỏ H0" không đồng nghĩa "H0 đúng". Chỉ được nói: không phát hiện lệch ở độ nhạy hiện có |
| "Nếu XSMB dùng bộ sinh số giả ngẫu nhiên thì P = NP phá được" | đúng có điều kiện [X] | T2. Điều kiện đầu chờ WP0 xác minh |

## 7. Nguồn

- Yao A.C. (1982). Theory and applications of trapdoor functions. FOCS.
- Impagliazzo R. (1995). A personal view of average-case complexity. CCC.
- Impagliazzo R., Levin L. (1990). No better ways to generate hard NP instances than picking uniformly at random. FOCS.
- Hirahara S., Nanashima M. (2023). Learning in Pessiland via Inductive Inference. ECCC TR23-100.
- Learning, Compression, and Meta-Complexity. arXiv 2610.16535 (2026).
- Almost-Polynomial Ratio ETH-Hardness of Approximating Densest k-Subgraph, bản 2026, mục 2.1: trích dẫn thuật toán của OpenAI. arXiv 1611.05991.
- Wikipedia "Exponential time hypothesis" (truy cập 20/11/2026); emergentmind.com (27/10/2026); hackernoon, letsdatascience (10/2026).

Trân trọng,
**Claude** (KTST)
