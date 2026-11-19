# SCORE_R2_CLAUDECODE: CHẤM ĐIỂM VÒNG 2 VÀ TỔNG HỢP ĐIỂM HỘI ĐỒNG

| Trường | Nội dung |
|---|---|
| Task | ASTRA-WEB-RFC002, vòng 2 |
| Người chấm | Claude Code |
| Thời điểm đọc | 19/11/2026, 02:10–02:20 UTC (09:10–09:20 ICT) |
| Phân loại | PUBLIC_SAFE (không có chi tiết lỗ hổng, link nội bộ hay thông tin cá nhân) |
| Trạng thái | SUBMITTED. Đây là ý kiến; LK quyết. |

> ⚠️ **Xung đột lợi ích:** Claude Code chấm cả bản của mình (v2.0). Điểm tự chấm để riêng và **không tính** vào tổng hợp hay kiến nghị.

## 1. Ứng viên được chấm (bản mới nhất của mỗi AI, đọc toàn văn)

| Mã | Bản |
|---|---|
| CX | Codex KH_Hợp_nhất_Chốt **v1.1-RC2** |
| GPT | ChatGPT KH_Hợp_nhất_Chốt **v1.0-RC2** |
| CL | Claude KH_HOP_NHAT_CHOT **v6.0** |
| GM | Gemini KH_HOP_NHAT_CHOT **v5** |
| CC | Claude Code KH_HOP_NHAT_CHOT **v2.0** (tự chấm, để riêng) |
| GK | Grok: **chưa có bản vòng 2**, không xếp hạng (không gán 0 điểm) |

## 2. Bộ tiêu chí

- **Dùng bộ tiêu chí 10 mục của Codex**, vì ChatGPT, Codex và Claude đều đã chấm vòng 2 bằng bộ này. Claude Code **rút đề xuất C1–C9 của mình** để các phiếu so sánh được với nhau.
- **Trọng số:** Phạm vi/15 nhánh 10 · UX 8 · Phối hợp 12 · Khoa học 14 · Bảo mật 16 · Tích hợp 12 · Vận hành 12 · Mở rộng 6 · Chi phí 5 · Backlog 5. **Tổng 100.**
- **Thang neo:** 0 = thiếu; ¼ = chỉ có khẩu hiệu; ½ = có thiết kế nhưng thiếu phụ thuộc/test; ¾ = có contract, owner, test; tối đa = nhất quán, khả thi, nghiệm thu rõ.
- **Điểm chấm chất lượng kế hoạch**, không phải tiến độ triển khai.

## 3. Phiếu chấm của Claude Code

| Tiêu chí (tối đa) | CX v1.1 | GPT RC2 | CL v6 | GM v5 | CC v2.0 ⚠️ tự chấm |
|---|---|---|---|---|---|
| Phạm vi / 15 nhánh (10) | 10 | 10 | 10 | 8 | 10 |
| UX (8) | 6 | 7 | 8 | 7 | 8 |
| Phối hợp (12) | 12 | 11 | 11 | 8 | 12 |
| Khoa học / dữ liệu (14) | 14 | 13 | 13 | 9 | 12 |
| Bảo mật / riêng tư (16) | 16 | 15 | 14 | 8 | 14 |
| Tích hợp (12) | 12 | 11 | 11 | 8 | 12 |
| Vận hành / khôi phục (12) | 11 | 11 | 10 | 6 | 11 |
| Mở rộng (6) | 6 | 6 | 6 | 5 | 6 |
| Chi phí / nguồn lực (5) | 5 | 4 | 4 | 2 | 4 |
| Backlog / nghiệm thu (5) | 5 | 4 | 4 | 2 | 4 |
| **Tổng** | **97** | **92** | **91** | **63** | *93* |

Kiểm tra số học: từng cột đã cộng lại; tổng trọng số = 100.

## 4. Lý do điểm (dẫn mục của bản được chấm)

**CX v1.1: 97**
- Cộng:
  - Bảo mật đầy đủ nhất: kiểm JWT của Access (signature/issuer/audience/expiry), quyền theo project/role/action ở server, test vượt rào qua preview/alias/raw/origin. Fallback **không hạ bảo mật**: thiếu auth thì chỉ public demo + relay, khóa ghi (§0, §5).
  - Khoa học: khóa Ledger theo **lịch giao dịch có ngày nghỉ**; baseline "luôn tăng" chỉ áp cho bài toán hướng giá (§6).
  - Có ước lượng 20–35 ngày công + 3–5 ngày review, ghi HYPOTHESIS; RPO/RTO ghi HYPOTHESIS (§7, §9, §14).
  - Backlog P01–P09 có owner, reviewer, phụ thuộc, điều kiện đóng, ngày công; **thứ tự phụ thuộc đúng**: inventory → ADR → vá P0 → migration (§14).
  - Kết luận tách "chất lượng tài liệu / chọn làm master / sẵn sàng vận hành" (§12).
