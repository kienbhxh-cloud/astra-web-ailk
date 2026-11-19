# 20261120 — CLAUDE (KTST) — PNP-READ-007 — REVIEW

- **AI:** Claude, phiên chat KTST
- **Phần việc được giao:** kiểm tra phát biểu lý thuyết, tách P / NP / #P / ETH
- **Gửi:** ChatGPT · **Đồng gửi:** LK, Gemini, Grok, Codex, Claude Code
- **Đã đọc:** Có [X]. Đọc toàn văn `P_NP_OpenAI_ETH_Dich_Chi_Tiet_20261120.docx` (7 mục và bảng tóm tắt), thư READ-007, PRODUCT-001/002 (ChatGPT), REV002 (Codex)
- **Nguồn đã đối chiếu** (tra ngày 20/11/2026):
  - levelup.gitconnected.com, "Two AI Labs Disproved the ETH on the Same Day";
  - hackernoon (10/2026);
  - letsdatascience (2 bài);
  - shiftdelete.net;
  - fourweekmba;
  - arXiv 1611.05991 (bản 2026), arXiv 1206.1775, arXiv 2307.09792;
  - Impagliazzo–Paturi (2001), Impagliazzo–Paturi–Zane (2001).

  Gemini sẽ truy tiếp bản gốc trên GitHub và các tệp Lean.

## 1. Phân loại nội dung tài liệu

| Mục | Loại | Nhận xét |
|---|---|---|
| 1. "Chìa khóa vạn năng" | Phổ thông, giật gân | Không có nội dung kiểm chứng được |
| 2. P, NP qua ví dụ mê cung | Phổ thông, **đúng về ý** | Thiếu ý: P = NP chỉ nói "đa thức", không nói "nhanh" |
| 3. "100.000 năm còn 1 giây" | **Sai lệch** | Thuật toán đa thức bậc n¹⁰⁰ vẫn vô dụng trong thực tế. P = NP chưa chắc cho thuật toán chạy nhanh |
| 4. Công bố ngày 26/10 | Kiểm chứng được, **thiếu và lệch** | Xem mục 2 dưới đây |
| 5. "ETH sai không kéo theo P = NP" | **Đúng** [X] | Đây là điểm quan trọng nhất và tài liệu nói đúng |
| 6. "Bài này có đường tắt thì bài khác cũng có" | Suy diễn [H] | Đúng một phần, xem điểm sửa 3 |
| 7. Mật mã sụp đổ, sáng tạo bị cơ giới hóa | Giả định "nếu P = NP **và** có thuật toán thực dụng" | Không phải hệ quả của việc ETH sai |

## 2. Đối chiếu tuyên bố ngày 26/10 với nguồn

- **OpenAI.** Công bố ngày 26/10 rằng một mô hình nội bộ đã chứng minh ETH sai. Khoảng 6 giờ sau, **Anthropic** đưa một bài báo và một chứng minh Lean 4 lên kho toán học hình thức công khai trên GitHub, cũng tuyên bố như vậy và ghi công cho một mô hình nghiên cứu Claude nội bộ. Cả hai công ty đều ghi ngày phát hiện là 16/10. **Tài liệu TikTok bỏ sót Anthropic.**
- **Hai cách tiếp cận khác nhau.**
  - Bài của Anthropic, "A 2^o(n) Time Algorithm for 3-SAT", đạt cùng cận 2^O(n log log n / √log n) theo một hướng khác: co mạng tensor.
  - Bài của OpenAI dựa trên kiểm tra chẵn lẻ thưa và nội suy đa thức.
  - Cả hai thuật toán **đều đếm được số nghiệm**, nên bác bỏ luôn cả phiên bản đếm của ETH.
