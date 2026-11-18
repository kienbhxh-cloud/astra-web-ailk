# THƯ ĐỒNG BỘ MÃ NGUỒN & ĐẶC TẢ WEB AI-LK CLOUD v2.0 (CHO REPOSITORY `astra-web-ailk`)

- **Mã thư:** MSG_20261118-1504_GEMINI_CLAUDE_WEB_AILK_CLOUD_SPEC_AND_SOURCE
- **Từ:** Gemini (Kiến trúc sư Giải pháp & Điều phối Kỹ thuật — ASTRA OMNIVERSE AI)
- **Đến:** CLAUDE / CLAUDE CODE (và ghi nhận báo cáo LK)
- **Thời gian:** 15:04 ngày 18/11/2026 (UTC+7)
- **Repository mục tiêu:** `kienbhxh-cloud/astra-web-ailk` (GitHub Pages: `https://kienbhxh-cloud.github.io/astra-web-ailk/`)
- **Trạng thái:** [P1 - BẢN CẬP NHẬT ĐẶC TẢ & MÃ NGUỒN TRIỂN KHAI 24/7]

---

## 1. Tóm tắt Kiến trúc Chuyển đổi (PC Local -> GitHub Cloud 24/7)

Theo chỉ đạo của Chủ dự án **LK** (do việc duy trì server Node.js cục bộ trên Windows PC bất tiện khi tắt máy) và thống nhất quy trình tiết kiệm token (áp dụng cơ chế **0-token automation qua GitHub Actions** và **On-Demand Skill Loading**), hệ thống **Web AI-LK** được chuẩn hóa thành kiến trúc **Serverless SPA + GitHub REST API + Lightweight Skill Runner**:

1. **Frontend (`docs/index.html` trên GitHub Pages):**
   - Giao diện quản trị đa AI chạy tĩnh 24/7 trên cả PC và iPhone 13.
   - Đọc/ghi trực tiếp các tệp tin nhắn (`.md`), danh sách kỹ năng (`10_SKILLS/*.md`) và bảng nhiệm vụ (`09_HOP_THU/_ASTRA_TASKS.json`) thông qua GitHub REST API (`https://api.github.com`).
   - Lưu cấu hình (`owner`, `repo`, `branch`, `folder`, `PAT`) cục bộ trong `localStorage` của trình duyệt người dùng, tuyệt đối không hardcode token vào mã nguồn.
2. **Backend Tự động hóa 0-Token (`.github/workflows/astra-skill-agent.yml`):**
   - Chỉ kích hoạt khi có commit mới từ Chủ dự án (`09_HOP_THU/MSG_*_LK_*.md`), tránh vòng lặp vô hạn.
   - Nhận diện thẻ `[SKILL:<TEN_SKILL>]`, nạp duy nhất 1 tệp kỹ năng tương ứng trong `10_SKILLS/` (cắt giảm 70–85% input token).
   - Thực thi qua Gemini API Free Tier / OpenRouter Free Models và tự động commit báo cáo phản hồi `*_REPLY.md` vào `09_HOP_THU/`.
3. **Cầu nối Google Drive (`09_HOP_THU`):**
   - Hỗ trợ đồng bộ bản sao sang Google Drive thông qua Google Apps Script Webhook (tùy chọn cấu hình URL Webhook trên giao diện Web AI-LK) để các tác nhân đọc qua Google Drive Connector luôn có dữ liệu mới nhất.

---

## 2. Yêu cầu Triển khai Dành cho Claude / Claude Code

Đề nghị **Claude / Claude Code** thực hiện trọn gói trong 1 phiên (batch) trên repository `kienbhxh-cloud/astra-web-ailk`:

1. **Cập nhật tệp `docs/index.html`** theo đúng mã nguồn chuẩn hóa tại Mục 3 bên dưới (hỗ trợ mặc định repo `astra-web-ailk`, chọn Skill động từ `10_SKILLS/`, quản lý Hộp thư, Diễn đàn, Bảng nhiệm vụ Kanban và nút xác nhận `[ACK_BY_LK]`).
2. **Tạo cấu trúc thư mục & tệp khởi tạo trên repo `astra-web-ailk`:**
   - `09_HOP_THU/README.md` (giữ chỗ thư mục hộp thư).
   - `10_SKILLS/TONG_HOP_BAO_CAO.md` (Skill tóm tắt báo cáo tối đa 5 ý chính).
   - `10_SKILLS/PHAN_BIEN_KY_THUAT.md` (Skill kiểm toán mã nguồn và đề xuất bản vá).
   - `.github/workflows/astra-skill-agent.yml` (Workflow tự động chạy Skill khi có thư `MSG_*_LK_*.md`).
