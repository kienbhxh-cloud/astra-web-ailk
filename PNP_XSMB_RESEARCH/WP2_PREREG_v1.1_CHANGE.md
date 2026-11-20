# WP2_PREREG v1.1 — thay đổi so với v1.0 (DUY NHẤT: dữ liệu đầu vào)

- Ngày 20/11/2026 · Claude Code · Căn cứ: ChatGPT ACTION-008 (G0), Claude KTST DATA-FIX-001, Gemini PRODUCT-002 v2.1, chỉ đạo LK "làm tiếp".
- **Thay đổi:** dữ liệu `07e110ac…5b78` (SRC-002, v1, LEGACY_KNOWN_ERROR) → `85aabd573c67bf4c0dbba4151a05f6771113c8c542dd6dd4dcdfaf4d27535909` (SRC-002B, v2).
- **Không đổi:** mã `wp2_distinguishers.py` (SHA-256 `9983468a…a9c3`), 13 phép, thứ tự, đuôi kiểm định, B = 9.999 / 999, seed 20261120, Holm α = 0,05, quy tắc diễn giải.
- **Kiểm chứng độc lập v2 của Claude Code [X]:** hash khớp; `diff` v1→v2 đúng **1 dòng** (2006-09-21); v1 có 2006-09-21 ≡ 2006-09-25 cả 27 giải; lỗi có từ nguồn gốc khiemdoan (bản Claude Code tải 19/11 cũng trùng).
- **Còn mở [C]:** 26 giải ngoài ĐB của 2006-09-21 mới có 1 nguồn đầy đủ. Claude Code thử minhngoc.net.vn, xskt.com.vn, xoso.com.vn: **bị chặn mạng** trong môi trường này.
- **Minh bạch:** WP2 đã chạy một lần trên v1 (00:16–00:24 UTC 20/11, trước thư ACTION-008 lúc 00:25 UTC) theo chỉ đạo LK. Kết quả v1 được GIỮ NGUYÊN, gắn nhãn chạy trên dữ liệu có lỗi đã biết. Lần chạy v1.1 là chạy lại do **sửa dữ liệu**, không đổi thống kê; cả hai được báo cáo.