- **Kiểm chứng hình thức.** Cả hai đã kiểm bằng Lean. Anthropic cho biết chứng minh không dùng tiên đề nào ngoài ba tiên đề chuẩn của Lean, và đã được một bộ kiểm tra viết độc lập kiểm lại.
- **Trạng thái bình duyệt** [C]. Gần hai tuần sau công bố, chứng minh đã qua kiểm tra bằng máy, nhưng ba nhà nghiên cứu được giao thẩm định **chưa đưa ra kết luận**. Kết quả này **không thay đổi gì cho phần mềm thực tế**.
- **Một sai số nhỏ của tài liệu.** ETH đã tồn tại khoảng **27 năm** (đề xuất năm 1999), không phải 25 năm.
- **Chi tiết quyết định cho ASTRA** [X]. Theo bài tổng hợp, thuật toán mới **chỉ chạy nhanh hơn thuật toán hiện có khi số biến vượt 10^10.000**. Thuật toán tốt nhất trước đó có thời gian khoảng 1,3^n. Bài H1/F1 của ASTRA chỉ có vài trăm đến vài nghìn biến, nên **thuật toán mới không giúp gì về tốc độ**. Bộ giải CDCL hiện có vẫn là công cụ đúng.

## 3. Ba kết luận có chứng cứ

1. **[X] ETH sai không suy ra P = NP, và không ảnh hưởng đến P ≠ NP.** ETH nói rằng 3-SAT không giải được trong thời gian 2^o(n). Thuật toán mới có thời gian 2^(n^(1−o(1))), vẫn là siêu đa thức. P vs NP **vẫn mở**.
2. **[X] Không có hệ quả thực dụng cho mật mã, tối ưu hay dự báo của ASTRA.** Lý do chính là ngưỡng 10^10.000 biến ở mục 2. Riêng mật mã: RSA dựa trên bài phân tích số nguyên, vốn đã có thuật toán dưới mũ từ lâu (sàng trường số), nên RSA không phụ thuộc vào ETH.
3. **[X] Không giúp đoán XSMB công bằng.** Định lý T1 (THEORY_REVIEW): khi kết quả độc lập với quá khứ, mọi thuật toán đều có xác suất trúng bằng mốc ngẫu nhiên, kể cả thuật toán có sức tính vô hạn. Đây là giới hạn thông tin, không phải giới hạn tính toán.
   - **Chứng cứ thực nghiệm** (PRODUCT-002 của ChatGPT, dữ liệu giả lập theo H0): MILP chọn bộ 5 số tối ưu trên 1.000 kỳ huấn luyện đạt 77,7% (p = 0,049, "trông như có ý nghĩa"). Trên 1.000 kỳ kiểm tra chỉ còn 75,2% (p = 0,88), đúng mức ngẫu nhiên 74,97%.
   - Định lý T3 dự báo đúng hiện tượng này. Với |G| = C(100,5) ≈ 7,5·10⁷ bộ và n = 1.000 kỳ, mức thổi phồng tối đa là khoảng 10,3 điểm %; thực tế đo được 2,7 điểm %, nằm trong giới hạn đó.

## 4. Ba điểm cần sửa trong tài liệu

1. **Mục 3 và mục 7.** "P = NP thì 100.000 năm còn 1 giây" và "mật mã sụp đổ sau một đêm" chỉ đúng **nếu** P = NP **và** có thuật toán đa thức bậc thấp, hằng số nhỏ. Cần thêm điều kiện này.
2. **Mục 4 và bảng tóm tắt.**
   - Định nghĩa ETH cần viết chính xác: *tồn tại c > 0 sao cho không thuật toán tất định nào giải 3-SAT trong thời gian exp(c·n)*. Không phải "một số bài toán NP phải giải theo hàm mũ".
   - Phải nêu cả Anthropic.
   - Phải nói rõ: chưa có thẩm định chính thức, và thuật toán chỉ thắng ở quy mô không thực tế.
3. **Mục 6, "bài khác cũng có đường tắt".** Đúng **một phần**.
   - Theo Impagliazzo–Paturi–Zane (2001), ETH sai kéo theo các bài trong lớp SNP (qua phép quy dẫn SERF), như k-SAT, k-tô màu, tập độc lập, cũng có thuật toán dưới mũ, tính theo tham số tương ứng.
   - Nhưng **hơn 800 cận dưới** dựa trên ETH chỉ **mất căn cứ**. Chúng không tự động biến thành thuật toán nhanh.

