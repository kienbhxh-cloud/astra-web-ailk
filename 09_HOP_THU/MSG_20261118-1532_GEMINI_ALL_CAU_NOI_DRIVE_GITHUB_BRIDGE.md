# ĐẶC TẢ & MÃ NGUỒN CẦU NỐI ĐỒNG BỘ 2 CHIỀU DRIVE <-> GITHUB (ASTRA BRIDGE v1.0)

- **Mã thư:** MSG_20261118-1532_GEMINI_ALL_CAU_NOI_DRIVE_GITHUB_BRIDGE
- **Từ:** Gemini (Kiến trúc sư Giải pháp — ASTRA OMNIVERSE AI)
- **Đến:** LK (Chủ dự án) & CLAUDE / CLAUDE CODE
- **Thời gian:** 15:32 ngày 18/11/2026 (UTC+7)
- **Mục tiêu:** Đồng bộ dữ liệu 24/7 giữa thư mục Google Drive `09_HOP_THU` và repository GitHub `kienbhxh-cloud/astra-web-ailk` (`09_HOP_THU/`) để mọi AI (dù dùng Drive Connector hay GitHub Connector) đều đọc/ghi chung một nguồn dữ liệu duy nhất mà không cần mở PC.

---

## 1. Kiến trúc Đồng bộ 2 Chiều (Chống lặp vòng & Tiết kiệm tài nguyên)

1. **Chiều 1: Web AI-LK (GitHub) -> Google Drive (`09_HOP_THU`) [Tức thì qua Webhook]:**
   - Khi anh LK gửi chỉ đạo trên Web AI-LK (`https://kienbhxh-cloud.github.io/astra-web-ailk/`) hoặc khi GitHub Actions xuất báo cáo phản hồi (`*_REPLY.md`), Webhook đẩy thẳng nội dung sang **Google Apps Script Web App**.
   - Apps Script kiểm tra xem tệp đã tồn tại trong `09_HOP_THU` trên Drive chưa; nếu chưa có sẽ tạo mới (hoặc cập nhật nếu có thay đổi), đảm bảo Gemini đọc được ngay lập tức.
2. **Chiều 2: Google Drive (`09_HOP_THU`) -> GitHub (`astra-web-ailk`) [Tự động mỗi 5 phút qua Time-driven Trigger]:**
   - Khi Gemini (hoặc bất kỳ AI nào kết nối Drive) lưu thư/báo cáo mới vào `09_HOP_THU` trên Drive, bộ quét định kỳ 5 phút của Google Apps Script sẽ đọc các tệp `.md` / `.txt` (và nội dung Google Docs xuất ra text) mới cập nhật trong 15 phút gần nhất và tự động commit lên thư mục `09_HOP_THU/` của GitHub qua GitHub REST API.
   - Cơ chế **Hash Check (`MD5` lưu trong `PropertiesService`)**: Chỉ đẩy lên GitHub khi nội dung tệp thực sự thay đổi, triệt tiêu hoàn toàn nguy cơ đồng bộ lặp vòng qua lại giữa Drive và GitHub.

---

## 2. Mã nguồn Google Apps Script Hoàn chỉnh (`Code.gs`)

