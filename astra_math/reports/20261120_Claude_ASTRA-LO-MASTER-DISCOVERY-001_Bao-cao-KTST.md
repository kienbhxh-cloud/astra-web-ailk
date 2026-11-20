# ASTRA-LO/MASTER-DISCOVERY-001 — BÁO CÁO NGHIÊN CỨU ĐỘC LẬP CỦA CLAUDE (KTST)

- **Ngày:** 20/11/2026, 23:00 ICT · **Phiên bản:** 1.0 · **Từ:** Claude (phiên chat, KTST: toán học, kinh tế lượng, kiểm định, phản biện)
- **Gửi:** LK · **Đồng gửi:** ChatGPT, Gemini, Grok, Codex, Claude Code
- **Dữ liệu:** bản v2 `xsmb_2005-10-01_to_2026-11-19_clean_v2_fix20060921.csv` (SHA-256 `85aabd57…27535909`), 7.622 kỳ.
- **Mã:** `astra_math/pnp/discovery/` (`tran_loi_the.py`, `tre_theo_thu.py`) và `astra_math/pnp/soicau/`. Nhánh `claude/astra-math-research-wdvww8`.
- **Nhãn:** [X] đã chạy, có bằng chứng · [H] giả thuyết · [C] cần xác minh.
- **Lưu ý:** toàn bộ kết quả trong báo cáo là thăm dò hồi cứu. Chỉ E-1 đang được chấm tương lai.

---

## 1. Vì sao các quy luật ngắn xuất hiện (Nhiệm vụ 1)

**1.1. Mẫu hình ngắn sinh ra từ ngẫu nhiên là chắc chắn, không phải ngoại lệ** [X]
- Có 11.342 cầu vị trí. Xác suất một cầu ăn trong một ngày là p = 23,77%. Vì vậy, **mỗi ngày**, hoàn toàn do ngẫu nhiên:

| Số kỳ cầu đã ăn liên tiếp | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|
| Số cầu như vậy mỗi ngày | 152 | 36 | **8,6** | 2,0 | 0,5 | 0,1 |

- Nói cách khác: hôm nào cũng có khoảng 9 cầu "chạy đều 5 ngày", và cứ hai ngày lại có một cầu chạy 7 ngày, **không cần bất kỳ quy luật nào**.
- Con người nhìn thấy những cầu này nhưng **không đếm** được hàng vạn cầu đã gãy. Đây là thiên lệch chọn mẫu: thấy người sống sót, quên người đã mất.

**1.2. Vì sao cầu "đang thông" thì đột ngột gãy** [X]
- Sau mỗi kỳ, cầu ăn tiếp với xác suất đúng bằng p, **bất kể đã ăn bao nhiêu kỳ trước đó**. Dữ liệu thật xác nhận điều này (SOICAU-001): cầu đã ăn 4–8 kỳ thì kỳ sau ăn 23,4–24,4%.
- Vì vậy độ dài chuỗi ăn theo phân phối hình học với trung bình 1/(1 − p) ≈ 1,3 kỳ.
- Cầu không "gãy vì hết vận". Cầu chưa bao giờ có vận.

**1.3. Cần bao nhiêu dữ liệu** [X]
- Đã tính ở PREREG v1.2. Với lợi thế vừa đủ hòa vốn (+4,17% số nháy), cần khoảng **4.244 kỳ** (gần 12 năm) để đạt lực thống kê 80%.
- Với "+1 điểm %" tỷ lệ kỳ trúng, cần 19.570 kỳ.
- Một quy luật "đúng 10 tuần liền" gần như không mang thông tin gì.

**1.4. Bốn loại quy luật (theo yêu cầu phân biệt của LK)**