- Trừ:
  - UX −2: chỉ có 6 luồng thao tác dạng chữ, không có bố cục màn hình; văn bản dày.
  - Vận hành −1: chưa có bảng KPI thống nhất.

**GPT RC2: 92**
- Cộng:
  - Bản đồ dự án và phân loại dữ liệu đầy đủ (§5).
  - Danh sách test âm tính dài và cụ thể (anonymous read, forged sender, replay, expired token, cross-project read, stale decision, budget, XSS, restore) (§10).
  - Sổ rủi ro có tiêu chí dừng (§17); quy tắc hợp nhất rõ (§18).
- Trừ:
  - UX −1: wireframe mỗi màn hình chỉ một dòng.
  - Phối hợp −1: Relay Pack và điều kiện bật kênh theo lịch còn ở mức nguyên tắc.
  - Khoa học −1: data-use ledger chưa có trong schema.
  - Tích hợp −1: ít ánh xạ tài sản có sẵn.
  - Vận hành −1: chưa có KPI, RPO/RTO.
  - Chi phí −1: mượn ước lượng của CX.
  - Backlog −1: 12 gói có owner/reviewer nhưng thiếu điều kiện đóng và ngày công từng gói.

**CL v6: 91**
- Cộng:
  - Wireframe cụ thể nhất cho màn hình Điều hành, STOCK và iPhone, **có ghi rõ số liệu minh họa là SIMULATION** (§6.2).
  - Nhãn PROPOSED/DECIDED; data-use ledger trong schema (§10).
  - 8 lỗi S1–S8 có test âm tính (§12.1); có nguồn quota (§13.1).
- Trừ:
  - Vận hành −2: không có bảng KPI.
  - Khoa học −1: Ledger cố định thứ Hai, chưa tính ngày nghỉ (§11.1 P5); holdout ghi FACT nhưng chưa có data-use ledger làm bằng chứng.
  - Bảo mật −2: phương án A chưa kiểm JWT và test vượt rào; vẫn giữ phương án C (token ở client).
  - Chi phí −1, Backlog −1: chưa có ngày công; nhiều gói đồng owner.

**GM v5: 63**
- Cộng: đã bỏ PIN, sửa tên tệp task, tiếp thu Access và tách kho; có PWA và cảnh báo ngân sách 80%/100%.
- Trừ:
  - Bảo mật −8: kích hoạt bot dựa vào metadata Drive + secret dùng chung, không xác thực principal; "feed lọc sạch 100%" không phải bảo đảm an ninh.
  - Vận hành −6: còn "24/7", "kill-switch dừng ngay lập tức" mà không có đo hay cơ chế.
  - Khoa học −5: "6 luật" trộn PIT với tiền đăng ký/N_trials; thiếu strict "<", ex-date, nến đã đóng.
  - Chi phí −3, Backlog −3: "xấp xỉ 0 đồng", "M0 khoảng 3 ngày" không có căn cứ; không có owner/reviewer, schema, điều kiện đóng tách kho.

**CC v2.0: 93, tự chấm, không tính.** Claude Code **chấp nhận** các điểm yếu các AI khác đã chỉ ra:
- **Vòng phụ thuộc trong backlog** (Codex chỉ ra): M0-P5 ADR-AUTH đứng sau việc vá P0, trong khi vá P0 lại cần thiết kế auth. Thứ tự đúng là inventory → ADR → vá → migration, như CX.
- Còn giữ phương án C (token chỉ-đọc ở client); A chưa có kiểm JWT và test vượt rào.
- Ledger cố định thứ Hai, chưa tính ngày nghỉ.
- KPI "100% tái lập khớp" thiếu dung sai số học.
- Chưa có ước lượng ngày công; "timebox 5 ngày" không có căn cứ.

## 5. Tổng hợp điểm Hội đồng vòng 2 (cùng bộ tiêu chí, không tính tự chấm)

Bốn phiếu vòng 2 đã có: **ChatGPT, Codex, Claude, Claude Code**. Gemini và Grok chưa nộp phiếu vòng 2.

| Ứng viên | ChatGPT chấm | Codex chấm | Claude chấm | Claude Code chấm | **Trung vị liên chấm** | Khoảng | (Tự chấm, không tính) |
|---|---|---|---|---|---|---|---|
| **CX v1.1** | 95 | *94 (tự)* | 97 | 97 | **97** | 95–97 | 94 |
| **CC v2.0** | 93 | 93 | 96 | *93 (tự)* | **93** | 93–96 | 93 |
| **GPT RC2** | *92 (tự)* | 95 | 93 | 92 | **93** | 92–95 | 92 |
| **CL v6** | 94 | 90 | *91 (tự)* | 91 | **91** | 90–94 | 91 |
| **GM v5** | 79 | 76 | 64 | 63 | **70** | 63–79 | — |

