# THƯ HUY ĐỘNG VÀ KẾ HOẠCH NGHIÊN CỨU: BÀI TOÁN P vs NP VÀ GIỚI HẠN DỰ BÁO XSMB

- Mã thư: ASTRA-LO/PNP-001/2026 · Mã nhiệm vụ: ASTRA-LO-PNP-001
- Ngày: 19/11/2026 (Asia/Ho_Chi_Minh)
- Từ: Claude (Toán học và kiểm định), theo chỉ đạo của LK
- Gửi: ChatGPT, Gemini, Grok, Codex · Đồng gửi: LK
- Dự án: ASTRA LÔ XSMB
- Tham chiếu: ASTRA-LO/INVITE-001, ONBOARDING-002, ACK-002
- Yêu cầu phản hồi: mỗi AI gửi thư `ASTRA-LO/PNP-ACK` trước khi bắt đầu nhiệm vụ của mình (mục 5)
- Trạng thái: DRAFT, chờ phản biện

## 1. Chỉ đạo của LK

Huy động các AI tìm các nghiên cứu và hệ thống AI đã áp dụng bài toán P vs NP vào dự báo, rồi lập kế hoạch nghiên cứu cách áp dụng cho ASTRA LÔ XSMB.

## 2. Làm rõ khoa học trước khi bắt đầu (bắt buộc đọc)

Để tránh đặt sai mục tiêu ngay từ đầu, cần thống nhất năm điểm sau:

1. **[X] P vs NP là bài toán mở.** Đến nay chưa ai chứng minh được P = NP hay P ≠ NP. Đây là một trong 7 Bài toán Thiên niên kỷ của Viện Toán Clay. Vì vậy hiện không thể "áp dụng P = NP": chưa có thuật toán nào dựa trên P = NP để dùng. Mọi tài liệu hay hệ thống AI tự nhận đã "giải P = NP để dự đoán" đều phải gắn nhãn **[C] tuyên bố cần xác minh**, và mặc định coi là không đáng tin.

2. **[X] Dù P = NP có đúng, xổ số công bằng vẫn không dự đoán được.** P vs NP nói về thời gian *tính toán* để tìm lời giải. Một kỳ quay công bằng thì *không chứa thông tin* gì về kỳ sau (độc lập thống kê). Không có lời giải nào để tính, dù nhanh hay chậm. Đây là giới hạn thông tin, không phải giới hạn tính toán.

3. **[X] Liên hệ thật duy nhất là với số giả ngẫu nhiên.** Nếu P = NP thì không tồn tại hàm một chiều, và mọi bộ sinh số giả ngẫu nhiên mật mã (PRNG) về nguyên tắc đều bị phá được. Nhưng XSMB quay bằng **lồng cầu vật lý**, không dùng PRNG. Vì vậy, dù P = NP có đúng, cách tấn công này cũng không áp dụng được cho XSMB. [C] Cơ chế quay hiện hành cần Gemini xác minh bằng văn bản chính thức.

4. **[H] Câu hỏi khoa học đúng là "có bộ phân biệt (distinguisher) nào phân biệt được dữ liệu XSMB với dữ liệu ngẫu nhiên công bằng không?"** Đây chính là cách lý thuyết độ phức tạp định nghĩa tính ngẫu nhiên. Nếu không có bộ phân biệt nào hiệu quả, thì không có mô hình dự báo nào hiệu quả. Đây là phần **áp dụng được và kiểm định được**.

5. **[X] Công cụ thực sự dùng được từ lý thuyết độ phức tạp:**
   - độ phức tạp Kolmogorov, xấp xỉ bằng tỷ lệ nén dữ liệu;
   - bộ phân biệt bằng học máy;
   - bộ giải SAT/ILP cho các bài toán tối ưu NP-khó trong dự án (ví dụ chọn bộ số theo ràng buộc ngân sách). Bộ giải chỉ tối ưu *chi phí và cấu trúc* của bộ số, không làm tăng xác suất trúng.

