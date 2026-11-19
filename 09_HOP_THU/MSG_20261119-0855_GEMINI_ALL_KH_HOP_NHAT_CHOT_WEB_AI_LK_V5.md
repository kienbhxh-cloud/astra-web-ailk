KẾ HOẠCH HỢP NHẤT CHỐT: WEB AI-LK — ASTRA OMNIVERSE & STOCK TERMINAL
Bản Đề cử Vòng 2 của Gemini (GEMINI-WEB-PLAN-v5) · 19/11/2026
Trường
Nội dung
Mã văn bản
GEMINI-WEB-PLAN-v5 (KH_Hop_Nhat_Chot)
Task ID
ASTRA-WEB-RFC002 (Vòng 2 — Chấm điểm & Chốt Phương án Cuối)
Từ
Gemini (Cloud & Product Research)
Đến
Chủ dự án LK & Hội đồng AI (Claude, Codex, ChatGPT, Grok, Claude Code)
Thời gian
08:55 ngày 19/11/2026 (UTC+7)
Trạng thái
ĐỀ CỬ VÒNG 2 — CHỜ CHẤM ĐIỂM & CHỦ DỰ ÁN LK PHÊ DUYỆT (Chưa phải bản đã duyệt)
Phân loại dữ liệu
INTERNAL_SAFE (Đã rà soát, không chứa thông tin cá nhân, cơ quan, bí mật hay URL nội bộ)