3. **Checkpoint cuối phiên:** Xuất 01 báo cáo nghiệm thu kèm mã commit SHA vào `09_HOP_THU` để LK và Gemini đối chiếu.

---

## 3. Mã nguồn Hoàn chỉnh `docs/index.html` (Production Ready)

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>WEB AI-LK CLOUD | Trung tâm Chỉ huy Đa AI 24/7</title>
  <style>
    :root {
      --bg: #0f172a;
      --panel: #1e293b;
      --panel-2: #334155;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --success: #10b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }
    header {
      background: #0b1120;
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    .brand { display: flex; align-items: center; gap: 10px; }
    .brand h1 { margin: 0; font-size: 17px; }
    .badge {
      background: rgba(16, 185, 129, 0.15);
      color: var(--success);
      border: 1px solid rgba(16, 185, 129, 0.4);
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
    }
    .status-bar {
      background: var(--panel);
      padding: 8px 20px;
      font-size: 13px;
      color: var(--muted);
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      border-bottom: 1px solid var(--border);
    }
    .status-bar code { color: #38bdf8; background: #0f172a; padding: 2px 6px; border-radius: 4px; }
    nav {
      display: flex;
      gap: 6px;
      padding: 12px 20px 0;
      border-bottom: 1px solid var(--border);
      overflow-x: auto;
    }
    .tab-btn {
      background: transparent;
      color: var(--muted);
      border: none;
      border-bottom: 2px solid transparent;
      padding: 10px 14px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      min-height: 44px;
      white-space: nowrap;
    }
    .tab-btn.active { color: #fff; border-bottom-color: var(--primary); }
    main { max-width: 1280px; margin: 0 auto; padding: 20px; }
    .grid-2 { display: grid; grid-template-columns: 360px 1fr; gap: 20px; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
    }
    .msg-item {
      padding: 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #162032;
      margin-bottom: 10px;
      cursor: pointer;
    }
    .msg-item:hover, .msg-item.selected { border-color: var(--primary); background: #1e2d4a; }
    .msg-meta { display: flex; justify-content: space-between; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
    .sender-tag { font-weight: 700; color: #60a5fa; }
    .msg-title { font-weight: 600; font-size: 14px; color: #f1f5f9; }
    pre.content-view {
      white-space: pre-wrap;
      word-wrap: break-word;
      background: #0b1120;
      padding: 16px;
      border-radius: 8px;
      border: 1px solid var(--border);
      font-family: Consolas, 'Courier New', monospace;
      font-size: 13.5px;
      max-height: 60vh;
      overflow-y: auto;
      color: #e2e8f0;
    }
    input, select, textarea {
      width: 100%;
      background: #0f172a;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 12px;
      border-radius: 6px;
      font-size: 14px;
      margin-top: 6px;
      margin-bottom: 12px;
      font-family: inherit;
    }
    button.btn {
      background: var(--primary);
      color: white;
      border: none;
      padding: 10px 16px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      min-height: 44px;
      font-size: 14px;
    }
    button.btn:hover { background: var(--primary-hover); }
    button.btn-secondary { background: var(--panel-2); }
    button.btn-success { background: var(--success); color: #052e16; }
    button.btn-sm { padding: 6px 10px; min-height: 36px; font-size: 12.5px; }
    .task-board { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
    @media (max-width: 1000px) { .task-board { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 600px) { .task-board { grid-template-columns: 1fr; } }
    .col { background: #141e30; border: 1px solid var(--border); border-radius: 8px; padding: 12px; min-height: 320px; }
    .col h3 { margin: 0 0 12px; font-size: 13.5px; text-transform: uppercase; color: var(--muted); }
    .task-card { background: var(--panel); border: 1px solid var(--border); border-radius: 6px; padding: 10px; margin-bottom: 10px; }
    .toast {
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: var(--success);
      color: #022c22;
      font-weight: 700;
      padding: 12px 18px;
      border-radius: 8px;
      display: none;
      z-index: 99;
    }
    .hidden { display: none !important; }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>ASTRA OMNIVERSE AI — WEB AI-LK</h1>
      <span class="badge">GITHUB CLOUD 24/7</span>
    </div>
    <div style="display:flex; gap:8px;">
      <button class="btn btn-secondary btn-sm" onclick="syncFromGitHub()">↻ Đồng bộ GitHub</button>
      <button class="btn btn-sm" onclick="switchTab('settings')">⚙️ Cấu hình Token</button>
    </div>
  </header>

  <div class="status-bar">
    <div>Kho lưu trữ: <code id="repoDisplay">kienbhxh-cloud/astra-web-ailk/09_HOP_THU</code></div>
    <div id="connStatus">Trạng thái: Đang kiểm tra kết nối...</div>
  </div>

  <nav>
    <button class="tab-btn active" id="tab-inbox" onclick="switchTab('inbox')">📥 Hộp thư AI (<span id="count-inbox">0</span>)</button>
    <button class="tab-btn" id="tab-forum" onclick="switchTab('forum')">💬 Diễn đàn (<span id="count-forum">0</span>)</button>
    <button class="tab-btn" id="tab-tasks" onclick="switchTab('tasks')">📋 Bảng Nhiệm vụ (<span id="count-tasks">0</span>)</button>
    <button class="tab-btn" id="tab-compose" onclick="switchTab('compose')">✍️ Gửi Chỉ đạo</button>
    <button class="tab-btn" id="tab-settings" onclick="switchTab('settings')">🔑 Kết nối GitHub</button>
  </nav>

  <main>
    <!-- TAB 1: HỘP THƯ -->
    <section id="view-inbox">
      <div class="grid-2">
        <div class="card">
          <select id="filterSender" onchange="renderInbox()" style="margin-top:0;">
            <option value="ALL">Tất cả tác nhân AI</option>
            <option value="LK">LK (Chủ dự án)</option>
            <option value="Claude">Claude / Claude Code</option>
            <option value="ChatGPT">ChatGPT / Codex</option>
            <option value="Gemini">Gemini</option>
            <option value="Grok">Grok</option>
            <option value="AGENT">Skill Agent Tự động</option>
          </select>
          <div id="inboxList" style="max-height:66vh; overflow-y:auto;"></div>
        </div>
        <div class="card" id="messageDetail">
          <p style="color:var(--muted);">Chọn một thư hoặc báo cáo bên trái để đọc chi tiết (hoặc vào tab <b>🔑 Kết nối GitHub</b> nếu chưa nhập Token).</p>
        </div>
      </div>
    </section>

    <!-- TAB 2: DIỄN ĐÀN -->
    <section id="view-forum" class="hidden">
      <div id="forumContainer"></div>
    </section>

    <!-- TAB 3: BẢNG NHIỆM VỤ -->
    <section id="view-tasks" class="hidden">
      <div class="card" style="margin-bottom:16px;">
        <h3 style="margin-top:0;">Giao nhiệm vụ mới trên GitHub Cloud</h3>
        <div style="display:grid; grid-template-columns: 2fr 1fr 1fr auto; gap:10px; align-items:end;">
          <div>
            <label style="font-size:12px; color:var(--muted);">Nội dung nhiệm vụ</label>
            <input id="newTaskTitle" placeholder="Nhập nhiệm vụ thực tế..." style="margin:4px 0 0;" />
          </div>
          <div>
            <label style="font-size:12px; color:var(--muted);">AI phụ trách</label>
            <select id="newTaskAssignee" style="margin:4px 0 0;">
              <option value="Gemini">Gemini</option>
              <option value="Claude">Claude</option>
              <option value="Claude Code">Claude Code</option>
              <option value="ChatGPT">ChatGPT</option>
              <option value="Codex">Codex</option>
              <option value="Grok">Grok</option>
              <option value="ALL">Tất cả 4 AI</option>
            </select>
          </div>
          <div>
            <label style="font-size:12px; color:var(--muted);">Ưu tiên</label>
            <select id="newTaskPriority" style="margin:4px 0 0;">
              <option value="P0">P0 - Khẩn cấp</option>
              <option value="P1">P1 - Cao</option>
              <option value="P2">P2 - Bình thường</option>
            </select>
          </div>
          <button class="btn" onclick="createTask()">+ Giao việc</button>
        </div>
      </div>
      <div class="task-board">
        <div class="col"><h3>📌 Chờ xử lý (TODO)</h3><div id="col-TODO"></div></div>
        <div class="col"><h3>⚡ Đang làm (DOING)</h3><div id="col-DOING"></div></div>
        <div class="col"><h3>🚫 Bị chặn (BLOCKED)</h3><div id="col-BLOCKED"></div></div>
        <div class="col"><h3>✅ Hoàn thành (DONE)</h3><div id="col-DONE"></div></div>
      </div>
    </section>

    <!-- TAB 4: SOẠN THƯ & GỌI SKILL -->
    <section id="view-compose" class="hidden">
      <div class="card" style="max-width:760px;">
        <h3 style="margin-top:0;">Gửi Chỉ đạo trực tiếp lên GitHub (09_HOP_THU)</h3>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
          <div>
            <label>Người nhận (AI)</label>
            <select id="msgReceiver">
              <option value="ALL">ALL (Tất cả 4 AI)</option>
              <option value="GEMINI">Gemini</option>
              <option value="CLAUDE">Claude / Claude Code</option>
              <option value="CHATGPT">ChatGPT / Codex</option>
              <option value="GROK">Grok</option>
            </select>
          </div>
          <div>
            <label>Kỹ năng áp dụng (Tiết kiệm Token)</label>
            <select id="msgSkill">
              <option value="">-- Không gọi Skill tự động --</option>
              <option value="TONG_HOP_BAO_CAO">TONG_HOP_BAO_CAO (Tóm tắt 5 ý)</option>
              <option value="PHAN_BIEN_KY_THUAT">PHAN_BIEN_KY_THUAT (Kiểm toán code)</option>
              <option value="SOAN_THAO_HANH_CHINH">SOAN_THAO_HANH_CHINH (Văn bản chuẩn)</option>
            </select>
          </div>
        </div>
        <label>Chủ đề (Topic)</label>
        <input id="msgTopic" placeholder="Ví dụ: P0_CHI_DAO_MOI" />
        <label>Nội dung</label>
        <textarea id="msgBody" rows="8" placeholder="Nhập nội dung chỉ đạo..."></textarea>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <button class="btn" onclick="sendMessage()">🚀 Đăng trực tiếp lên GitHub</button>
          <button class="btn btn-secondary" onclick="copyDispatchPrompt()">📋 Copy lệnh gọi AI</button>
        </div>
      </div>
    </section>

    <!-- TAB 5: CẤU HÌNH KẾT NỐI GITHUB & DRIVE WEBHOOK -->
    <section id="view-settings" class="hidden">
      <div class="card" style="max-width:640px;">
        <h3 style="margin-top:0;">Cấu hình Kết nối GitHub & Đồng bộ Drive</h3>
        <p style="font-size:13px; color:var(--muted);">Thông tin chỉ lưu cục bộ trên trình duyệt của thiết bị này.</p>
        <label>Tài khoản / Tổ chức GitHub (Owner)</label>
        <input id="cfgOwner" value="kienbhxh-cloud" />
        <label>Tên Repository</label>
        <input id="cfgRepo" value="astra-web-ailk" />
        <label>Nhánh (Branch)</label>
        <input id="cfgBranch" value="main" />
        <label>Thư mục Hộp thư trên Repo</label>
        <input id="cfgFolder" value="09_HOP_THU" />
        <label>GitHub Personal Access Token (Quyền Contents Read & Write)</label>
        <input id="cfgToken" type="password" placeholder="ghp_... hoặc github_pat_..." />
        <label>Google Apps Script Webhook URL (Tùy chọn - Đồng bộ sang Drive 09_HOP_THU)</label>
        <input id="cfgWebhook" placeholder="https://script.google.com/macros/s/.../exec" />
        <button class="btn" onclick="saveSettings()">💾 Lưu cấu hình & Kết nối ngay</button>
      </div>
    </section>
  </main>

  <div id="toast" class="toast"></div>

  <script>
    const CFG_KEY = 'ASTRA_WEB_AILK_GITHUB_CFG';
    let STATE = { messages: [], tasks: [], tasksSha: null, selectedPath: null };

    function getCfg() {
      const saved = JSON.parse(localStorage.getItem(CFG_KEY) || '{}');
      return {
        owner: saved.owner || 'kienbhxh-cloud',
        repo: saved.repo || 'astra-web-ailk',
        branch: saved.branch || 'main',
        folder: saved.folder || '09_HOP_THU',
        token: saved.token || '',
        webhook: saved.webhook || ''
      };
    }

    function saveSettings() {
      const cfg = {
        owner: document.getElementById('cfgOwner').value.trim(),
        repo: document.getElementById('cfgRepo').value.trim(),
        branch: document.getElementById('cfgBranch').value.trim() || 'main',
        folder: document.getElementById('cfgFolder').value.trim().replace(/^\/+|\/+$/g, ''),
        token: document.getElementById('cfgToken').value.trim(),
        webhook: document.getElementById('cfgWebhook').value.trim()
      };
      localStorage.setItem(CFG_KEY, JSON.stringify(cfg));
      showToast('✅ Đã lưu cấu hình kết nối!');
      syncFromGitHub();
      switchTab('inbox');
    }

    function showToast(text) {
      const t = document.getElementById('toast');
      t.textContent = text;
      t.style.display = 'block';
      setTimeout(() => { t.style.display = 'none'; }, 3000);
    }

    function switchTab(tab) {
      ['inbox', 'forum', 'tasks', 'compose', 'settings'].forEach(name => {
        document.getElementById('view-' + name).classList.toggle('hidden', name !== tab);
        document.getElementById('tab-' + name).classList.toggle('active', name === tab);
      });
    }

    function utf8ToBase64(str) {
      return btoa(unescape(encodeURIComponent(str)));
    }

    function base64ToUtf8(b64) {
      return decodeURIComponent(escape(atob(b64.replace(/\n/g, ''))));
    }

    async function ghFetch(apiPath, options = {}) {
      const cfg = getCfg();
      const headers = {
        'Accept': 'application/vnd.github+json',
        ...(cfg.token ? { 'Authorization': 'Bearer ' + cfg.token } : {}),
        ...(options.headers || {})
      };
      const res = await fetch('https://api.github.com' + apiPath, { ...options, headers });
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`GitHub API ${res.status}: ${errText}`);
      }
      return res.json();
    }

    function detectSender(fileName) {
      const u = fileName.toUpperCase();
      if (u.includes('_AGENT_')) return 'Skill Agent Tự động';
      if (u.includes('_LK_') || (u.startsWith('MSG_') && u.includes('_LK'))) return 'LK (Chủ dự án)';
      if (u.includes('CLAUDE_CODE') || u.includes('CLAUDE-CODE')) return 'Claude Code';
      if (u.includes('CLAUDE')) return 'Claude';
      if (u.includes('CODEX')) return 'Codex';
      if (u.includes('GPT') || u.includes('CHATGPT')) return 'ChatGPT';
      if (u.includes('GEMINI')) return 'Gemini';
      if (u.includes('GROK')) return 'Grok';
      return 'SYSTEM';
    }

    async function syncFromGitHub() {
      const cfg = getCfg();
      document.getElementById('repoDisplay').textContent = `${cfg.owner}/${cfg.repo}/${cfg.folder}`;
      document.getElementById('cfgOwner').value = cfg.owner;
      document.getElementById('cfgRepo').value = cfg.repo;
      document.getElementById('cfgBranch').value = cfg.branch;
      document.getElementById('cfgFolder').value = cfg.folder;
      document.getElementById('cfgToken').value = cfg.token;
      document.getElementById('cfgWebhook').value = cfg.webhook;

      if (!cfg.token) {
        document.getElementById('connStatus').innerHTML = '<span style="color:#f59e0b;">⚠️ Chưa nhập GitHub Token (Vào tab Kết nối GitHub)</span>';
        return;
      }

      try {
        document.getElementById('connStatus').textContent = '⏳ Đang đồng bộ từ GitHub...';
        const items = await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${cfg.folder}?ref=${cfg.branch}`);
        const files = Array.isArray(items) ? items.filter(f => f.type === 'file') : [];

        // Tự động nạp danh sách Skill từ thư mục 10_SKILLS nếu có
        try {
          const skillItems = await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/10_SKILLS?ref=${cfg.branch}`);
          if (Array.isArray(skillItems)) {
            const mdSkills = skillItems.filter(s => s.name.endsWith('.md') && s.name !== 'README.md');
            if (mdSkills.length) {
              const sel = document.getElementById('msgSkill');
              sel.innerHTML = '<option value="">-- Không gọi Skill tự động --</option>' +
                mdSkills.map(s => {
                  const code = s.name.replace(/\.md$/i, '').toUpperCase();
                  return `<option value="${code}">${code}</option>`;
                }).join('');
            }
          }
        } catch (_) {}

        // Tải Tasks nếu có
        const taskFile = files.find(f => f.name === '_ASTRA_TASKS.json');
        if (taskFile) {
          const tData = await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${taskFile.path}?ref=${cfg.branch}`);
          STATE.tasks = JSON.parse(base64ToUtf8(tData.content));
          STATE.tasksSha = tData.sha;
        } else {
          STATE.tasks = [];
          STATE.tasksSha = null;
        }

        // Danh sách thư
        const msgFiles = files
          .filter(f => /\.(md|txt|log)$/i.test(f.name) && !f.name.startsWith('_ASTRA_') && f.name.toUpperCase() !== 'README.MD')
          .sort((a, b) => b.name.localeCompare(a.name));

        STATE.messages = msgFiles.map(f => ({
          name: f.name,
          path: f.path,
          sha: f.sha,
          sender: detectSender(f.name),
          topic: f.name.replace(/\.[^.]+$/, '').replace(/[_-]+/g, ' '),
          content: null
        }));

        document.getElementById('count-inbox').textContent = STATE.messages.length;
        document.getElementById('count-tasks').textContent = STATE.tasks.length;
        document.getElementById('connStatus').innerHTML = '<span style="color:#10b981;">✅ Đã kết nối GitHub 24/7</span>';

        renderInbox();
        renderForum();
        renderTasks();
      } catch (err) {
        document.getElementById('connStatus').innerHTML = `<span style="color:#ef4444;">❌ Lỗi kết nối: ${escapeHtml(err.message)}</span>`;
      }
    }

    async function selectMessage(path) {
      STATE.selectedPath = path;
      renderInbox();
      const msg = STATE.messages.find(m => m.path === path);
      if (!msg) return;

      const detail = document.getElementById('messageDetail');
      detail.innerHTML = '<p style="color:var(--muted);">⏳ Đang tải nội dung tệp từ GitHub...</p>';

      try {
        if (!msg.content) {
          const cfg = getCfg();
          const data = await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${msg.path}?ref=${cfg.branch}`);
          msg.content = base64ToUtf8(data.content);
          msg.sha = data.sha;
        }
        const isAcked = msg.content.includes('[ACK_BY_LK]');
        detail.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
            <div>
              <h2 style="margin:0 0 4px; font-size:17px;">${escapeHtml(msg.topic)}</h2>
              <div style="font-size:12.5px; color:var(--muted);">Từ: <strong>${msg.sender}</strong> | Tệp: <code>${msg.name}</code></div>
            </div>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-success btn-sm" onclick="ackMessage('${msg.path}')">${isAcked ? '✅ Đã ACK' : '✔ Xác nhận ACK'}</button>
              <button class="btn btn-secondary btn-sm" onclick="copyTextPrompt('${msg.name}')">📋 Copy lệnh AI</button>
            </div>
          </div>
          <pre class="content-view">${escapeHtml(msg.content)}</pre>
        `;
      } catch (err) {
        detail.innerHTML = `<p style="color:#ef4444;">Lỗi đọc tệp: ${escapeHtml(err.message)}</p>`;
      }
    }

    function renderInbox() {
      const filter = document.getElementById('filterSender').value;
      const list = document.getElementById('inboxList');
      const filtered = STATE.messages.filter(m => filter === 'ALL' || m.sender.toLowerCase().includes(filter.toLowerCase()) || m.name.toLowerCase().includes(filter.toLowerCase()));

      if (!filtered.length) {
        list.innerHTML = '<p style="color:var(--muted); font-size:13px;">Chưa có thư nào trong thư mục 09_HOP_THU trên GitHub.</p>';
        return;
      }

      list.innerHTML = filtered.map(m => `
        <div class="msg-item ${STATE.selectedPath === m.path ? 'selected' : ''}" onclick="selectMessage('${m.path}')">
          <div class="msg-meta"><span class="sender-tag">${m.sender}</span><span>GitHub</span></div>
          <div class="msg-title">${escapeHtml(m.topic)}</div>
          <div style="font-size:11px; color:var(--muted); margin-top:3px;">${m.name}</div>
        </div>
      `).join('');

      if (!STATE.selectedPath && filtered.length) selectMessage(filtered[0].path);
    }

    function renderForum() {
      const groups = {};
      for (const m of STATE.messages) {
        const key = m.topic.split(' ').slice(0, 4).join(' ') || 'CHUNG';
        if (!groups[key]) groups[key] = [];
        groups[key].push(m);
      }
      const keys = Object.keys(groups);
      document.getElementById('count-forum').textContent = keys.length;
      document.getElementById('forumContainer').innerHTML = keys.map(k => `
        <div class="card" style="margin-bottom:14px;">
          <h3 style="margin:0 0 8px; color:#38bdf8;">🧵 Chủ đề: ${escapeHtml(k)} (${groups[k].length} bài)</h3>
          ${groups[k].map(i => `<div style="font-size:13px; padding:6px 0; border-top:1px solid var(--border);"><strong>${i.sender}</strong> — <code>${i.name}</code> <button class="btn btn-secondary btn-sm" style="margin-left:8px;" onclick="switchTab('inbox'); selectMessage('${i.path}')">Đọc</button></div>`).join('')}
        </div>
      `).join('');
    }

    function renderTasks() {
      ['TODO', 'DOING', 'BLOCKED', 'DONE'].forEach(status => {
        const col = document.getElementById('col-' + status);
        const items = STATE.tasks.filter(t => t.status === status);
        col.innerHTML = items.map(t => `
          <div class="task-card">
            <div style="display:flex; justify-content:space-between; font-size:11.5px; color:var(--muted); margin-bottom:4px;">
              <span><strong>${escapeHtml(t.assignee)}</strong></span><span>${t.priority}</span>
            </div>
            <div style="font-size:13.5px; font-weight:600; margin-bottom:8px;">${escapeHtml(t.title)}</div>
            <div style="display:flex; gap:4px; flex-wrap:wrap;">
              ${status !== 'DOING' ? `<button class="btn btn-secondary btn-sm" onclick="moveTask('${t.id}','DOING')">Làm</button>` : ''}
              ${status !== 'DONE' ? `<button class="btn btn-success btn-sm" onclick="moveTask('${t.id}','DONE')">Xong</button>` : ''}
              ${status !== 'BLOCKED' ? `<button class="btn btn-secondary btn-sm" onclick="moveTask('${t.id}','BLOCKED')">Chặn</button>` : ''}
              <button class="btn btn-secondary btn-sm" onclick="deleteTask('${t.id}')">Xóa</button>
            </div>
          </div>
        `).join('');
      });
    }

    async function sendMessage() {
      const cfg = getCfg();
      if (!cfg.token) return alert('Vui lòng nhập GitHub Token trước!');
      const receiver = document.getElementById('msgReceiver').value;
      const skill = document.getElementById('msgSkill').value;
      const topic = document.getElementById('msgTopic').value.trim();
      const body = document.getElementById('msgBody').value.trim();
      if (!topic || !body) return alert('Vui lòng nhập Chủ đề và Nội dung!');

      const d = new Date();
      const pad = n => String(n).padStart(2, '0');
      const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}`;
      const slug = topic.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').toUpperCase().slice(0, 35);
      const fileName = `MSG_${stamp}_LK_${receiver}_${slug}.md`;
      const skillTag = skill ? `[SKILL:${skill}]\n` : '';
      const md = `${skillTag}# CHỈ ĐẠO CHỦ DỰ ÁN ASTRA OMNIVERSE AI\n- **Từ:** LK (Chủ dự án)\n- **Đến:** ${receiver}\n- **Chủ đề:** ${topic}\n- **Thời gian:** ${d.toLocaleString('vi-VN')}\n\n---\n\n${body}`;

      await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${cfg.folder}/${fileName}`, {
        method: 'PUT',
        body: JSON.stringify({
          message: `LK gửi chỉ đạo: ${fileName}`,
          content: utf8ToBase64(md),
          branch: cfg.branch
        })
      });

      // Đồng bộ sang Google Drive qua Webhook nếu đã cấu hình
      if (cfg.webhook) {
        fetch(cfg.webhook, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fileName, content: md })
        }).catch(() => {});
      }

      document.getElementById('msgTopic').value = '';
      document.getElementById('msgBody').value = '';
      showToast('✅ Đã đăng lên GitHub: ' + fileName);
      await syncFromGitHub();
      switchTab('inbox');
    }

    async function ackMessage(path) {
      const cfg = getCfg();
      const msg = STATE.messages.find(m => m.path === path);
      if (!msg || !msg.content || msg.content.includes('[ACK_BY_LK]')) return;
      const updated = `${msg.content}\n\n---\n[ACK_BY_LK] Đã xác nhận bởi Chủ dự án LK lúc ${new Date().toLocaleString('vi-VN')}\n`;

      await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${msg.path}`, {
        method: 'PUT',
        body: JSON.stringify({
          message: `ACK bởi LK: ${msg.name}`,
          content: utf8ToBase64(updated),
          sha: msg.sha,
          branch: cfg.branch
        })
      });
      showToast('✅ Đã ghi nhận ACK trên GitHub!');
      msg.content = null;
      await syncFromGitHub();
      selectMessage(path);
    }

    async function persistTasks() {
      const cfg = getCfg();
      const res = await ghFetch(`/repos/${cfg.owner}/${cfg.repo}/contents/${cfg.folder}/_ASTRA_TASKS.json`, {
        method: 'PUT',
        body: JSON.stringify({
          message: 'Cập nhật bảng nhiệm vụ Web AI-LK',
          content: utf8ToBase64(JSON.stringify(STATE.tasks, null, 2)),
          ...(STATE.tasksSha ? { sha: STATE.tasksSha } : {}),
          branch: cfg.branch
        })
      });
      STATE.tasksSha = res.content.sha;
      renderTasks();
      document.getElementById('count-tasks').textContent = STATE.tasks.length;
    }

    async function createTask() {
      const title = document.getElementById('newTaskTitle').value.trim();
      if (!title) return;
      STATE.tasks.unshift({
        id: 'TASK-' + Date.now().toString().slice(-5),
        title,
        assignee: document.getElementById('newTaskAssignee').value,
        priority: document.getElementById('newTaskPriority').value,
        status: 'TODO',
        createdAt: new Date().toISOString()
      });
      document.getElementById('newTaskTitle').value = '';
      await persistTasks();
      showToast('✅ Đã giao nhiệm vụ lên GitHub!');
    }

    async function moveTask(id, status) {
      STATE.tasks = STATE.tasks.map(t => t.id === id ? { ...t, status } : t);
      await persistTasks();
    }

    async function deleteTask(id) {
      STATE.tasks = STATE.tasks.filter(t => t.id !== id);
      await persistTasks();
    }

    function copyDispatchPrompt() {
      const receiver = document.getElementById('msgReceiver').value;
      const topic = document.getElementById('msgTopic').value.trim() || 'CHI_DAO_MOI';
      const body = document.getElementById('msgBody').value.trim();
      navigator.clipboard.writeText(`[CHỈ ĐẠO TỪ LK -> ${receiver}] Chủ đề: ${topic}\nHãy kiểm tra thư mục 09_HOP_THU trên GitHub repository kienbhxh-cloud/astra-web-ailk, đọc chỉ đạo mới nhất và lưu báo cáo phản hồi trực tiếp vào 09_HOP_THU.\nNội dung: ${body}`);
      showToast('📋 Đã copy lệnh gọi AI!');
    }

    function copyTextPrompt(fileName) {
      navigator.clipboard.writeText(`Hãy đọc tệp "${fileName}" trong thư mục 09_HOP_THU của repository kienbhxh-cloud/astra-web-ailk, thực hiện yêu cầu và lưu báo cáo phản hồi lại vào 09_HOP_THU.`);
      showToast('📋 Đã copy lệnh phản hồi!');
    }

    function escapeHtml(str) {
      return String(str).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[s]));
    }

    syncFromGitHub();
  </script>
</body>
</html>
```

---

## 4. Workflow GitHub Actions Tự động Chạy Skill (0-Token Overhead)

Tệp `.github/workflows/astra-skill-agent.yml`:

```yaml
name: ASTRA Skill Agent Runner

on:
  push:
    paths:
      - '09_HOP_THU/MSG_*_LK_*.md'

permissions:
  contents: write

jobs:
  run-skill-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Execute Lightweight Skill Agent
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          node -e '
          const fs = require("fs");
          const { execSync } = require("child_process");

          const changedFile = execSync("git diff-tree --no-commit-id --name-only -r HEAD")
            .toString().trim().split("\n")
            .find(f => f.startsWith("09_HOP_THU/MSG_") && f.includes("_LK_"));

          if (!changedFile || !fs.existsSync(changedFile)) process.exit(0);

          const msgContent = fs.readFileSync(changedFile, "utf8");
          const skillMatch = msgContent.match(/\[SKILL:([A-Z0-9_-]+)\]/i);
          if (!skillMatch) process.exit(0);

          const skillName = skillMatch[1].toUpperCase();
          const skillPath = `10_SKILLS/${skillName}.md`;
          const skillInstruction = fs.existsSync(skillPath)
            ? fs.readFileSync(skillPath, "utf8")
            : "Thực hiện yêu cầu ngắn gọn, đi thẳng vào kết quả.";

          const prompt = `VAI TRÒ: Trợ lý thực thi ASTRA.\nKỸ NĂNG ÁP DỤNG:\n${skillInstruction}\n\nYÊU CẦU:\n${msgContent}`;

          async function run() {
            const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { maxOutputTokens: 1500, temperature: 0.2 }
              })
            });
            const data = await res.json();
            const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || "Không có phản hồi từ API.";
            const outName = changedFile.replace("_LK_", "_AGENT_").replace(".md", "_REPLY.md");
            fs.writeFileSync(outName, `# BÁO CÁO TỰ ĐỘNG (SKILL: ${skillName})\n\n${reply}\n`);
          }
          run();
          '

      - name: Commit Agent Reply
        run: |
          git config user.name "ASTRA-Skill-Agent"
          git config user.email "agent@astra-omniverse.local"
          git add 09_HOP_THU/*_REPLY.md
          git diff --staged --quiet || git commit -m "Agent hoàn thành tác vụ Skill"
          git push
```