| Loại | Định nghĩa | Ví dụ ở ASTRA |
|---|---|---|
| Mô tả | Mẫu hình có thấy trong dữ liệu đã xem | "Cầu (12, 57) ăn 7 ngày liền" |
| Toán học | Đúng theo định nghĩa, với **mọi** dãy số | "Trong 7 kỳ, một chữ số d có mặt ở đầu hoặc đít đề với xác suất 77,1%" (SOICAU-002) |
| Thống kê | Khác ngẫu nhiên sau hiệu chỉnh đa kiểm định | Phụ thuộc thời gian của E-1 (mục 2.2) |
| Dự báo | Có lợi thế trên dữ liệu **chưa từng xem**, đủ lớn để có ý nghĩa | **Chưa có quy luật nào** |

## 2. Phát hiện mới: đo TRẦN lợi thế bằng thành phần phương sai (Nhiệm vụ 2–3, nhánh B, C, H)

**Câu hỏi.** Thay vì thử từng cầu, em hỏi thẳng: dữ liệu **chứa tối đa bao nhiêu thông tin dự báo** dưới dạng "số nào đang có xác suất cao hơn"?

**2.1. Mô hình** [X]
- Mỗi số n có xác suất mỗi lượt quay là θ_n(t) = 0,01·(1 + e_n(t)).
- Phần e_n(t) gồm một phần **cố định** và một phần **thay đổi theo thời gian**.
- Ước lượng: chia dữ liệu thành khối W kỳ. Gọi C là số nháy của mỗi số trong khối. Hiệp phương sai giữa độ lệch của C ở **hai khối liền nhau**, chuẩn hóa theo bình phương kỳ vọng, chính là phương sai của phần e **bền vững, tức là dự báo được**.
- **Null:** hoán vị thứ tự kỳ 300 lần. Cách này giữ nguyên lệch cố định nhưng phá phụ thuộc thời gian.

**2.2. Kết quả**

| Khối W | Hiệp phương sai trễ 1 (×10⁻⁴) | Null: trung bình ± sd | p một phía | SD phần dự báo được của e | **Trần** (biết chính xác θ) | **Đạt được** từ dữ liệu |
|---|---|---|---|---|---|---|
| 7 kỳ | 36,5 | −0,0 ± 15,6 | **0,007** | 6,0% | 14,1% | **1,17%** |
| 30 kỳ | 9,2 | 0,6 ± 6,9 | 0,086 | 2,9% | 6,8% | 0,57% |
| 90 kỳ | 9,9 | 0,2 ± 4,3 | **0,017** | 3,1% | 7,3% | **1,11%** |
| 180 kỳ | 2,3 | 0,5 ± 3,2 | 0,25 | 1,4% | 3,2% | 0,31% |
| 365 kỳ | −0,7 | 0,4 ± 2,0 | 0,71 | 0 | 0 | 0 |

- **Phần lệch cố định:** SD khoảng 0,6%. Phù hợp với χ² toàn bộ, p = 0,27.
- **Holm cho 5 cửa sổ:** W = 7 đạt (0,007 × 5 = 0,033). W = 90 không đạt sau hiệu chỉnh (0,017 × 4 = 0,066).

**2.3. Diễn giải**
- [H, bằng chứng thăm dò mạnh] Có **phụ thuộc thời gian yếu**: một số về nhiều hơn mức trung bình trong vài tuần thì tuần sau vẫn hơi nhỉnh. Hiệu ứng tắt dần sau khoảng 6 tháng.
- Điều này **khớp** với E-1 (nóng 90 kỳ hơn ngẫu nhiên +1,75% số nháy) và với SOICAU-001 (cầu vị trí cao hơn mốc hoán vị 0,05 điểm %).
- **Trần 7–14%** chỉ đạt được nếu **biết chính xác** θ của từng số tại từng thời điểm. Điều này không thể làm được, vì phải ước lượng θ từ chính số đếm vốn rất nhiễu, nên tín hiệu bị pha loãng.
- **Lợi thế đạt được thực tế** (chọn 5 số theo số đếm của W kỳ trước) là **0,3–1,2% số nháy**, so với mức **4,17%** cần để hòa vốn ở giá 22.500đ.
- Kết hợp nhiều cửa sổ một cách tối ưu ước lượng cũng chỉ đạt khoảng 2% [H]. **Vẫn lỗ.**

