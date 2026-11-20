# 20261120 — CLAUDE CODE — MASTER-DISCOVERY-001: Báo cáo nghiên cứu độc lập

- Từ: Claude Code (vai trò: triển khai độc lập, tái lập, đối chiếu Codex) · Gửi: LK · Đồng gửi: ChatGPT, Claude KTST, Gemini, Grok, Codex
- **Phiên bản 1.0, ngày 20/11/2026.** Dữ liệu SRC-002B (v2), SHA-256 `85aabd57…5909`, 7.622 kỳ (01/10/2005–19/11/2026).
- Mã nguồn: nhánh `claude/adoring-noether-fzur6n`, thư mục `PNP_XSMB_RESEARCH/`.
- Nhãn: [X] đã chạy, có bằng chứng · [H] giả thuyết · [C] chưa xác minh.

## 1. Vì sao "quy luật ngắn" xuất hiện (Nhiệm vụ 1)

### 1.1 Thí nghiệm H-STREAK: toàn bộ 11.342 cầu lô vị trí [X]

**Cách lập cầu.** Chọn 2 vị trí chữ số (i ≠ j) trong 107 chữ số của bảng kết quả kỳ t. Ghép thành N = 10·d_i + d_j và dự báo "lô N về ở kỳ t+1". Duyệt **mọi** cặp vị trí, **mọi** kỳ: tổng cộng 86,4 triệu lượt dự báo. Mã: `discovery_cau_vi_tri.py` (chạy 4,4 giây). Không có tham số nào được tinh chỉnh.

**Tỷ lệ trúng kỳ tới, chia theo số ngày cầu đã thông liên tiếp (k):**

| k (ngày cầu đã chạy) | Số lượt (thật) | **Tỷ lệ trúng: dữ liệu THẬT** | Tỷ lệ trúng: GIẢ LẬP ngẫu nhiên |
|---|---|---|---|
| 0 (cầu vừa gãy, hoặc mới) | 65.788.467 | 23,90% | 23,77% |
| 1 | 15.722.217 | 23,87% | 23,78% |
| 2 | 3.752.671 | 23,86% | 23,76% |
| 3 | 895.161 | 23,77% | 23,81% |
| **4** | 212.738 | **23,69%** | 23,87% |
| **5** | 50.395 | **23,80%** | 24,09% |
| 6 | 11.993 | 23,90% | 23,19% |
| 7 | 2.866 | 23,45% | 23,15% |
| 8 | 671 | 24,44% | 23,23% |
| 9 | 164 | 20,73% | 28,48% |
| 10 | 34 | 11,76% | 18,60% |

Mốc so sánh:
- lý thuyết: một lô cho trước về trong kỳ với xác suất **23,77%**;
- thực nghiệm theo u: **23,84%**.

**Kết luận [X]:**
1. Tỷ lệ trúng **không tăng** theo số ngày cầu đã chạy. Đường kết quả **phẳng**, giống hệt dữ liệu ngẫu nhiên.
   - "Nuôi cầu đã thông 4–5 ngày" cho 23,69% và 23,80%, **không cao hơn** cầu mới.
   - Ở k ≥ 8, số lượt quá ít nên tỷ lệ dao động mạnh, ở cả dữ liệu thật lẫn giả lập.
2. **Vì sao ai cũng thấy "cầu đang chạy":** có 11.342 cầu, mỗi cầu trúng một ngày với xác suất 0,2377. Vì vậy mỗi ngày **luôn có** khoảng 11.342 × 0,2377ᵏ cầu đang chạy k ngày, dù kết quả hoàn toàn ngẫu nhiên:

| Chạy liên tiếp | Kỳ vọng ngẫu nhiên (cầu/ngày) | Quan sát trên dữ liệu thật |
|---|---|---|
| ≥ 3 ngày | 152 | — |
| ≥ 4 ngày | 36 | — |
| ≥ 5 ngày | **8,6** | **8,65** |
| ≥ 6 ngày | 2,0 | — |
| ≥ 7 ngày | 0,49, tức cứ khoảng 2 ngày có 1 cầu chạy 7 ngày | — |

   Cầu dài nhất trong 21 năm: thật **12 ngày**, giả lập **13 ngày**.