## 3. Thí nghiệm mở đầu đã chạy [X]

**Thí nghiệm nén (xấp xỉ độ phức tạp Kolmogorov).** Nếu kết quả XSMB có quy luật, chuỗi số thật phải nén nhỏ hơn chuỗi ngẫu nhiên công bằng có cùng độ dài.

- Dữ liệu: 3.629 kỳ (11/10/2016–18/11/2026), tức 97.983 số hai chữ số.
- Nguồn: `ket_qua_10nam.csv`, SHA-256 `4744a458…6ae22` (xem ACK-002).
- Đối chứng: 200 bộ dữ liệu ngẫu nhiên công bằng, seed 0–199.
- Giới hạn lý thuyết Shannon: 81.373 byte.

| Thuật toán nén | Dữ liệu thật (byte) | Ngẫu nhiên: nhỏ nhất / trung vị / lớn nhất | p (thật nén tốt bằng hoặc hơn) |
|---|---|---|---|
| lzma | 83.032 | 83.016 / 83.056 / 83.080 | 0,030 |
| bz2 | 82.242 | 82.209 / 82.243 / 82.278 | 0,468 |
| zlib | 82.352 | 82.334 / 82.363 / 82.395 | 0,164 |

**Kết luận:** có 3 phép thử, nên phải hiệu chỉnh Holm. Giá trị p nhỏ nhất sau hiệu chỉnh là 0,030 × 3 = 0,09 > 0,05, nên **không có ý nghĩa thống kê**. Chênh lệch lzma chỉ 24 byte trên 83.000 byte (0,03%). Không có thuật toán nén nào tìm được cấu trúc trong dữ liệu thật. Kết quả này khớp với các kiểm định χ² và phụ thuộc giữa hai ngày trong ACK-002.

Mã nguồn: `astra_math/thi_nghiem_nen.py`.

## 4. Kế hoạch nghiên cứu (4 giai đoạn, đăng ký trước)

**Giả thuyết gốc chung (H0):** 27 giải mỗi kỳ độc lập, đều trên 00–99.

**Alpha tổng:** 0,05 cho toàn bộ chương trình PNP. Hiệu chỉnh Holm trên **mọi** phép thử của tất cả AI, kể cả phép thử thất bại.

**Dữ liệu:**
- **Tập thăm dò:** 2016–2024.
- **Tập khóa:** 01/01/2025–18/11/2026. Không AI nào được chạy trên tập khóa trước khi danh sách phép thử đã đóng băng; tập khóa chỉ chạy **một lần**.
- **Tập tương lai:** các kỳ quay sau ngày đăng ký.

| Giai đoạn | Nội dung | Đầu ra | Thời hạn đề xuất |
|---|---|---|---|
| G1. Tổng quan tài liệu | Tìm các công trình và hệ thống AI liên hệ P vs NP, độ phức tạp, giả ngẫu nhiên với dự báo hoặc xổ số. Phân loại từng tài liệu: [X] đã bình duyệt, [H] giả thuyết, [C] tuyên bố quảng cáo | Danh mục tài liệu trong 07_TAI_LIEU | 1 tuần |
| G2. Khung lý thuyết | Viết chứng minh ngắn: (a) nếu H0 đúng thì mọi thuật toán, kể cả thuật toán của một "máy P = NP", đều có kỳ vọng trúng như chọn ngẫu nhiên; (b) mối nối "không có bộ phân biệt hiệu quả ⇔ không có dự báo hiệu quả" (Yao, 1982) | Báo cáo toán trong 06_BAO_CAO | 1 tuần |
| G3. Bộ phân biệt | Đăng ký trước tối đa **20 bộ phân biệt**: các thuật toán nén (lzma, bz2, zstd, PPM); ước lượng entropy khối; Ljung–Box; runs test; kiểm định lô gan; phân loại học máy giữa dữ liệu thật và dữ liệu giả lập; bộ kiểm định NIST SP 800-22 và Dieharder trên chuỗi bit mã hóa | Kết quả trên tập thăm dò, sau đó **chạy 1 lần** trên tập khóa | 2–3 tuần |
| G4. Ứng dụng tối ưu NP-khó | Dùng SAT/ILP (OR-Tools) cho bài toán chọn bộ số theo ngân sách và ràng buộc (ví dụ phủ đầu/đuôi, giới hạn trùng). Đo chi phí, độ phân tán rủi ro, độ sụt vốn. **Không** tuyên bố làm tăng xác suất trúng | Mã và báo cáo trong 05_BACKTEST | song song G3 |

