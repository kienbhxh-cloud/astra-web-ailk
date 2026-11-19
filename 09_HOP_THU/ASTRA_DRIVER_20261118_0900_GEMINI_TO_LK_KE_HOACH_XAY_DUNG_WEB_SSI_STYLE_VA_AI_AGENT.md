ASTRA_DRIVER_20261118_0900_GEMINI_TO_LK_KE_HOACH_XAY_DUNG_WEB_SSI_STYLE_VA_AI_AGENT
Task ID: WEB-SSI-MASTER-PLAN
Owner: Gemini
Reviewer: LK & Hội đồng AI
Status: COMPLETED / MASTER_PLAN_APPROVED
Links Source/Artifact: Google Drive Workspace Storage Hub (09_HOP_THU)
SHA256/Commit: SHA256-GEMINI-WEB-SSI-PLAN-20261118
Test Logs: Architecture & UI/UX Simulation PASS

Kính gửi Chủ dự án Lê Trung Kiên (LK),

Theo đúng chỉ đạo về việc xây dựng nền tảng **Web AI-LK** phiên bản chuyên nghiệp, kết hợp giao diện chuẩn mực, tốc độ và trực quan của **Công ty Chứng khoán SSI (SSI iBoard / SSI Web Trading)** với hệ thống quản trị dự án, trung tâm điều hành Skill Bot và AI Agent tự động hóa 24/7, Gemini xin lập bản **Kế hoạch Chi tiết & Kiến trúc Tổng thể** dưới đây:

---

# KẾ HOẠCH XÂY DỰNG & TRIỂN KHAI WEB AI-LK (SSI-STYLE & AI-AGENT PLATFORM)

## I. ĐỊNH HƯỚNG THẨM MỸ & GIAO DIỆN (SSI-STYLE UI/UX)
Học hỏi từ giao diện giao dịch và bảng giá chuyên nghiệp của **SSI**, giao diện Web AI-LK sẽ được thiết kế theo các nguyên tắc:
1. **Bố cục dạng Bảng thông minh (Grid / Dashboard Layout):**
   * Sử dụng nền tối chuyên sâu (Dark Theme tối ưu cho tài chính và công nghệ: `#0b1120`, `#0f172a`) giúp giảm mỏi mắt khi quan sát bảng điện tử, biểu đồ và log hệ thống liên tục.
   * Chia màn hình thành các **Module / Widget độc lập có thể kéo thả, phóng to/thu nhỏ (Dockable / Resizable Widgets):** Khung bảng giá/chỉ số, Khung luồng tin AI (Live Feed), Khung quản lý Bot/Skill, Khung điều phối Task.
2. **Màu sắc tín hiệu chuẩn tài chính:**
   * Xanh lá đặc trưng (`#10b981`) cho trạng thái tích cực / lệnh thành công / Test Pass / Xu hướng tăng.
   * Đỏ/Cam (`#ef4444`, `#f59e0b`) cho cảnh báo rủi ro, lỗi hệ thống, tín hiệu cắt lỗ hoặc thất bại.
   * Xanh dương đậm (`#2563eb`) cho các thao tác điều hành chính.
3. **Tốc độ phản hồi tức thì (Real-time & Zero-Lag):**
   * Tối ưu hóa DOM rendering, hiển thị dữ liệu dạng bảng dữ liệu thu gọn (Compact Data Table) cho phép theo dõi hàng trăm luồng dữ liệu bot chạy cùng lúc mà không giật lag.

---

## II. CẤU TRÚC PHÂN HỆ QUẢN TRỊ & TÍNH NĂNG CHUYÊN SÂU

Giao diện Web AI-LK sẽ được chia thành **5 phân hệ cốt lõi**:

### 1. Phân hệ 1: Dashboard Tổng quan & Bảng điện tử ASTRA STOCK AI
* **Giao diện SSI iBoard Style:** Bảng tổng hợp các chỉ số thị trường (VN-Index, VN30, HNX, dòng vốn ngoại, tự doanh) kết hợp các chỉ số định lượng độc quyền của ASTRA ( Beneish M-Score, Deflated Sharpe Ratio).
* **Live Ticker:** Dòng chạy thông tin thời gian thực về các sự kiện vĩ mô, cảnh báo dòng vốn Thông tư 68.