3. **"Thông nhiều ngày rồi đột ngột gãy"** là hệ quả tất yếu. Ngày tiếp theo, cầu nào cũng chỉ còn 23,8% khả năng trúng, nên chuỗi nào rồi cũng gãy, và gãy đúng nhịp của xác suất hình học.
4. **Ghi chú kỹ thuật.** Các lượt dự báo tương quan với nhau, vì cùng ngày và cùng số N. Vì vậy không dùng sai số chuẩn nhị thức đơn thuần để tính p-value cho bảng trên. Đối chứng giả lập (cùng mã, cùng kích thước) cho thấy mức dao động là như nhau.

### 1.2 Trả lời 6 câu hỏi của Nhiệm vụ 1

| Câu hỏi | Trả lời | Căn cứ |
|---|---|---|
| 1. Vì sao con người phát hiện mẫu ngắn? | Não người tìm mẫu rất mạnh, và **xem rất nhiều** cầu cùng lúc (hàng nghìn vị trí, hàng chục cách ghép). Người ta nhớ cầu thắng, quên cầu thua. | §1.1: kỳ vọng 8,6 cầu chạy ≥ 5 ngày mỗi ngày [X] |
| 2. Mẫu nào hình thành hoàn toàn do ngẫu nhiên? | Mọi mẫu trong bảng §1.1. Ngoài ra còn tổng đề, đầu/đít trong 7 kỳ (≈ 77%) [X], bộ 5 có ≥ 1 số trúng (≈ 75%) [X], và "cầu thắng" khi thử 200 cầu [X] | Thư tổng đề; PREREG; benchmark phủ |
| 3. Vì sao cầu thông rồi gãy? | Xác suất trúng ngày tới không đổi (§1.1 kết luận 3). Độ dài chuỗi theo phân phối hình học | [X] |
| 4. Cần bao nhiêu dữ liệu? | Lợi thế vừa đủ hòa vốn (+4,17% số nháy): khoảng **3.700 kỳ**, tức ~10 năm tiến cứu. +10%: ~690 kỳ. +20%: ~180 kỳ | QD-001-REVIEW (Claude Code), Gemini v2.1 [X] |
| 5. Có phụ thuộc giữa kỳ, giải, vị trí không? | WP2: 13 phép, **không bác bỏ** H0 sau Holm. Theo thời gian (D06–D10) p ≥ 0,25 | WP2-RESULT v1/v2 [X] |
| 6. Yếu tố vật lý? | Hai dấu hiệu nhỏ, chưa có ý nghĩa sau hiệu chỉnh: (a) ít đuôi trùng trong kỳ hơn lý thuyết (z ≈ 4,4 sau khi đã xem dữ liệu; mạnh ở 2005–2020, không có ở 2021–2026); (b) hàng trăm thiếu chữ số 0 (−4,7 SE). **Cả hai không chứa thông tin về số nào sẽ về** | WP2 chẩn đoán [H] |

**Bốn loại "quy luật"** (theo yêu cầu phân biệt):
1. **Mô tả:** "cầu X đã thông 6 ngày". Luôn có, vô nghĩa với dự báo.
2. **Toán học:** "P(≥ 1 số trong bộ 5 về) = 74,97%". Đúng tuyệt đối, nhưng không đem lại lợi thế.
3. **Thống kê:** "D04 có p = 0,008". Có thật trong dữ liệu, nhưng không qua được hiệu chỉnh đa kiểm định.
4. **Có năng lực dự báo:** phải vượt mốc ngẫu nhiên trên **tương lai** (e-process). **Hiện chưa có quy luật nào đạt mức này.**

## 2. Danh mục những gì đã kiểm (Nhiệm vụ 2 và 4, phần Claude Code)

