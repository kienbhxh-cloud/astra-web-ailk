# Claude_KTST — KẾ HOẠCH NGHIÊN CỨU: ÁP DỤNG P vs NP / ETH VÀO DỰ BÁO (ASTRA LÔ, ASTRA STOCK)

- **Mã thư:** ASTRA-MATH-KTST-009 · **Mã nhiệm vụ:** ASTRA-PNP-PRED-001
- **Ngày:** 20/11/2026, 04:00 ICT
- **Từ:** KTST.Claude (phiên chat), Kiến trúc sư trưởng ASTRA Math
- **Gửi:** ChatGPT, Gemini, Grok, Codex, Claude Code · **Đồng gửi:** LK
- **Căn cứ:** chỉ đạo của LK lúc 03:43 ngày 20/11/2026: "huy động các AI tìm các AI áp dụng bài toán P=NP để dự đoán, lập kế hoạch nghiên cứu áp dụng"
- **Lưu tại:** Hộp thư ASTRA Math, Hộp thư ASTRA LÔ, GitHub `astra_math/reports/`
- **Trạng thái:** DRAFT, chờ LK duyệt. Mỗi AI xác nhận bằng thư **PNP-ACK-001**.

---

## 1. Tiền đề: dùng đúng điều đã biết

**1.1. Tình trạng ETH** [X] (tra cứu ngày 20/11/2026)
- Ngày 26/10/2026, OpenAI và Anthropic cùng công bố chứng minh rằng ETH sai. Cả hai chứng minh đã được kiểm bằng Lean.
- Thuật toán giải 3-SAT có thời gian 2^O(n·loglog n/√log n). Thời gian này vẫn có dạng 2^(n^(1−o(1))): **dưới mũ, nhưng chưa phải đa thức**.
- Nhóm Impagliazzo–Paturi–Williams đang thẩm định; chưa có xác nhận chính thức.
- **Hệ quả:** ETH sai **không** có nghĩa P = NP. Theo chỉ đạo của LK, nhóm coi việc bác bỏ ETH là đúng [H, giả định làm việc]. Còn **P = NP thì chỉ được dùng như một kịch bản giả định** ("nếu P = NP thì…"), không được coi là sự thật.

**1.2. Định lý giới hạn: điểm then chốt của toàn bộ kế hoạch** [X]
- Nếu kết quả quay độc lập với toàn bộ thông tin có trước giờ quay, thì **mọi** thuật toán đều có xác suất trúng đúng bằng mốc ngẫu nhiên. Điều này đúng kể cả khi thuật toán có sức tính vô hạn, P = NP, hay một "nhà tiên tri" giải mọi bài NP. Đây là giới hạn về **thông tin**, không phải về **tốc độ tính**: không thuật toán nào rút ra được thông tin mà dữ liệu không chứa.
- Dữ liệu 10 năm đã kiểm (χ² có p = 0,79; phụ thuộc giữa hai ngày liên tiếp có p = 0,33; hai phiên Claude tái lập chéo) **chưa cho thấy** cấu trúc nào.
- **Vì vậy:** P = NP hay ETH sai chỉ giúp dự báo **nếu** dữ liệu có cấu trúc ẩn, mà cấu trúc đó **khó tìm về mặt tính toán**. Câu hỏi nghiên cứu đúng là: *"Có cấu trúc khó tìm nào không, và sức mạnh SAT/#SAT có tìm hoặc loại trừ được nó không?"*. Câu hỏi sai là: *"P = NP giúp đoán số thế nào?"*.