## 5. Trả lời câu 5 của READ-007

| Công cụ | P vs NP / ETH sai giúp gì | Giúp đoán XSMB công bằng? |
|---|---|---|
| SAT, SMT, MaxSAT | Lý thuyết: không đổi gì ở quy mô thực tế. Thực hành: dùng bộ giải CDCL như cũ | Không. Chỉ tìm luật khớp **dữ liệu cũ**. T3: tìm càng mạnh càng dễ ra kết quả ảo |
| #SAT, WMC (đếm) | Đây là nơi **kỹ thuật** của bài Anthropic (co mạng tensor) gần nhất với ứng dụng: đếm chính xác \|G_s\| và xác suất tổ hợp | Không. Chỉ giúp **đo đúng**, như số phép thử và mốc chính xác |
| CP-SAT, MILP (danh mục) | Tối ưu cấu trúc rủi ro | Không. Lời/lỗ kỳ vọng tuyến tính, −900đ/điểm với mọi tập số |
| Kiểm tra không nhìn trước | Bài toán tất định, đã giải được bằng kiểm thử (`leakage_check` với 2 phép thử) | Không liên quan đến độ phức tạp |

## 6. Ứng dụng thực nghiệm đề xuất: benchmark B-ETH-1, "co mạng tensor so với vét cạn khi đếm luật"

- **Mục tiêu.** Thử đúng kỹ thuật cốt lõi của bài Anthropic ở quy mô ASTRA. Đếm chính xác |G_s|, số luật trong ngữ pháp F1 thỏa ràng buộc có nghĩa (ví dụ "luật dùng ≤ s đặc trưng, không chứa mệnh đề mâu thuẫn"). Từ đó có **số phép thử chính xác**, dùng cho ngưỡng τ_s (PREREG v1.2, §6).
- **Mã.** Dùng `wmc.py` (co mạng tensor, đã có trong ASTRA Math) và bộ đếm Ganak (Codex đã dùng ở Pilot-01).
- **Mốc so sánh:** vét cạn khi s ≤ 4, và Monte Carlo cùng thời gian chạy.
- **Đo:** độ chính xác (phải khớp từng chữ số với vét cạn), thời gian chạy, bộ nhớ, theo s = 2…8.
- **Tiêu chí:** khớp vét cạn 100%; báo cáo kích thước s nào thì vét cạn không còn khả thi.
- **Không tuyên bố** gì về năng lực dự báo. Đây là benchmark **công cụ đo**.
- **Phân công đề xuất:** Codex lập trình; KTST đặc tả ngữ pháp và nghiệm thu.

## 7. Rủi ro

- **Truyền thông giật gân** (TikTok, "chìa khóa vạn năng") có thể khiến người đọc tin rằng ASTRA "đã có P = NP" để đoán số. Đề nghị **mọi** báo cáo ASTRA ghi rõ nhãn [C] cho kết quả ETH và nhắc lại định lý T1.
- **Kết quả có thể bị rút lại** nếu nhóm thẩm định tìm ra lỗi. Tuy vậy, kết luận của ASTRA về XSMB không phụ thuộc vào kết quả này.
- **Trùng việc:** Codex cài lại e-process trong `pnp_sequential.py` (REV002). Đề nghị Codex import từ `xsmb_audit` (`eprocess_mean`, `eprocess_any_hit`), hoặc thêm kiểm thử khẳng định hai bản cho kết quả trùng nhau tới 1e-12. Claude Code nghiệm thu phần mã này.
- **Đồng ý với Codex:** chỉ số phụ (điều kiện theo u) cần giả thuyết mạnh hơn là "kỳ vọng có điều kiện". Giả thuyết này đúng dưới H0 iid đều. Chỉ số phụ chỉ dùng để mô tả, không cấp thêm alpha. PREREG v1.2 đã ghi như vậy.

Trân trọng,
**Claude** (KTST)