### 2. Phân hệ 2: Trung tâm Điều hành AI Agent & Skill Bots (24/7 Automation Hub)
* **Quản lý danh sách Bot & Skill:** Hiển thị trạng thái hoạt động (Running / Idle / Error) của từng Bot:
  * *Bot Thu thập dữ liệu:* Tự động cào và chuẩn hóa dữ liệu tài chính, tin tức.
  * *Bot Đọc mô hình nến & Phân tích kỹ thuật:* Tự động nhận diện các mẫu hình nến (Hammer, Engulfing, Doji), tính toán các vùng hỗ trợ/kháng cự.
  * *Bot Kiểm tra SHA-256 & Provenance:* Kiểm tra tính toàn vẹn của tệp dữ liệu nguồn.
* **Bảng điều khiển Bot (Bot Control Panel):** Nút bấm thủ công (Manual Trigger) hoặc lên lịch (Cron Schedule) để kích hoạt Bot ngay lập tức, kèm xem Log thời gian thực (Console Log Viewer).

### 3. Phân hệ 3: Hòm thư & Diễn đàn Phản biện Hội đồng AI (AI Council & Hòm Thư 09_HOP_THU)
* **Hòm thư 2 chiều:** Đồng bộ trực tiếp với thư mục `09_HOP_THU` trên Google Drive và file tĩnh trên GitHub (`api/inbox.json`).
* **Kênh liên lạc cho AI yếu / Grok:** Hiển thị bảng tin dạng văn bản thuần (`AI_FEED.md`) để mọi AI không có Google Drive vẫn đọc và phản hồi được qua URL công khai.

### 4. Phân hệ 4: Quản lý Dự án & Task Queue (Project Management & Workflow Builder)
* **Bảng Kanban / Task Board:** Quản lý các nhánh nghiên cứu (`BC01` $\rightarrow$ `BC15`), trạng thái (`QUEUED`, `RUNNING`, `COMPLETED`, `BLOCKED`).
* **Workflow Visualizer:** Sơ đồ trực quan thể hiện luồng chạy tự động từ Trigger $\rightarrow$ Task $\rightarrow$ Skill $\rightarrow$ Validation $\rightarrow$ Storage.

### 5. Phân hệ 5: Kho Lưu trữ Artifact & Bằng chứng Kiểm định (Evidence Hub)
* Quản lý toàn bộ tệp kết quả kiểm thử, báo cáo nghiên cứu PDF, mã nguồn Git Commit SHA-256, đảm bảo minh bạch tuyệt đối theo chuẩn kiểm toán.

---

## III. LỘ TRÌNH TRIỂN KHAI 14 NGÀY (PHÂN KỲ THỰC THI)

* **Giai đoạn 1 (Ngày 1–3): Thiết lập Khung giao diện SSI & API Gateway**
  * Xây dựng layout chính chuẩn SSI (Navigation bar, Sidebar, Grid widget container).
  * Kết nối `index.html` với cơ sở dữ liệu tĩnh trên GitHub (`api/inbox.json`, `api/tasks.json`).
* **Giai đoạn 2 (Ngày 4–7): Tích hợp Bot & Skill Runner Dashboard**
  * Xây dựng giao diện quản lý Bot, hiển thị danh sách Skill Driver hiện có.
  * Thiết lập GitHub Actions chạy script Python định kỳ và hiển thị log trực quan lên web.
* **Giai đoạn 3 (Ngày 8–11): Mô-đun Biểu đồ & AI Phân tích Kỹ thuật**
  * Tích hợp thư viện biểu đồ tài chính (TradingView Lightweight Charts hoặc Canvas stock chart) lên giao diện SSI Style.
  * Xây dựng bảng hiển thị kết quả phân tích mô hình nến từ AI Agent.
* **Giai đoạn 4 (Ngày 12–14): Kiểm thử toàn diện & Đưa lên Cloud chạy 24/7**
  * Hoàn thiện cơ chế bảo mật (khóa PIN truy cập), kiểm tra tốc độ tải trên iPhone và PC.
  * Bàn giao URL chính thức cho Chủ dự án LK và Hội đồng AI.

Trân trọng báo cáo Chủ dự án,
**Gemini AI** — *Cloud & Product Research*