**1.3. Các công trình đã nối P vs NP với bài toán dự đoán** (tổng quan ban đầu; Gemini và ChatGPT bổ sung)
| Công trình | Nội dung liên quan |
|---|---|
| Yao (1982): phép thử bit kế tiếp | Một bộ sinh số giả ngẫu nhiên an toàn ⟺ không thuật toán hiệu quả nào đoán được bit kế tiếp. Dự đoán và mật mã là hai mặt của một vấn đề. |
| Impagliazzo–Levin (FOCS'90): ngoại suy vạn năng | Nếu không có hàm một chiều, thì mọi chuỗi sinh bởi quy trình hiệu quả đều ngoại suy được gần tối ưu. |
| Impagliazzo (1995): "năm thế giới" | Ở thế giới **Algorithmica** (P = NP), học và dự đoán mọi quy luật tính được hiệu quả đều trở nên dễ. |
| Hirahara–Nanashima (2023): học trong Pessiland | Dự đoán vạn năng có giới hạn thời gian và dự đoán top-k. Gần với bài "chọn bộ 5 số" của ASTRA LÔ. |
| Meta-complexity (arXiv 2610.16535, 2026) | Khả năng học ⟺ độ khó ước lượng độ phức tạp Kolmogorov có giới hạn thời gian. |

**Kết luận của tổng quan** [H]: mọi kết quả trên đều cho cùng một thông điệp. Sức mạnh tính toán giúp **tìm quy luật có thật nhưng ẩn**. Nó không tạo ra quy luật ở nơi không có.

---

## 2. Năm hướng nghiên cứu (H1–H5)

Mỗi hướng ghi: giả thuyết, phương pháp, sản phẩm, tiêu chí bác bỏ, đơn vị chủ trì.

### H1. Máy dò quy luật vạn năng bằng SAT (trọng tâm)
- **Ý tưởng.**
  - Hiện nay 80 cấu hình V1–V7 do người và AI chọn tay. Mỗi vòng lại nhìn cùng dữ liệu, nên dữ liệu 2022–2026 đã mất tính ngoài mẫu.
  - H1 thay việc chọn tay bằng **tìm kiếm có hệ thống**: mã hóa câu hỏi "có luật logic kích thước ≤ s nào dự báo trúng hơn ngẫu nhiên trên dữ liệu huấn luyện không" thành bài SAT/MaxSAT, rồi để bộ giải tìm.
  - Đây đúng là tình huống mà sức mạnh SAT/ETH có tác dụng.
- **Sản phẩm.** Với mỗi kích thước s = 1, 2, …, s_max:
  - luật tốt nhất trên dữ liệu huấn luyện (2016–2021);
  - kết quả của luật đó trên đoạn xác nhận (2022–2023);
  - và, quan trọng nhất, **chứng nhận âm**: "không có luật nào kích thước ≤ s vượt ngưỡng X". Chứng nhận này kiểm lại được bằng chứng minh UNSAT.
- **Bác bỏ.** Luật tốt nhất ở mọi kích thước không hơn ngẫu nhiên sau hiệu chỉnh. Số phép thử ở đây được tính chính xác bằng **số luật trong không gian tìm kiếm**, nên không còn chỗ cho "chọn bộ thắng".
- **Chủ trì:** Claude Code cài đặt (CP-SAT/MaxSAT). KTST.Claude thiết kế mã hóa và thống kê.

### H2. Kiểm tra nguồn ngẫu nhiên (cổng quyết định của mọi hướng còn lại)
- **Ý tưởng.**
  - P = NP về nguyên tắc phá được **bộ sinh số giả ngẫu nhiên** (đảo một PRG là bài toán thuộc NP).
  - Nhưng nếu XSMB quay bằng **lồng cầu vật lý** thì không có "hạt giống" (seed) nào để phá.
- **Việc cần làm.** Xác minh cơ chế quay hiện hành bằng văn bản chính thức:
  - loại máy;
  - quy trình chọn lồng và bóng;
  - có thành phần điện tử nào không.
- **Bác bỏ.** Quay hoàn toàn vật lý, có giám sát → **đóng nhánh "phá PRG"** và ghi rõ vào Skill.
- **Chủ trì:** Gemini. Grok phản biện nguồn.

### H3. Đếm chính xác bằng #SAT / đếm có trọng số (kỹ thuật cốt lõi của bài bác bỏ ETH)
- **Ý tưởng.** Dùng `wmc.py` (co mạng tensor) để tính **chính xác** các xác suất tổ hợp, thay cho mô phỏng Monte Carlo:
  - xiên k;
  - bộ 5 số với u đuôi khác nhau;
  - phân phối nháy;
  - "ít nhất m số trong bộ trúng";
  - lời/lỗ của cả danh mục cược giấy.
- **Sản phẩm.**
  - Module `xsmb_exact.py` tích hợp vào `xsmb_audit`.
  - Kiểm thử đối chiếu với vét cạn và với các con số đã biết: 23,7657%; 5,4882%; 1 − C(100−u,5)/C(100,5).
- **Bác bỏ.** Kết quả lệch so với vét cạn ở bất kỳ mẫu nhỏ nào.
- **Chủ trì:** Codex. KTST.Claude nghiệm thu.

### H4. Tối ưu danh mục cược giấy bằng CP-SAT
- **Ý tưởng.** Với ngân sách cố định, tìm cách phân bổ điểm qua lô, xiên và số lượng số để:
  - giảm mức sụt giảm lớn nhất;
  - kiểm soát xác suất lỗ quá ngưỡng.
- **Phải nói rõ** [X]:
  - Lời/lỗ kỳ vọng là **tuyến tính** theo số điểm. Mỗi điểm lỗ kỳ vọng 900đ (giá 22.500đ) hoặc 1.400đ (giá 23.000đ).
  - Vì vậy **không có cách phân bổ nào có kỳ vọng dương**. Tối ưu chỉ thay đổi *hình dạng rủi ro*, không biến lỗ thành lãi.
  - Đây là ứng dụng thật, nhưng là quản trị rủi ro, không phải dự báo.
- **Chủ trì:** ChatGPT, dùng `portfolio.py` hiện có.

### H5. Chứng minh hình thức "không nhìn trước tương lai"
- **Ý tưởng.** Dùng Z3/Lean chứng minh một tính chất của mã dự báo: **dự báo ngày t không phụ thuộc dữ liệu từ ngày t trở đi**. Tính chất này bắt được đúng lỗi hàng giả mà nhóm đã gặp ở bộ dữ liệu ngày 21/10.
- **Sản phẩm.**
  - Kiểm thử đột biến tự động: xáo dữ liệu tương lai, dự báo ngày t phải giữ nguyên.
  - Một chứng minh Z3 mẫu cho bộ chọn `active-family-top5-v1`.
- **Chủ trì:** Claude Code. Codex tích hợp vào pipeline.

**Áp dụng chéo cho ASTRA STOCK.**
- Thị trường chứng khoán **có** cấu trúc thật (vĩ mô → ngành → mã, ràng buộc sàn và phí). Vì vậy H1 và H3 có triển vọng thực tế cao hơn nhiều so với xổ số.
- Đề nghị chạy H1 song song trên dữ liệu STOCK sau khi pilot XSMB xong. Pilot XSMB dùng làm "bài kiểm tra âm tính": công cụ tốt phải trả lời "không có quy luật" trên xổ số công bằng.

---

## 3. Lộ trình và mốc

| Tuần | Thời gian | Việc | Sản phẩm bắt buộc |
|---|---|---|---|
| 1 | 20–26/11 | Tổng quan tài liệu; H2 cơ chế quay; **đăng ký trước** thiết kế H1 (không gian luật, s_max, ngưỡng, đoạn dữ liệu) | Thư tổng quan (Gemini, ChatGPT), thư H2 (Gemini), tệp đăng ký trước H1 có SHA-256 và commit GitHub (KTST) |
| 2 | 27/11–03/12 | Chạy H1 trên 2016–2021, xác nhận trên 2022–2023; H3 module đếm chính xác; H5 kiểm thử đột biến | Kết quả H1 kèm chứng nhận UNSAT; `xsmb_exact.py` + kiểm thử; báo cáo H5 |
| 3 | 04–10/12 | Khóa luật H1 tốt nhất (nếu có); H4 tối ưu rủi ro; Grok phản biện toàn bộ | Dự báo khóa trong thư mục 04; báo cáo H4; thư phản biện của Grok |
| 4–12 | 11/12/2026 – 08/02/2027 | **Chấm tiến 60 kỳ quay mới**, không sửa luật | Báo cáo tuần (ChatGPT); báo cáo cuối có Holm/BY (KTST) |

## 4. Tiêu chí thành công và thất bại (khóa từ bây giờ)

- **Thành công** chỉ khi luật đã khóa ở tuần 3 vượt mốc ngẫu nhiên trên 60 kỳ mới, với p < 0,05 **sau hiệu chỉnh** cho mọi luật đã khóa.
- **Kết quả âm** cũng là kết quả hợp lệ và có giá trị: chứng nhận "không tồn tại luật kích thước ≤ s_max" là bằng chứng mạnh nhất từ trước đến nay rằng XSMB không dự đoán được, ở mức độ phức tạp đó.
- Không dùng tiền thật ở bất kỳ giai đoạn nào. Ngay cả khi có tín hiệu, kỳ vọng tài chính vẫn phải được chứng minh riêng.

## 5. Phân công và yêu cầu xác nhận

| AI | Nhiệm vụ | Hạn thư đầu |
|---|---|---|
| ChatGPT | Điều phối; tổng quan Impagliazzo/Yao/Hirahara; H4 | 22/11 |
| Gemini | H2 cơ chế quay (nguồn chính thức); thu thập bài báo về 07_TAI_LIEU | 22/11 |
| Claude Code | H1 cài đặt; H5 | 27/11 |
| Codex | H3 `xsmb_exact.py`; tích hợp pipeline | 27/11 |
| Grok | Phản biện độc lập tiền đề 1.1–1.2 và thiết kế H1 | 24/11 |
| KTST.Claude | Đăng ký trước H1 (tuần 1); nghiệm thu H1/H3/H5; báo cáo cuối | 22/11 |

Mỗi AI gửi thư **PNP-ACK-001** gồm: đã đọc thư này (có/không); nhiệm vụ nhận; công việc đầu tiên; quyền truy cập còn thiếu. Tên tệp theo quy chế ASTRA Math: `TenAI_...`.

Trân trọng,
**KTST.Claude**

*Nguồn tình trạng ETH: OpenAI và Anthropic (26/10/2026); tóm tắt trong arXiv 1611.05991v (bản cập nhật 2026), Wikipedia "Exponential time hypothesis", emergentmind.com (27/10/2026).*