**Xếp hạng theo trung vị liên chấm:**
1. **Codex v1.1-RC2: 97**
2. Claude Code v2.0: 93 (đồng hạng)
2. ChatGPT v1.0-RC2: 93 (đồng hạng)
4. Claude v6: 91
5. Gemini v5: 70

**Nhận xét:**
- **Codex v1.1 dẫn 4 điểm**, vượt ngưỡng tương đương ±3 đã thống nhất. Trong cả 3 phiếu chấm chéo, Codex không dưới 95.
- Nhóm 91–93 (CC, GPT, CL) chênh nhau ≤ 2 điểm, coi là **tương đương**.
- Kiến nghị của từng người chấm khác nhau:

| Người chấm | Kiến nghị | Điểm cao nhất trong phiếu (không tính tự chấm) |
|---|---|---|
| ChatGPT | Codex | Codex 95 |
| Codex | ChatGPT | ChatGPT 95 |
| Claude | Claude Code (phương án thay thế: Codex) | Codex 97 |
| Claude Code | **Codex** | Codex 97 |

  Điểm chung: **trong mọi phiếu có chấm chéo Codex (ChatGPT, Claude, Claude Code), Codex đều đứng đầu**.
- **Giới hạn:**
  - Chỉ có 4 người chấm; điểm là nhận định chủ quan, không phải khoảng tin cậy thống kê.
  - Gemini và Grok chưa chấm vòng 2; nếu họ nộp, cần tính lại trung vị.

## 6. Kiến nghị chốt của Claude Code

**Chọn Codex v1.1-RC2 làm MASTER dùng chung.**

Lý do:
1. Trung vị liên chấm cao nhất (97) và dẫn vượt ngưỡng tương đương.
2. Mạnh nhất ở ba phần khó sửa nhất về sau: bảo mật, thứ tự phụ thuộc thực thi, ước lượng nguồn lực.
3. Phần yếu (giao diện, KPI) là những đoạn **chép được nguyên** từ các bản khác, không phải viết lại kiến trúc.

**Change request (CR) bắt buộc trước khi phát hành MASTER v1.0:**

| CR | Nội dung | Lấy từ |
|---|---|---|
| CR-1 | Thêm 6 màn hình wireframe (PC/iPhone), hành trình sử dụng và tóm tắt hỏi–đáp | CC v2.0 §0, §5.2; CL v6 §6.2 (nhãn SIMULATION) |
| CR-2 | Thêm bảng KPI có định nghĩa; sửa "tái lập 100%" thành "khớp trong dung sai đã đăng ký theo từng study" | CC v2.0 §12, theo phản biện của Codex |
| CR-3 | Thêm 8 điều kiện đóng tách kho D2-B làm checklist của gói P04 | CC v2.0 §9.3 |
| CR-4 | Thêm data-use ledger vào schema; nhãn PROPOSED/DECIDED | CL v6 §10 |
| CR-5 | Hợp nhất danh sách test âm tính đầy đủ | GPT RC2 §10 |
| CR-6 | Thêm Context Pack và checkpoint phiên (trả lời phản ánh LK 18/11), cảnh báo ngân sách 80%/100% | CC v2.0 §13; GM v5 |
| CR-7 | Thêm bản đồ và phân loại dữ liệu cho mọi workspace | GPT RC2 §5 |

**Vai trò sau khi chọn (đề xuất):**
- ChatGPT: owner master, disposition log, tiêu chí nghiệm thu.
- Codex: kỹ thuật, tích hợp.
- Claude Code: bảo mật, E2E, khôi phục, review.
- Claude: khoa học, schema.
- Gemini: UX, nguồn dữ liệu.
- Grok: phản biện độc lập.

**Cần LK quyết ngay, độc lập với bản được chọn:** D-TRIGGER (tắt kích hoạt theo tên tệp), D-WRITE-OFF (khóa ghi bằng token trên web), D-SECRET (đổi secret). Mọi bản đứng đầu đều xếp đây là P0.

**Sau D-SELECT:**
1. Đóng dấu SELECTED_BY_LK.
2. Đóng băng baseline Codex v1.1-RC2.
3. Owner master áp CR-1…CR-7, kèm changelog và disposition log (giữ dissent).
4. Phát hành MASTER v1.0.
5. Mở backlog M0.

Claude Code **rút v2.0 khỏi vai trò ứng viên master**; v2.0 chuyển thành nguồn cho CR-1, CR-2, CR-3, CR-6.

*Phiếu này không kích hoạt Skill hay API trả phí. Không ký ACK thay AI khác.*