| Mã | Phương pháp (nhánh) | Dữ liệu | Kết quả | Tệp |
|---|---|---|---|---|
| CC-01 | χ², tự tương quan trễ 1, cầu "lặp đề" (B) | thật 10 năm và 21 năm | không lệch [X] | `astra_math/kiem_tra_du_lieu_that.py` |
| CC-02 | Nén lzma / bz2 / zlib, Kolmogorov (F) | thật 10 năm | không có cấu trúc [X] | `astra_math/thi_nghiem_nen.py` |
| CC-03 | WP2: 13 bộ phân biệt (A, B, F, H) | thật 21 năm, v1 và v2 | không bác bỏ [X] | `astra_math/wp2_distinguishers.py` |
| CC-04 | Phủ tối đa CP-SAT, tham lam, tần suất (G) | giả lập | tối ưu mạnh hơn thì học nhiễu nhiều hơn [X] | `coverage_benchmark.py` |
| CC-05 | Kiểm toán top5_90, top5_365, MILP maxcov (G) | thật (của ChatGPT) | không vượt ngẫu nhiên; nghiệm MILP 0,5 giây kém hơn ngẫu nhiên [X] | `audit_chatgpt_003_004.py` |
| CC-06 | Tổng đề < 10 → đầu/đít trong 7 kỳ (dân gian) | thật 21 năm | 77,51% so với 77,12% ngẫu nhiên, p = 0,65 [X] | `test_quy_luat_tong_de*.py` |
| CC-07 | **H-STREAK: 11.342 cầu vị trí, nuôi cầu** (dân gian, A, B) | thật 21 năm và giả lập | đường phẳng, không lợi thế [X] | `discovery_cau_vi_tri.py` |
| CC-08 | e-process QD-001 (B) | giả lập | hợp lệ (Ville), lực thống kê khớp KTST và Gemini [X] | `eprocess_check.py` |
| CC-09 | Nghiệm thu rule_count, xsmb_exact, REV002 (G, kiểm thử) | — | đạt; tìm ra lỗi L1, L2, B1 [X] | các thư nghiệm thu |

**Chưa làm, đề xuất cho các AI khác:**
- Transformer, mô hình chuỗi (D): Codex.
- Hồi quy ký hiệu (symbolic regression) và GP (E): Codex, ngân sách ≤ 500 ứng viên.
- Mô hình chuyển trạng thái / Markov ẩn (C): V7 đã có HSMM, cần tái lập.
- Khôi phục 14 nhóm phương pháp của Gemini và V1–V7 (Nhiệm vụ 4): Gemini và ChatGPT.

Claude Code sẵn sàng **tái lập độc lập** từng mục khi có mã.

## 3. Giả thuyết mới có công thức (Nhiệm vụ 2, mục 3)

**H-NEW-1 (Nhánh H, vật lý): "độ đa dạng đuôi trong ngày".**
- Biến: u_t = số đuôi khác nhau của kỳ t.
- H1: E[u_t] > 23,7657, tức các giải trong cùng một kỳ "đẩy nhau" ra khỏi các đuôi trùng.
- Kiểm định: e-process tiến cứu trên Y_t = u_t − 23,7657, mỗi bước bị chặn trong khoảng [−23,8; +3,3], ngưỡng 20.
- Ý nghĩa: nếu đúng, đây là bằng chứng thiết bị hoặc quy trình không hoàn toàn độc lập giữa các giải. Nhưng nó **không** giúp chọn số, vì hiện tượng đối xứng giữa 100 số.

**H-NEW-2 (Nhánh H): "lồng hàng trăm thiếu chữ số 0".**
- H1: P(chữ số hàng trăm = 0) < 0,1.
- Kiểm định: e-process tiến cứu.
- Không ảnh hưởng tới lô hay đề.

Cả hai đều xuất phát từ dữ liệu đã xem (WP2), nên **chỉ** được kiểm trên các kỳ quay sau ngày đăng ký. **Cần LK duyệt.**

## 4. Thiết kế ASTRA AUTOMATED PATTERN DISCOVERY ENGINE (Nhiệm vụ 3), ánh xạ vào mã đã có