**2.4. Hệ quả quan trọng nhất của báo cáo** [X / H]
- **Mọi phương pháp dựa trên tần suất gần đây** (lô nóng/lạnh, lô rơi, lô gan, nuôi khung, cầu chu kỳ ngắn) đều chỉ là những cách khác nhau để khai thác **cùng một** tín hiệu yếu này. Vì vậy chúng **không thể vượt trần trên**.
- Đây là một **giới hạn trên cho cả một họ phương pháp**, không phải bác bỏ từng cầu một.
- **Giới hạn của kết luận:** trần này áp dụng cho thông tin nằm ở mức "số nào đang có xác suất cao". Cấu trúc **phi tuyến** khác (quan hệ giữa các vị trí, giữa các giải) do F1 (SAT), WP2 (nén) và SOICAU kiểm. Đến nay những kiểm tra đó đều âm tính.

## 3. Giả thuyết vật lý mới: mỗi đài có lệch riêng (nhánh H) — BÁC BỎ [X]

- **Cơ sở:** XSMB quay luân phiên theo thứ trong tuần: Hà Nội (thứ 2, thứ 5), Quảng Ninh, Bắc Ninh, Hải Phòng, Nam Định, Thái Bình. Nếu mỗi đài có thiết bị hoặc bộ bóng riêng, sẽ có (a) khác biệt tần suất theo thứ, và (b) phụ thuộc mạnh nhất ở trễ đúng 7, 14, 21 ngày.
- **Kiểm định (a):** bảng 7 thứ × 100 số cho χ² = 608,8 với 594 bậc tự do, **p = 0,33**. Không có khác biệt.
- **Kiểm định (b):** hiệp phương sai trễ L = 1…21 **ngày lịch**, so với null hoán vị 200 lần:
  - Trễ 7, 14, 21 cho z = +0,39; −0,22; −0,54, **không có gì**.
  - Trễ 1 và 8 có z ≈ +2,4, nhưng sau hiệu chỉnh 21 trễ thì không đạt.
- **Kết luận:** không có lệch theo đài. Phụ thuộc ở mục 2 trải đều trên trễ ngắn. Điều này phù hợp với giả thuyết **trôi chậm của thiết bị nói chung** (ví dụ mòn bóng, thay bộ bóng) [H], chưa có bằng chứng vật lý trực tiếp.
- **Đề nghị Gemini:** tìm văn bản về chu kỳ thay bóng và lồng cầu của Công ty XSKT Thủ đô. Nếu có ngày thay thiết bị, có thể kiểm định **điểm thay đổi** (change-point): độ lệch phải "nhảy" đúng vào những ngày đó.

## 4. Danh mục hướng nghiên cứu (đã biết và mới) với trạng thái

| Nhánh | Hướng | Trạng thái |
|---|---|---|
| A | Cầu vị trí, ghép cầu (11.342 cầu) | [X] bác bỏ lợi thế (SOICAU-001) |
| A | Tổng, đầu, đuôi, chạm (tổng đề) | [X] bác bỏ (SOICAU-002, 002b) |
| B | Độc lập trễ 1; χ² vị trí giải | [X] âm tính (Claude Code) |
| B | **Thành phần phương sai / trần lợi thế** | [X] **mới**, mục 2 |
| B | Change-point theo thời gian thay thiết bị | [H] đề xuất, chờ dữ liệu từ Gemini |
| C | Lệch theo đài / thứ trong tuần | [X] bác bỏ, mục 3 |
| C | Mô hình không gian trạng thái (Dirichlet có hệ số quên, Kalman) | [H] đề xuất: là phiên bản tối ưu của E-1; chỉ chạy tương lai |
| E, G | F1-v1 SAT/MaxSAT (606.032 luật), τ_s | [X] khung đã có, chờ cổng G2 |
| F | Nén lzma/bz2/zlib | [X] âm tính (Claude Code, p sau hiệu chỉnh 0,09) |
| G | P vs NP / ETH | [X] không giúp dự báo (định lý T1, THEORY_REVIEW) |
| — | E-1 (nóng 90, e-process) | [X] **đang chấm tương lai** từ 20/11/2026 |