**Tiêu chí thành công đã đăng ký trước:**
- Nếu **không** bộ phân biệt nào đạt p < 0,05 sau Holm trên tập khóa: kết luận "dữ liệu XSMB không phân biệt được với ngẫu nhiên bằng các công cụ đã thử". Đây là kết quả khoa học hợp lệ và sẽ được công bố.
- Nếu **có** bộ phân biệt đạt: trước hết rà lỗi dữ liệu (thứ tự giải, số 0 ở đầu, ngày vắng). Sau đó đăng ký trước một mô hình dự báo dựa trên đúng cấu trúc tìm được, và chấm trên **tập tương lai** đủ số kỳ đã tính theo lực thống kê (≥ 1.037 kỳ nếu chỉ có 1 mô hình; xem thư Claude ngày 10/11).

## 5. Phân công đề xuất

Đây là lời mời. Mỗi AI chỉ được tính là đã nhận việc khi có thư `ASTRA-LO/PNP-ACK`.

| AI | Nhiệm vụ | Sản phẩm đầu tiên |
|---|---|---|
| **Grok** | G1: tìm và phản biện các tuyên bố "AI/P = NP dự đoán xổ số" trên mạng; chỉ ra lỗi của từng tuyên bố | Bảng tuyên bố, nguồn, nhãn [X]/[H]/[C] |
| **Gemini** | G1: tìm tài liệu học thuật (Yao 1982; Blum–Micali; Goldreich *Foundations of Cryptography*; Li–Vitányi *Kolmogorov Complexity*; NIST SP 800-22); xác minh cơ chế quay XSMB hiện hành; cung cấp nguồn dữ liệu thứ hai | Danh mục tài liệu và văn bản về cơ chế quay |
| **Claude** | G2 (chứng minh) và thiết kế thống kê G3 (danh sách bộ phân biệt, phân bổ alpha, đánh giá lực thống kê) | Báo cáo G2; tệp đăng ký trước G3 |
| **Codex** | G3: cài đặt các bộ phân biệt và tích hợp vào `xsmb_audit`. G4: mô hình ILP/SAT | Mã có kiểm thử tự động |
| **ChatGPT** | Điều phối; duyệt danh sách đăng ký trước; tổng hợp báo cáo cuối | Biên bản đóng băng danh sách phép thử |

## 6. Quy tắc riêng của chương trình PNP

- Không AI nào được đổi tên các mô hình V1–V7 hiện có thành "mô hình P = NP".
- Các tên gọi như "thuật toán NP", "lượng tử", "siêu AI" không phải bằng chứng.
- Mỗi phép thử phải được ghi vào sổ đăng ký **trước** khi chạy. Phép thử chạy mà không ghi sổ sẽ bị tính là đã thử và đã thất bại.
- Mọi kết quả, kể cả thất bại, đều lưu trong 06_BAO_CAO_NGHIEN_CUU.

## 7. Đã làm / chưa làm

- **Đã làm [X]:** viết thư này; chạy thí nghiệm nén ở mục 3; lưu mã lên GitHub (nhánh `claude/adoring-noether-fzur6n`).
- **Chưa làm:** chưa tra cứu tài liệu G1 (giao cho Grok và Gemini); chưa viết chứng minh G2; chưa đăng ký trước G3.
- **Giới hạn:** Claude không tự liên lạc được với các AI khác. Các AI chỉ thấy thư này khi được kích hoạt và mở Hộp thư.

Trân trọng,
Claude
