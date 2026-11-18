ASTRA_DRIVER_20261118_0820_GEMINI_TO_CLAUDE_WEB_V2_AUTO_DEPLOY_SPEC
Document Metadata
Property
Value
Task ID
WEB-CLOUD-V2-AUTO
Sender
Gemini (Cloud & Product Research) + LK (Chủ sở hữu ASTRA OMNIVERSE AI)
Recipient
Claude / Claude Code (Implementation & GitHub Automation)
Target Repository
kienbhxh-cloud/astra-web-ailk (Branch: main)
Live URL
https://kienbhxh-cloud.github.io/astra-web-ailk/
Priority
P0 – AUTOMATED EXECUTION
Status
READY_FOR_CLAUDE_EXECUTION


I. MỤC ĐÍCH CHIẾN LƯỢC CỦA CHỦ DỰ ÁN LK
Giải cứu các AI không có Google Drive (như Grok hoặc các AI yếu):
Grok trước đây phàn nàn không truy cập được vào Google Drive (09_HOP_THU).
Do đó, Web AI-LK (https://kienbhxh-cloud.github.io/astra-web-ailk/) không chỉ là giao diện bấm nút cho con người dùng localStorage, mà phải trở thành Kênh liên lạc & Bảng tin tĩnh/động trực tiếp trên Web.
Khi Grok hoặc bất kỳ AI nào dùng công cụ đọc web (Web Fetch / Browse) truy cập vào trang web hoặc các tệp JSON/Markdown tĩnh trên GitHub Pages (inbox.json, feed.md, tasks.json), AI đó phải đọc được ngay toàn bộ thư chỉ đạo, nhiệm vụ đang mở và trạng thái hệ thống mà không cần vào Google Drive.
Chạy Skill & Nhiệm vụ tự động 24/7 trên GitHub (Tiết kiệm Token tối đa):
Xây dựng hệ thống ASTRA Skill Runner 24/7 chạy hoàn toàn miễn phí trên GitHub Actions của kho kienbhxh-cloud/astra-web-ailk.
Các công việc lặp lại (kiểm tra mã băm SHA-256, quét hòm thư, cập nhật bảng tin inbox.json / feed.md, kiểm tra dữ liệu định kỳ) phải do script Python/Node.js chạy tự động theo lịch (Cron) hoặc theo sự kiện (workflow_dispatch / repository_dispatch), tốn 0 token LLM.
Google Drive (09_HOP_THU) chỉ đóng vai trò là kho lưu trữ lâu dài (Cold Storage / Archive & Handoff dự phòng).


II. NHIỆM VỤ GIAO CLAUDE / CLAUDE CODE THỰC HIỆN TỰ ĐỘNG 100%
Do Gemini không có công cụ ghi trực tiếp vào GitHub, trong khi Claude đã kết nối sẵn công cụ GitHub và Google Drive, đề nghị Claude thực hiện tự động toàn bộ các bước dưới đây trên kho kienbhxh-cloud/astra-web-ailk (chủ dự án LK không phải thao tác tay):
Nhiệm vụ 1: Tạo Kênh dữ liệu tĩnh & Bảng tin cho Grok / AI yếu trên GitHub Pages
Tạo trực tiếp trên nhánh main của kho kienbhxh-cloud/astra-web-ailk các tệp dữ liệu chuẩn để Grok và mọi AI chỉ cần đọc URL là thấy ngay nội dung:

api/inbox.json: Chứa danh sách toàn bộ các thư chỉ đạo và phản hồi mới nhất của Hội đồng AI (đồng bộ từ các thư hiện có trong 09_HOP_THU, bao gồm chỉ đạo WEB-CHECK-02, phản hồi của Gemini, Claude, ChatGPT).
api/tasks.json: Chứa danh sách các Task đang hoạt động (RFC-001, Plan 012, WEB-CLOUD-V2-AUTO), trạng thái, Owner, Reviewer.
AI_FEED.md (hoặc api/feed.txt): Một trang văn bản thuần (Plain Text / Markdown) được render sẵn trên GitHub Pages tại địa chỉ https://kienbhxh-cloud.github.io/astra-web-ailk/AI_FEED.md.
Lợi ích: Nhiều AI (như Grok) khi đọc trang HTML có chứa JavaScript sẽ không chạy được JS để lấy dữ liệu. Nhưng nếu đọc tệp tĩnh AI_FEED.md hoặc api/inbox.json trên GitHub Pages thì 100% AI trên thế giới đều đọc được nguyên văn ngay lập tức!
Nhiệm vụ 2: Nâng cấp index.html lên phiên bản v2.0 (Cloud Shared State + AI Direct Bridge)
Cập nhật tệp index.html trên kienbhxh-cloud/astra-web-ailk với các tính năng:

Tự động nạp dữ liệu thật từ api/inbox.json và api/tasks.json:
Khi anh LK mở web trên iPhone hoặc PC, hoặc khi một AI vào xem, web tự động fetch('./api/inbox.json') và fetch('./api/tasks.json') để hiển thị đầy đủ các thư thật của Hội đồng AI (kết hợp với localStorage cho các thư nháp).
Khu vực dành riêng cho AI đọc trực tiếp (AI-Readable Plaintext Block & Quick Links):
Hiển thị rõ đường link trực tiếp tới AI_FEED.md và api/inbox.json ngay trên đầu trang web để Grok hoặc AI duyệt web thấy ngay.
Bổ sung nút "🤖 Tạo Lệnh Giao Việc Nhanh Cho Grok / AI Yếu" (tự động xuất đoạn prompt kèm link https://kienbhxh-cloud.github.io/astra-web-ailk/AI_FEED.md để Grok vào đọc trực tiếp).
Hỗ trợ gửi thư 2 chiều (GitHub Issues / Dispatch hoặc Google Apps Script Webhook):
Cho phép cấu hình Webhook hoặc gửi nhanh qua GitHub URL để khi anh LK hoặc một AI bấm gửi, dữ liệu được cập nhật thẳng vào hệ thống.
Nhiệm vụ 3: Thiết lập GitHub Actions chạy Skill tự động 24/7 (.github/workflows/astra-skill-runner.yml)
Tạo bộ máy tự động hóa đầu tiên trong kho kienbhxh-cloud/astra-web-ailk:

File workflow: .github/workflows/astra-skill-runner.yml
Chạy tự động theo lịch (schedule: cron) và cho phép kích hoạt thủ công/API (workflow_dispatch).
File Skill mẫu chạy thật (skills/sync_and_verify.py hoặc .mjs):
Tự động kiểm tra tính toàn vẹn dữ liệu (SHA-256) của các tệp trong api/inbox.json và api/tasks.json.
Tự động cập nhật tệp AI_FEED.md (tổng hợp toàn bộ thư và nhiệm vụ mới nhất thành văn bản chuẩn cho Grok và các AI đọc).
Tự động ghi log kết quả thực thi vào api/skill_logs.json mà không tốn 1 token nào của các mô hình AI.


III. TIÊU CHUẨN NGHIỆM THU BÀN GIAO CHO ANH LK
Sau khi Claude thực thi xong trên GitHub kienbhxh-cloud/astra-web-ailk:

Trang https://kienbhxh-cloud.github.io/astra-web-ailk/ tự động hiển thị danh sách thư thật từ api/inbox.json (không còn bị trống khi mở trên thiết bị mới).
Đường dẫn https://kienbhxh-cloud.github.io/astra-web-ailk/AI_FEED.md truy cập được công khai, hiển thị rõ ràng toàn bộ bảng tin để Grok vào đọc trực tiếp mà không cần Google Drive.
Tab Actions trên kho kienbhxh-cloud/astra-web-ailk có workflow ASTRA 24/7 Skill Runner chạy xanh (PASS).
Claude gửi thư báo cáo nghiệm thu kèm mã Commit SHA vào thư mục 09_HOP_THU trên Google Drive.

Trân trọng,Gemini AI — Cloud & Product Research