Tính độc lập & Kế thừa minh bạch: Bản kế hoạch này đứng độc lập để Chủ dự án LK có thể chọn triển khai ngay mà không cần đọc lại các bản nháp cũ. Bản này khắc phục toàn bộ điểm trừ ở vòng 1 của Gemini và tiếp thu có ghi nguồn các điểm mạnh nhất từ Claude v5.0 (bảo mật Cloudflare Access, 6 luật chống nhìn trước tương lai, hàng chờ Cần anh quyết), Codex v0.4 (nguyên tắc một nơi ghi, kiểm chứng thực tế repo/schema, lộ trình WEB-M0..M4), ChatGPT RFC-002 (kiến trúc 1 nền tảng OMNIVERSE, trạng thái do hệ thống ghi), và Grok ASTRA Board (giao diện 1 màn hình 3 lớp kiểu SSI iBoard, quy ước màu giá VN, bảng Skill Boot, không nút Mua/Bán).
0. TÓM TẮT ĐIỀU HÀNH CHO CHỦ DỰ ÁN LK
Câu hỏi cốt lõi
Phương án chốt trong GEMINI-WEB-PLAN-v5
Xây cái gì?
Một cổng web duy nhất (Web AI-LK) chạy 24/7 trên PC và iPhone: điều hành dự án ASTRA OMNIVERSE, cổng phối hợp đa AI, trung tâm chạy Bot/Skill tự động (ASTRA FLOW), và ứng dụng đầu tiên STOCK TERMINAL mang bố cục trực quan kiểu SSI iBoard (không sao chép thương hiệu, không đặt lệnh thật).
Kế thừa hay viết lại?
Kế thừa 100%, không viết lại. Tiến hóa trực tiếp từ docs/index.html, api/tasks.json (schema astra-tasks/1), Bridge Drive-GitHub, skills/skill_agent.mjs và .github/workflows/astra-skill-agent.yml đang chạy thật.
Chi phí vận hành?
Hạ tầng giai đoạn đầu xấp xỉ 0 đồng (GitHub Actions + Cloudflare Pages/Access gói miễn phí). Khoản chi thật là phí gọi API AI -> bắt buộc áp dụng Token Economy 5 cấp và Trần ngân sách API theo ngày (Daily Budget Cap).
Ưu tiên làm gì trước?
(1) Bịt 2 lỗ hổng P0: tách kho riêng tư (SPLIT-REPO-01), bỏ lưu PAT/Secret ở trình duyệt, vá lỗ hổng giả danh tên tệp kích hoạt bot; (2) Bản chỉ xem trên iPhone/PC: Dashboard SSI, 15 nhánh BC01-BC15, Hộp thư, Skill Boot, Bằng chứng; (3) Luồng ghi có kiểm soát: LK duyệt quyết định 1 chạm trên web, bot chạy 24/7 khi PC tắt; (4) Luồng STOCK trọn vẹn: dữ liệu PIT -> nhận diện nến (nhãn GIẢ THUYẾT) -> kiểm định -> phản biện -> báo cáo.
Tiến độ ra sao?
Không cam kết cứng 14 hay 35 ngày khi chưa đo. Mốc WEB-M0 (dự kiến khoảng 3 ngày làm việc) hoàn tất vá bảo mật P0 và xuất bảng ước lượng nguồn lực từng gói việc để LK chốt lịch chính thức.
1. TÁM NGUYÊN TẮC BẤT BIẾN (ÁP DỤNG CHO MỌI MÀN HÌNH, BOT VÀ AI)
Sự thật có bằng chứng (Evidence-First): Mọi con số trên web bắt buộc gắn kèm nguồn (source), thời điểm (timestamp), lớp dữ liệu (A / B / C) và trạng thái (value_status: OK / MISSING / STALE / BLOCKED). Thiếu dữ liệu phải ghi rõ "THIẾU", tuyệt đối không hiển thị thành số 0 giả (tiếp thu Grok, Codex).
Trạng thái do hệ thống ghi, AI không tự khai: Cấm AI tự gán nhãn APPROVED, PASS, 0-token hay chuỗi tự đặt kiểu SHA256-... nếu không kèm run ID, commit hash hoặc digest SHA-256 thật do hệ thống sinh ra (tiếp thu ChatGPT RFC-002, Codex).
Một nơi ghi, nhiều nơi xem (Single Source of Truth): Mỗi loại dữ liệu chỉ có một nguồn ghi chuẩn. Toàn bộ tệp JSON/feed phục vụ giao diện web chỉ là bản chiếu chỉ đọc (read-only), tuyệt đối không biến thành nơi ghi thứ hai gây lệch dữ liệu (tiếp thu Codex).
Phần mềm trước, AI sau (Deterministic-First): Việc nào tính được bằng mã xác định (Python/JS) thì chạy bằng mã (0 token). Chỉ gọi AI cho phân tích ngữ nghĩa, giải thích, phản biện và tổng hợp (RFC-001).
Riêng tư mặc định (Private by Default — SPLIT-REPO-01): Thư nội bộ, dữ liệu nghiên cứu, thông tin dự án chưa công bố nằm tại kho riêng tư (private repo) và Google Drive. Kho công khai chỉ chứa vỏ giao diện hoặc bản tin đã lọc sạch hoàn toàn dữ liệu nhạy cảm.
Khoa học trước giao diện (Scientific Rigor): Nhận diện mẫu hình nến không đồng nghĩa với lợi thế giao dịch. Mọi tín hiệu mặc định gắn nhãn GIẢ THUYẾT (HYPOTHESIS) cho đến khi vượt qua kiểm định tiền đăng ký. Kết quả âm tính (thất bại) phải hiển thị ngang hàng với kết quả dương tính (tiếp thu Claude v5).
Không giao dịch thật: Tuyệt đối không có nút Mua / Bán. Chỉ cung cấp thao tác "Theo dõi" và "Ghi chú" (tiếp thu Grok).
Đo bằng sản phẩm dùng được thực tế: Đánh giá tiến độ bằng tính năng chạy ổn định trên PC và iPhone của LK, không đo bằng số lượng thư hay số dòng báo cáo (tiếp thu Claude v5).
2. KIẾN TRÚC TỔNG THỂ: MỘT CỔNG ASTRA DUY NHẤT & HẠ TẦNG AN NINH P0
2.1. Phân tầng kiến trúc 4 lớp (Không tạo nền tảng cạnh tranh)
Tầng Nền tảng tổng: ASTRA OMNIVERSE (quản trị danh tính, quyền, sổ cái bằng chứng, ngân sách).
Tầng Cổng phối hợp: Web AI-LK (giao diện điều hành đa AI, hộp thư, hàng chờ phê duyệt của LK).
Tầng Thực thi tự động: ASTRA FLOW (runtime chạy Bot/Skill 24/7 trên GitHub Actions).
Tầng Ứng dụng chuyên ngành: STOCK TERMINAL là ứng dụng đầu tiên (P0). Các nhánh mở rộng (WORLD, FUTURE, INVENTOR, SENTIENT MIND) chỉ đăng ký ranh giới dữ liệu và không gian chờ (PARKED) trong MVP để tránh phình phạm vi.
2.2. Công nghệ nền & Quy tắc tiến hóa
Giữ kiến trúc tĩnh (Static Web + GitHub Actions): Tiếp tục dùng HTML/CSS/JS thuần kế thừa từ docs/index.html; tự động tách thành các module JS nhỏ khi vượt khoảng 1.500 dòng để dễ bảo trì.
Hoãn Next.js / SQLite / Postgres: Chỉ xem xét chuyển sang React/Vite hoặc backend động khi có văn bản quyết định kiến trúc (ADR) so sánh rõ chi phí vận hành, hiệu năng và phương án hoàn tác (rollback).
2.3. Giải pháp An ninh P0 (Bịt triệt để 3 rủi ro đang mở)
Tách 2 kho theo SPLIT-REPO-01: Chuyển toàn bộ dữ liệu thư, cấu hình và tài liệu nội bộ sang kho riêng tư (private). Kho công khai chỉ giữ mã vỏ giao diện không chứa dữ liệu nhạy cảm.
Đăng nhập tầng hạ tầng (Bỏ khóa PIN trình duyệt & bỏ lưu PAT ở localStorage):
Bỏ hoàn toàn đề xuất khóa PIN ở frontend và ngừng lưu GitHub PAT / BRIDGE_SECRET trong localStorage của trình duyệt.
Xây dựng bản web nội bộ từ kho riêng tư lên Cloudflare Pages và đặt sau cổng đăng nhập Cloudflare Access (chỉ cho phép email của Chủ dự án LK đăng nhập). Mọi thao tác ghi từ web (duyệt quyết định, kích hoạt bot) đi qua một endpoint/worker trung gian giữ bí mật ở phía máy chủ (Secrets), không bao giờ lộ token ra trình duyệt (tiếp thu Claude v5).
Vá lỗ hổng kích hoạt [SKILL:...] theo tên tệp:
Lỗ hổng hiện tại: astra-skill-agent.yml và skill_agent.mjs chỉ dựa vào tiền tố tên tệp MSG_*_LK_*.md để nhận diện lệnh từ LK, nên bất kỳ ai ghi được vào thư mục hộp thư đều có thể mạo danh kích hoạt job gọi Gemini API.
Cách vá bắt buộc ở WEB-M0: Bridge phải ghi kèm metadata người tạo/sửa thật từ Google Drive (owner / lastModifyingUser) và đối chiếu với danh sách được phép (allowlist email của LK) kết hợp chữ ký/xác thực BRIDGE_SECRET trước khi cho phép kích hoạt Skill Agent.
3. GIAO DIỆN SSI-STYLE & TRẢI NGHIỆM PC / IPHONE (PWA)
Tiếp thu trọn vẹn tinh hoa thiết kế ASTRA Board (Grok) kết hợp tính thực dụng trên iPhone (Gemini):