```javascript
/**
 * ASTRA OMNIVERSE AI — CẦU NỐI ĐỒNG BỘ 2 CHIỀU GOOGLE DRIVE <-> GITHUB (24/7)
 * Thư mục Drive: 09_HOP_THU
 * Repository GitHub: kienbhxh-cloud/astra-web-ailk
 */

const CONFIG = {
  GITHUB_OWNER: 'kienbhxh-cloud',
  GITHUB_REPO: 'astra-web-ailk',
  GITHUB_BRANCH: 'main',
  GITHUB_FOLDER: '09_HOP_THU',
  DRIVE_FOLDER_NAME: '09_HOP_THU'
};

// Lấy hoặc lưu cấu hình bí mật an toàn trong Script Properties
function getSecrets() {
  const props = PropertiesService.getScriptProperties();
  return {
    GITHUB_TOKEN: props.getProperty('GITHUB_TOKEN') || '',
    BRIDGE_SECRET: props.getProperty('BRIDGE_SECRET') || 'ASTRA_BRIDGE_2026',
    DRIVE_FOLDER_ID: props.getProperty('DRIVE_FOLDER_ID') || ''
  };
}

/**
 * KHỞI TẠO LẦN ĐẦU: Lưu Token và tự động tìm ID thư mục 09_HOP_THU
 * Thay thế 'YOUR_GITHUB_PAT' bằng Token của anh rồi bấm Run 1 lần duy nhất.
 */
function setupBridge() {
  const props = PropertiesService.getScriptProperties();
  // Dán GitHub Personal Access Token (quyền Contents: Read & Write) vào dòng dưới trước khi chạy setupBridge:
  props.setProperty('GITHUB_TOKEN', 'YOUR_GITHUB_PAT');
  props.setProperty('BRIDGE_SECRET', 'ASTRA_BRIDGE_2026');

  const folders = DriveApp.getFoldersByName(CONFIG.DRIVE_FOLDER_NAME);
  if (folders.hasNext()) {
    const folder = folders.next();
    props.setProperty('DRIVE_FOLDER_ID', folder.getId());
    Logger.log('Đã kết nối thư mục Drive: ' + folder.getName() + ' (' + folder.getId() + ')');
  } else {
    throw new Error('Không tìm thấy thư mục ' + CONFIG.DRIVE_FOLDER_NAME + ' trên Google Drive!');
  }
}

/**
 * CHIỀU 1: NHẬN DỮ LIỆU TỪ WEB AI-LK / GITHUB ACTIONS -> LƯU VÀO GOOGLE DRIVE
 */
function doPost(e) {
  try {
    const secrets = getSecrets();
    const payload = JSON.parse(e.postData.contents || '{}');

    if (payload.secret && payload.secret !== secrets.BRIDGE_SECRET) {
      return jsonResponse({ ok: false, error: 'Sai mã xác thực Bridge Secret' });
    }

    const fileName = String(payload.fileName || '').trim();
    const content = String(payload.content || '');
    if (!fileName || !content) {
      return jsonResponse({ ok: false, error: 'Thiếu fileName hoặc content' });
    }

    const folder = DriveApp.getFolderById(secrets.DRIVE_FOLDER_ID);
    const hash = computeMd5(content);
    const props = PropertiesService.getScriptProperties();
    const cacheKey = 'SYNC_HASH_' + fileName;

    // Bỏ qua nếu nội dung y hệt bản đã đồng bộ
    if (props.getProperty(cacheKey) === hash) {
      return jsonResponse({ ok: true, status: 'UNCHANGED', fileName: fileName });
    }

    const existing = folder.getFilesByName(fileName);
    if (existing.hasNext()) {
      const file = existing.next();
      if (file.getMimeType() === MimeType.GOOGLE_DOCS) {
        DocumentApp.openById(file.getId()).getBody().setText(content);
      } else {
        file.setContent(content);
      }
    } else {
      folder.createFile(fileName, content, MimeType.PLAIN_TEXT);
    }

    props.setProperty(cacheKey, hash);
    return jsonResponse({ ok: true, status: 'SYNCED_TO_DRIVE', fileName: fileName });
  } catch (err) {
    return jsonResponse({ ok: false, error: err.message });
  }
}

function doGet() {
  return jsonResponse({ ok: true, service: 'ASTRA Drive-GitHub Bridge 24/7 Active' });
}

/**
 * CHIỀU 2: QUÉT THƯ MỤC 09_HOP_THU TRÊN DRIVE -> ĐẨY TỆP MỚI LÊN GITHUB
 * Cài Trigger chạy tự động mỗi 5 phút.
 */
function syncDriveToGitHub() {
  const secrets = getSecrets();
  if (!secrets.GITHUB_TOKEN || secrets.GITHUB_TOKEN === 'YOUR_GITHUB_PAT') {
    Logger.log('Chưa cấu hình GITHUB_TOKEN trong setupBridge()');
    return;
  }

  const folder = DriveApp.getFolderById(secrets.DRIVE_FOLDER_ID);
  const files = folder.getFiles();
  const props = PropertiesService.getScriptProperties();
  const cutoffMs = Date.now() - 24 * 60 * 60 * 1000; // Chỉ quét tệp cập nhật trong 24h qua

  while (files.hasNext()) {
    const file = files.next();
    if (file.getLastUpdated().getTime() < cutoffMs) continue;

    let name = file.getName();
    const mime = file.getMimeType();
    let content = '';

    if (mime === MimeType.GOOGLE_DOCS) {
      content = DocumentApp.openById(file.getId()).getBody().getText();
      if (!/\.(md|txt)$/i.test(name)) name += '.md';
    } else if (mime === MimeType.PLAIN_TEXT || /\.(md|txt|json)$/i.test(name)) {
      content = file.getBlob().getDataAsString('UTF-8');
    } else {
      continue;
    }

    if (!content.trim()) continue;

    const hash = computeMd5(content);
    const cacheKey = 'SYNC_HASH_' + name;
    if (props.getProperty(cacheKey) === hash) continue;

    pushFileToGitHub(secrets.GITHUB_TOKEN, name, content);
    props.setProperty(cacheKey, hash);
    Logger.log('Đã đồng bộ lên GitHub: ' + name);
  }
}

function pushFileToGitHub(token, fileName, content) {
  const apiUrl = `https://api.github.com/repos/${CONFIG.GITHUB_OWNER}/${CONFIG.GITHUB_REPO}/contents/${CONFIG.GITHUB_FOLDER}/${encodeURIComponent(fileName)}`;
  const headers = {
    'Authorization': 'Bearer ' + token,
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
  };

  let sha = null;
  const checkRes = UrlFetchApp.fetch(apiUrl + '?ref=' + CONFIG.GITHUB_BRANCH, {
    method: 'get',
    headers: headers,
    muteHttpExceptions: true
  });

  if (checkRes.getResponseCode() === 200) {
    const existingData = JSON.parse(checkRes.getContentText());
    sha = existingData.sha;
  }

  const body = {
    message: 'Bridge Sync từ Drive 09_HOP_THU: ' + fileName,
    content: Utilities.base64Encode(content, Utilities.Charset.UTF_8),
    branch: CONFIG.GITHUB_BRANCH
  };
  if (sha) body.sha = sha;

  const putRes = UrlFetchApp.fetch(apiUrl, {
    method: 'put',
    headers: headers,
    contentType: 'application/json',
    payload: JSON.stringify(body),
    muteHttpExceptions: true
  });

  if (putRes.getResponseCode() >= 300) {
    throw new Error('GitHub Push lỗi (' + putRes.getResponseCode() + '): ' + putRes.getContentText());
  }
}

function computeMd5(text) {
  const raw = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, text, Utilities.Charset.UTF_8);
  return raw.map(b => ('0' + (b & 0xFF).toString(16)).slice(-2)).join('');
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
```

---

## 3. Cập nhật nhỏ cho GitHub Actions (`.github/workflows/astra-skill-agent.yml`)

Để mỗi khi **Skill Agent** trên GitHub chạy xong cũng tự động đẩy báo cáo `*_REPLY.md` sang Google Drive, chỉ cần thêm biến môi trường `DRIVE_WEBHOOK_URL: ${{ secrets.DRIVE_WEBHOOK_URL }}` vào workflow và gọi `fetch(process.env.DRIVE_WEBHOOK_URL, ...)` ngay sau bước ghi tệp phản hồi.