## 5. Giả thuyết mới có công thức, sẵn sàng kiểm chứng tương lai (Nhiệm vụ 5)

**H-DRIFT** (đăng ký trước sau khi LK duyệt; chưa chạy tương lai):
- **Ước lượng:** θ̂_n(t) = (Σ_k λ^k C_n(t−k) + α) / (Σ_k λ^k·27 + 100α), với λ = 0,99 (bán rã khoảng 70 kỳ) và α = 2,7 (prior).
- **Chọn số:** top 5 theo θ̂.
- **Chấm:** e-process trên số nháy, μ = 1,35, ngưỡng W ≥ 20m.
- **Kỳ vọng [H]:** nếu tín hiệu ở mục 2 là thật, H-DRIFT sẽ nhỉnh hơn E-1 khoảng 0,2–0,5% số nháy. Vẫn **dưới mức hòa vốn**.
- **Mục đích:** xác nhận khoa học xem tín hiệu có thật không. **Không** phải để có lãi.

## 6. Phản biện về khả năng tạo lợi thế (Nhiệm vụ 6)

1. Tín hiệu duy nhất vượt hiệu chỉnh là **phụ thuộc thời gian yếu**. Lợi thế khai thác được từ nó (≈ 1–2% số nháy) **nhỏ hơn 2–4 lần** mức cần để hòa vốn (4,17%).
2. **Tỷ lệ trúng cao không phải lợi thế.** Ví dụ: quy luật tổng đề đúng 77,5%, trong khi chọn ngẫu nhiên đúng 77,1%. Mọi con số "70–90%" phải đi kèm mốc ngẫu nhiên.
3. Với dữ liệu hiện có, **không có phương pháp nào trong họ "tần suất gần đây" có thể có lãi**. Khẳng định này dựa trên trần ở mục 2, không phụ thuộc vào việc thử bao nhiêu cầu.

## 7. Đề xuất bổ sung Master Skill và bộ máy khám phá tự động (Nhiệm vụ 3, 7)

1. **Bước bắt buộc "Kiểm trần" trước mọi tìm kiếm.** Chạy `tran_loi_the.py` trên dữ liệu mới nhất. Nếu lợi thế đạt được cao nhất < 4,17% thì ghi rõ: "mọi phương pháp họ tần suất không thể có lãi". Tiết kiệm ngân sách thử nghiệm.
2. **Mọi tuyên bố phải điền đủ 7 mục** như mục VI của thư LK: sự kiện nào, bao nhiêu số, khung bao lâu, lý thuyết hay thực nghiệm, n và khoảng tin cậy, mức hơn ngẫu nhiên, ngoài mẫu hay không. Kèm thêm **số nháy so với 1,35 và so với 1,40625 (hòa vốn)**.
3. **Kiểm tra dữ liệu tự động:** `duplicate_draws`, `load_draws(strict_lengths=True)`. Từ nay mọi AI tự xác minh và sửa lỗi dữ liệu ngay, không chờ AI khác.
4. **Thứ tự ưu tiên cho bộ máy khám phá (Codex):** (a) kiểm trần → (b) WP2 bộ phân biệt → (c) F1 SAT với τ_s → (d) chỉ chuyển sang tiến cứu khi vượt τ_s **và** lợi thế ước lượng > 4,17%.

## 8. Kết luận trung thực

AI **đã** tìm ra một cấu trúc mà con người không đo được bằng mắt: một phụ thuộc thời gian rất yếu trong tần suất các số, kèm **lượng hóa chính xác** độ lớn của nó.

Chính việc lượng hóa đó cho thấy cấu trúc này **quá nhỏ để tạo lợi nhuận**. Cấu trúc này giải thích vì sao các phương pháp "lô nóng" đôi khi có vẻ đúng hơn ngẫu nhiên một chút, nhưng người chơi vẫn **lỗ khoảng 4% số tiền cược** về lâu dài.

Trân trọng,
**Claude** (KTST)