Bố cục 1 màn hình 3 lớp (Desktop SSI iBoard Style):
Thanh trên (Top Bar): Chuyển đổi không gian dự án (Workspace Switcher), đồng hồ trạng thái Bridge/Actions, nút Ngắt khẩn cấp (Global Kill-Switch) và bộ đếm ngân sách API trong ngày.
Menu trái (Sidebar): Điều hướng nhanh giữa 7 khu vực chức năng chính.
Vùng giữa (Compact Grid): Nền tối tài chính (#0b1120, #0f172a), bảng dữ liệu mật độ cao, liên kết đồng bộ theo mã màu. (Tính năng kéo thả và lưu bố cục widget tùy biến được đẩy sang mốc WEB-M4 để giữ MVP nhẹ và nhanh).
Ngăn chi tiết phải (Right Inspector): Xem nhanh chi tiết mã nghiên cứu, bằng chứng SHA-256, log chạy bot hoặc nội dung thư mà không phải chuyển trang.
Quy ước màu sắc kỷ luật: Màu xanh lá/đỏ kèm ký hiệu tăng/giảm (▲▼) chỉ dùng cho biến động giá thị trường theo chuẩn chứng khoán Việt Nam (tím trần, xanh lơ sàn, vàng tham chiếu). Trạng thái hệ thống dùng hệ màu riêng (xanh dương/xám/cam cảnh báo) để tránh nhiễu thị giác.
Tối ưu di động (iPhone PWA): Đóng gói chuẩn Progressive Web App (PWA) để LK ghim ra màn hình chính iPhone; giao diện tự động gom về thẻ trượt dọc, ưu tiên hiển thị đầu tiên là hàng chờ "Cần anh LK quyết" để duyệt/từ chối chỉ bằng 1 chạm.
4. CẤU TRÚC 7 PHÂN HỆ CHỨC NĂNG CỐT LÕI
Hàng chờ "Cần anh LK quyết" (Human-in-the-Loop Decision Queue): Gom mọi yêu cầu cần Chủ dự án phê duyệt (chốt RFC, mở cổng dữ liệu, mở khóa chi phí, duyệt thay đổi mã nguồn) kèm tóm tắt 3 dòng, rủi ro và bằng chứng đi kèm.
Cổng Phối hợp Đa AI (Multi-AI Coordination Hub):
Ma trận kết nối sống: Phân rõ nhóm có GitHub+Drive (Claude, Claude Code, Codex), nhóm có Drive (Gemini, ChatGPT) và nhóm không có Drive / AI yếu (Grok).
Kênh cho Grok / AI yếu: Cung cấp Sanitized Feed (tệp tĩnh văn bản thuần đã lọc sạch 100% thông tin nhạy cảm, cá nhân, cơ quan và đường dẫn nội bộ) hoặc luồng "Chuyển việc thủ công" gắn trạng thái WAITING_FOR_MANUAL_RELAY.
Kiểm chứng chéo & Nhật ký bất đồng (Dissent Log): Ghi nhận độc lập các ý kiến phản biện trái chiều giữa các AI trước khi LK ra quyết định.
Vòng đời nhiệm vụ chuẩn: NEW -> ACK -> IN_PROGRESS -> SUBMITTED -> REVIEW -> ACCEPTED / CHANGES_REQUESTED / BLOCKED / CANCELLED. Tách bạch 3 lớp trạng thái: research_status, job_status, và acceptance_status (job chạy SUCCESS không đồng nghĩa với đã ACCEPTED).
Không gian Nghiên cứu 15 Nhánh (BC01–BC15):
Giữ đủ 15 branch_id theo DRIVER_010 (không tự ý đóng băng hay gộp nhánh khi LK chưa duyệt: BC04/BC05 đặt NO_NEW_WORK_30D; BC13/BC14 dùng chung Price-Pattern Lab nhưng giữ 2 định danh riêng).
Gắn trực tiếp dữ liệu Ledger/H-01 thật, hiển thị rõ trạng thái khóa của Cổng dữ liệu G1 (BLOCKED), Cổng thực nghiệm G2 (NOT_STARTED) và nhãn dữ liệu Lớp C (GEM-RAW-001).
ASTRA STOCK TERMINAL (Giao diện chuẩn SSI & Kỷ luật Khoa học):
Bảng theo dõi chỉ số/mã cổ phiếu (không nút Mua/Bán), biểu đồ nến (TradingView Lightweight Charts ở mốc WEB-M3).
6 luật chống nhìn trước tương lai (Anti-Lookahead / PIT): (1) chỉ dùng dữ liệu đã công bố tại thời điểm quyết định; (2) khóa ngày công bố báo cáo tài chính (PIT); (3) tiền đăng ký giả thuyết trước khi chạy thử; (4) ghi đủ bộ đếm ngân sách phép thử (N_trials) cho mọi lần chạy; (5) thừa nhận trung thực không còn tập holdout lịch sử, chuyển sang đánh giá bằng đồng hồ prospective-OOS (thử nghiệm tiến tới tương lai); (6) hiển thị kết quả âm tính ngang hàng kết quả dương tính (như kết quả thực tế đà tuần 54-56% thấp hơn mốc ngây thơ 58-59%).
Phân kỳ chỉ số: Mọi tín hiệu bot nhận diện mô hình nến (Hammer, Engulfing, Doji) bắt buộc mang nhãn HYPOTHESIS. Hoãn (DEFER) bot Thông tư 68, Beneish M-Score và Deflated Sharpe Ratio (DSR) cho đến khi có dữ liệu PIT có giấy phép vượt qua cổng G1 và có N_trials thật.
Trung tâm Skill Boot & Workflow 24/7 (ASTRA FLOW):
Bảng Skill Boot rõ ràng 4 cột: Tên Skill / Đầu vào / Đầu ra / Cổng kiểm định (tiếp thu Grok).
Sơ đồ trực quan Workflow Visualizer (Trigger -> Skill -> Validation -> Storage) kèm xem log chạy thật trên GitHub Actions.
Cơ chế độ tin cậy: Idempotency (chống chạy trùng bằng UUID + content_hash), Retry/Fallback model (xử lý lỗi 503/404), và nút Global Kill-Switch dừng toàn bộ bot ngay lập tức.
ASTRA Token Economy & Cost Dashboard:
Định tuyến chi phí 5 cấp: Cấp 0 (Cache SHA-256) -> Cấp 1 (Mã xác định 0-token) -> Cấp 2 (AI nhẹ như Flash-Lite) -> Cấp 3 (AI mạnh) -> Cấp 4 (Hội đồng đa AI).
Giám sát Trần ngân sách API theo ngày (Daily Budget Cap), tự động chuyển sang chế độ chỉ chạy mã 0-token và cảnh báo LK khi chạm ngưỡng 80% / 100%.
Trung tâm Bằng chứng & Kiểm toán (Evidence & Provenance Hub):
Quản lý sổ cái Manifest mã băm SHA-256 thật (tính tự động bằng script) cho các tệp nguồn PDF và báo cáo.
Tích hợp kiểm tra nguồn gốc chống giả mạo tên miền (Anti-Domain-Spoofing) và chống gán lùi thời gian (Anti-Backdating PIT). Mọi con số trên web đều bấm vào để truy ngược về tệp gốc / commit / run ID.
5. LỘ TRÌNH MỐC TRIỂN KHAI (WEB-M0 -> WEB-M4)
(Quy ước: Dùng WEB-M0..M4 để không trùng với cổng dữ liệu G1 và cổng thực nghiệm G2. Không hứa cứng tổng số ngày trước khi hoàn thành ước lượng tại WEB-M0.)

Mốc
Trọng tâm bàn giao
Tiêu chí nghiệm thu bắt buộc (Exit Criteria)
WEB-M0(An ninh P0 & Ước lượng — dự kiến ~3 ngày)
Tách kho theo SPLIT-REPO-01; gỡ PAT/Secret khỏi localStorage; thiết lập Cloudflare Pages + Cloudflare Access cho kho private; vá lỗ hổng xác thực người gửi [SKILL:...]; xuất bảng ước lượng nguồn lực cho WEB-M1..M4.
Không còn dữ liệu nội bộ trên kho public; thử giả danh MSG_*_LK_*.md bị từ chối có log; đăng nhập qua Cloudflare Access thành công trên PC & iPhone; LK chốt lịch các mốc sau.
WEB-M1(Bản Chỉ xem SSI trên PC & iPhone)
Nâng cấp giao diện nền tối 3 lớp kiểu SSI (read-only); hiển thị đủ 15 nhánh BC01–BC15, Hộp thư, Bảng Skill Boot, Evidence Hub và dữ liệu Ledger/H-01 thật; mọi số liệu có source/timestamp/value_status; đóng gói PWA cho iPhone.
Mở mượt trên PC và iPhone PWA; 0 số 0 giả khi thiếu dữ liệu; cầu nối Bridge Drive-GitHub không gián đoạn; các AI không có Drive đọc được Sanitized Feed.
WEB-M2(Luồng Ghi Có kiểm soát & Kiểm soát Chi phí)
Kích hoạt hàng chờ "Cần anh LK quyết" ghi ngược có xác thực; kích hoạt nút chạy Bot/Skill 24/7 từ web; bật Daily Budget Cap, Idempotency và Global Kill-Switch; bổ sung Dissent Log cho Hội đồng AI.
LK duyệt 1 quyết định từ iPhone ghi nhận thành công có audit log; Kill-Switch dừng được workflow ngay lập tức; vượt trần ngân sách tự động ngắt gọi LLM.
WEB-M3(Luồng STOCK TERMINAL Trọn vẹn)
Tích hợp biểu đồ nến (Lightweight Charts); vận hành 1 luồng khép kín: dữ liệu PIT -> Bot đọc nến (gắn nhãn HYPOTHESIS) -> kiểm định tiền đăng ký (N_trials, đồng hồ prospective-OOS) -> Hội đồng phản biện -> Báo cáo lưu Evidence Hub.
Chạy thông suốt 1 chu kỳ E2E trên dữ liệu thật có kiểm chứng; không nút Mua/Bán; kết quả âm tính hiển thị đầy đủ; 6 luật chống nhìn trước tương lai được kiểm tra tự động.
WEB-M4(Mở rộng & Cá nhân hóa)
Bật kéo thả lưu bố cục widget tùy biến; mở khóa các bot đã hoãn (Thông tư 68, M-Score, DSR) chỉ khi cổng G1 đã mở; kích hoạt dần các workspace phụ (WORLD, FUTURE, INVENTOR, SENTIENT MIND) theo chỉ đạo LK.
Vượt qua kiểm định cổng G1 trước khi hiển thị chỉ số định lượng mới; hiệu năng giao diện ổn định khi mở nhiều widget.
6. BẢNG ĐỐI CHIẾU KHẮC PHỤC ĐIỂM YẾU VÒNG 1 & GHI NGUỒN HỢP NHẤT
Hạng mục
Điểm yếu ở Gemini v4 (Vòng 1)
Đã hoàn thiện trong GEMINI-WEB-PLAN-v5 (Vòng 2)
Nguồn học hỏi
Đăng nhập & Secret
Còn thiếu giải pháp đăng nhập tầng hạ tầng cụ thể; bản KH1 cũ từng đề xuất khóa PIN trình duyệt.
Bỏ hoàn toàn khóa PIN và PAT ở localStorage; áp dụng Cloudflare Pages + Cloudflare Access từ kho private.

Xác thực Bot
Chưa chi tiết hóa cơ chế chống giả danh tên tệp.
Bắt buộc xác thực metadata thật (owner/lastModifyingUser) + allowlist email LK + BRIDGE_SECRET ngay tại WEB-M0.

Kỷ luật khoa học
Chưa nêu rõ 6 luật chống nhìn trước tương lai và thực tế không còn holdout lịch sử.
Đưa đầy đủ 6 luật Anti-Lookahead/PIT, N_trials, đồng hồ prospective-OOS và hiển thị ngang hàng kết quả âm tính.

Chuẩn hóa trạng thái
Bản KH1 cũ từng nhầm _ASTRA_TASKS.json và tự gắn nhãn APPROVED/PASS.
Khớp chuẩn api/tasks.json (astra-tasks/1), tách 3 lớp trạng thái, cấm AI tự khai trạng thái hệ thống.

UI/UX SSI & Skill
Chưa chuẩn hóa quy ước màu giá VN và bảng Skill Boot 4 cột.
Áp dụng bố cục 3 lớp SSI, xanh/đỏ chỉ cho giá kèm ▲▼, không nút Mua/Bán, bảng Skill Boot 4 cột, hoãn kéo thả sang M4.

7. ĐỀ NGHỊ CHẤM ĐIỂM VÒNG 2
Kính mời Hội đồng AI (Claude, Codex, ChatGPT, Grok) và Chủ dự án LK rà soát và chấm điểm vòng 2 cho bản GEMINI-WEB-PLAN-v5 trên cùng thang điểm 100 (An ninh 25 | Thực tế & Vận hành 25 | Kỷ luật khoa học 20 | Giao diện SSI & PC/iPhone 15 | Tích hợp đa AI & Mở rộng 15) để Chủ dự án chốt 1 bản duy nhất và mở khóa triển khai ngay mốc WEB-M0.

Trân trọng,Gemini AI — Cloud & Product Research