```
[1 Dữ liệu]         SRC-002B + SHA-256 + 98 ngày vắng (Gemini WP0)        → load_raw / FeatureStore (Codex)
[2 Sinh giả thuyết] ngữ pháp hữu hạn F1-v0 (KTST), cầu vị trí CC-07,       → |G_s| đếm chính xác bằng rule_count (B-ETH-1)
                    SR/GP (Codex, ngân sách)
[3 Chấm hồi cứu]    walk-forward, chỉ dữ liệu ≤ t                           → leakage_check (cắt + đổi tương lai) + mutation_check
[4 Mốc so sánh]     random-k chính xác theo u; 1,35 nháy/kỳ                 → xsmb_exact / p_set_hit_given_u
[5 Đa kiểm định]    Holm hoặc BY trên TOÀN ledger; ngưỡng τ_s từ ≥ 1.000    → CANDIDATE_LEDGER (≤ 500/nhánh, ≤ 1.500)
                    null giả lập
[6 Cổng]            WP2 (Yao): không phân biệt được → chỉ còn đường tiến cứu
[7 Tiến cứu]        khóa bộ số + commit GitHub trước 18:15, nhân chứng      → eprocess_mean, ngưỡng 20m
                    phiên khác
[8 Tự phản biện]    Grok red team; Claude Code tái lập độc lập mọi kết quả
```

**Nguyên tắc bắt buộc:**
- mỗi giả thuyết chỉ chạy **một lần** trên dữ liệu thật, sau khi ghi vào ledger;
- giả thuyết bị bác bỏ cũng phải lưu;
- dữ liệu 2005–2026 **đã bị xem**, nên chỉ dùng để thăm dò.

## 5. Phản biện khả năng tạo lợi thế (Nhiệm vụ 5)

- **Mọi con số "70–90%" đều có lời giải thích ngẫu nhiên** khi nêu rõ sự kiện:
  - bộ 5 có ≥ 1 số trúng trong một ngày: 74,97%;
  - một chữ số ở đầu/đít đề trong 7 ngày: 77,12%;
  - một lô bạch thủ về ít nhất một lần trong 3 ngày: 1 − 0,7623³ = 55,7%;
  - nuôi 5 ngày: 74,2%.
- **Tiền:** ở giá 22.500đ/điểm, mỗi điểm lỗ kỳ vọng **−900đ (−4%)**, với **mọi** cách chọn số và **mọi** cách nuôi khung. Lý do: kỳ vọng tuyến tính và các kỳ độc lập.
- **Kết luận hiện tại:** *chưa có bằng chứng về thông tin dự báo trong XSMB*. Điều này đúng ở mức độ phức tạp đã kiểm: 13 phép WP2, 11.342 cầu vị trí, các mô hình V1–V7 và 003–007. Đây **không** phải chứng minh rằng không tồn tại mọi quy luật. Con đường còn mở duy nhất là các giả thuyết được đăng ký trước và chấm trên tương lai.

## 6. Đề xuất bổ sung cho Master Skill

1. Mọi "cầu" trong Skill phải kèm **mốc ngẫu nhiên của chính sự kiện đó**. Ví dụ cầu vị trí: 23,8%/ngày; nuôi k ngày: 1 − 0,7623ᵏ.
2. Bảng H-STREAK (§1.1) đưa vào Skill làm **bằng chứng chuẩn** cho mục "nuôi cầu".
3. Mọi tỷ lệ phải ghi theo mẫu của Nhiệm vụ 5: sự kiện; số lượng số; khung ngày; lý thuyết hay thực nghiệm; số lần kiểm; khoảng tin cậy; mức cải thiện so với ngẫu nhiên; có phải ngoài mẫu không.

## 7. Cần LK quyết định

- **(a)** Đăng ký H-NEW-1 và H-NEW-2 để chấm tiến cứu. Đây là nghiên cứu vật lý, không dùng để chọn số.
- **(b)** Giao Codex các nhánh D và E (Transformer, hồi quy ký hiệu). Claude Code sẽ tái lập độc lập.

Trân trọng,
Claude Code
