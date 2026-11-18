# WEB-CLOUD-V2 — FACT / UNVERIFIED
Người báo cáo: Kỹ sư Codex-Sam Altman — SIMULATED_ROLEPLAY / AI.
Ngày 18/11/2026, 17:41 ICT. Trạng thái: CHỜ LK NHẬP KHÓA, chưa hoàn tất kiểm thử khép kín.
Kho kienbhxh-cloud/astra-web-ailk, source main 5b2beb160e5339ab31b9270e7ca4253f42c68fc4 (sau bfebb92775b2de67408af9591ace2e0918e0e1b5).

## Kết quả
| Mục | Nhãn | Bằng chứng / giới hạn |
|---|---|---|
| Đọc bridge/Code.gs an toàn | FACT | Đọc file tại exact source SHA; không dùng Code.gs gốc trong thư Gemini1532. |
| Syntax skill_agent.mjs | FACT | node --check trên bản lấy từ exact source SHA, exit0. |
| Bridge từ chối thiếu/sai secret | FACT, local stub ONLY | Node vm với Apps Script services giả: thiếu cấu hình, secret sai, payload thiếu secret đều ok:false/unauthorized; không truy cập Drive. Không phải webhook deploy thật. |
| URL /docs/ truy cập HTTP | FACT | GET https://kienbhxh-cloud.github.io/astra-web-ailk/docs/ trả200 từ cloud. Không phải xác nhận render. |
| a. Hiển thị trên PC | UNVERIFIED | Playwright thử nhưng thiếu Chromium executable, launch thất bại. HTTP200 không thay browser check. |
| a. Hiển thị trên iPhone thật | UNVERIFIED | Không có thiết bị thật trong phiên. |
| b. Thư LK + SKILL -> Skill Agent Runner -> REPLY | UNVERIFIED | Chưa đăng thư kích hoạt vì theo Bước1 phải chờ LK tự tạo/nhập khóa. Chưa xác minh Actions Secrets hoặc Gemini call. Không tạo reply giả. |
| c. REPLY xuất hiện trên Drive qua webhook | UNVERIFIED | Chưa có URL deployment và chưa kiểm cấu hình bridge; không suy từ report upload thủ công. |
| d. Drive MSG_test.md -> GitHub sau5phút | UNVERIFIED | Chưa xác minh setupBridge/folder/trigger5phút; chưa tạo test để bridge chưa cấu hình xử lý. |
| e. Sai secret bị từ chối trên webhook thật | UNVERIFIED | Local stub PASS không chứng minh deployment. Cần URL /exec của bản deploy hiện hành; chưa có. |
| GitHub Secrets / Script Properties đã đủ | UNVERIFIED | Công cụ hiện không có API nhập GitHub Secrets hay Script Properties. Không đọc/xuất giá trị khóa. |
| Pages main/root giữ nguyên | FACT về thao tác phiên | Không đổi Pages settings. Cấu hình hiện tại chưa đọc qua admin endpoint. |

## Actions đã quan sát, không phải test b
Pages build tại source SHA success:
https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44286912939
ASTRA 24/7 Skill Runner success tại bfebb927:
https://github.com/kienbhxh-cloud/astra-web-ailk/actions/runs/44286892957
Đây KHÔNG phải workflow ASTRA Skill Agent Runner được yêu cầu.
Đã đọc14 runs trả về, chưa thấy run tên ASTRA Skill Agent Runner.
09_HOP_THU tại source chỉ cóREADME.md; chưa có test/reply trong lần đọc.

## Quan sát kỹ thuật trước kiểm thử
1. doPost trả JSON ok:false,error:unauthorized khi secret thiếu/sai; HTTP200 có thể vẫn là từ chối.
   e phải assert JSON, rồi xác minh không có file được tạo.
2. skill_agent.mjs chỉ log webhook HTTPstatus, không kiểm JSON ok. Do đó run xanh/webhook200
   không chứng minh SYNCED_TO_DRIVE; c phải mở đúng file Drive và đối chiếu content.
3. setupBridge chọn thư mục09_HOP_THU đầu tiên theo tên. LK cần kiểm DRIVE_FOLDER_ID sau setup đúng
   thư mục dự định, đặc biệt nếu Drive có nhiều thư mục cùng tên.
4. syncDriveToGitHub chỉ lấy tên MSG_/ASTRA_DRIVER_, file gần24giờ và giới hạn kích thước.
   Thư mục chọn sẽ có các tệp phù hợp được đưa lên repo CÔNG KHAI. Chỉ dùng dữ liệu tổng hợp cho test.
5. Không sửa runtime/workflow/Pages; chưa gọi Gemini hoặc bật trigger/deploy từ phiên.

## Việc LK nhập trực tiếp (không dán khóa vào chat)
1. Tạo GEMINI_API_KEY tại aistudio.google.com.
2. Tạo BRIDGE_SECRET ngẫu nhiên >=16ký tự, cùng một giá trị tại hai nơi.
3. Tạo fine-grained PAT chỉ repo astra-web-ailk, Contents Read/write, hạn30–90ngày.
4. GitHub Settings > Secrets and variables > Actions: GEMINI_API_KEY và BRIDGE_SECRET.
5. Apps Script dùng đúng bridge/Code.gs tại source SHA trên; Script Properties:
   GITHUB_TOKEN=PAT, BRIDGE_SECRET. Chạy setupBridge một lần, kiểm đúng DRIVE_FOLDER_ID.
6. Deploy Web App ai cũng truy cập, secret bảo vệ; thêm trigger syncDriveToGitHub mỗi5phút.
7. Đặt URL /exec vào GitHub Secret DRIVE_WEBHOOK_URL.
Chỉ báo “đã cấu hình xong” và cung cấp URL deployment nếu cần; không gửi khóa/token/secret.
Sau đó mới kích hoạt MSG_<ngày>_LK_ALL_TEST.md [SKILL:TONG_HOP_BAO_CAO], theo dõi đúngrun,
đối chiếu REPLY hai phía, chạy Drive->GitHub và thử secret sai.
Lý do dừng phần nhập khóa: lệnh LK yêu cầu LK tự tạo và nếu Codex không có công cụ nhập an toàn thì để LK nhập.


## Cập nhật sau khi LK cấp kho cho ChatGPT Codex Connector
LK đã lưu quyền chọn hai kho. Việc tạo tệp báo cáo này là phép kiểm quyền ghi thật; chỉ xác nhận thành công khi có commit và readback. Các mục cấu hình Secrets/Apps Script và kiểm thử khép kín vẫn UNVERIFIED. Không chứa khóa.
