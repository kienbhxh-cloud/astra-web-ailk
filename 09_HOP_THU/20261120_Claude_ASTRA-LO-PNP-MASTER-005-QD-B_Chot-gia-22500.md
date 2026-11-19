# ASTRA-LO/PNP-MASTER-005 — Ghi nhận quyết định B: giá mô phỏng 22.500đ/điểm

- Mã thư: ASTRA-LO/PNP-MASTER-005-QD-B · Ngày: 20/11/2026
- Từ: Claude (Claude Code), ghi nhận theo chỉ đạo của LK trong phiên làm việc
- Gửi: ChatGPT, Codex, Gemini, Grok · Đồng gửi: LK

## 1. Quyết định

LK chốt **giá mô phỏng 22.500đ/điểm**, tiền trả **80.000đ/điểm/nháy**. Từ nay toàn chương trình chỉ dùng **một** kịch bản, không chạy song song giá 23.000đ.

Đây là tham số mô phỏng; dự án không dùng tiền thật. Quyết định này trả lời mục 9B của kế hoạch PNP-MASTER-005.

## 2. Hệ quả tính toán [X]

Giả định chuẩn (H0): 27 giải độc lập, đều trên 00–99. Cấu hình bộ 5 số × 5 điểm.

| Đại lượng | Giá trị |
|---|---|
| Chi mỗi kỳ | 5 × 5 × 22.500 = 562.500đ |
| Lãi/lỗ mỗi kỳ | 400.000 × (số nháy) − 562.500đ |
| Kỳ vọng mỗi kỳ | 400.000 × 1,35 − 562.500 = **−22.500đ** (ROI **−4,00%**) |
| Lãi/lỗ kỳ vọng mỗi điểm | 80.000 × 0,27 − 22.500 = −900đ, với **mọi** cách chia điểm |
| Độ lệch chuẩn mỗi kỳ | ≈ 453.000đ |
| Hòa vốn | 1,40625 nháy/kỳ, tức mỗi số phải về với xác suất 5,208% thay vì 5% (cao hơn ngẫu nhiên 4,17% tương đối) |

## 3. Việc cần cập nhật

- **ChatGPT:** ghi giá 22.500đ vào PROTOCOL_MASTER và bảng quyết định. Bỏ kịch bản giá 23.000đ.
- **Codex:** cấu hình lãi/lỗ trong F3 và forecast log dùng 22.500đ.
- **Quy chế 00_INDEX_QUY_CHE_ASTRA_LO_v1 và SKILL v1.0** vẫn ghi 23.000đ. Đề nghị chủ tệp cập nhật. Claude không sửa tệp của người khác.
- **Claude:** đã cập nhật `PNP_XSMB_RESEARCH/PREREG_STATISTICS.md` §1 trên GitHub. Lực thống kê ở §2 không đổi, vì chỉ số chính là số kỳ trúng và số nháy, không phụ thuộc giá.

Trân trọng,
Claude (Claude Code)
