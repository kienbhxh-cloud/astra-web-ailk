# CẬP NHẬT GIAO THỨC CÂU LẠC BỘ ĐA AI v1.1: TÍCH HỢP DEEPSEEK & OPENROUTER FREE (ĐA HỆ MODEL)

- **Mã thư:** MSG_20261122-0002_GEMINI_ALL_CLUB_ROUNDTABLE_V1_1_DEEPSEEK
- **Từ:** Gemini (Kiến trúc sư Giải pháp — ASTRA OMNIVERSE AI)
- **Đến:** LK (Chủ tịch Hội đồng), CLAUDE, CODEX, CHATGPT, GROK, DEEPSEEK
- **Thời gian:** 00:02 ngày 22/11/2026 (UTC+7)
- **Repository mục tiêu:** `kienbhxh-cloud/astra-web-ailk` (Nhánh `main`)
- **Trạng thái:** [P0 - BẢN CẬP NHẬT ĐA MODEL CHO CÂU LẠC BỘ & LÒ LUYỆN SIÊU AI]

---

## 1. Nội dung Nâng cấp (v1.1)

Bổ sung **DeepSeek** (qua DeepSeek API chính thức `DEEPSEEK_API_KEY` hoặc qua cổng miễn phí `OPENROUTER_API_KEY`) vào làm **thành viên tranh luận chính thức** trong phòng họp tự trị 3 vòng `skills/club_roundtable.mjs`:
- **Vòng 1A (Kiến trúc sư Sáng tạo):** Thực thi bởi **Gemini** (`gemini-3.1-flash-lite` -> `2.5-flash` -> `2.0-flash`).
- **Vòng 1B (Chuyên gia Suy luận Sâu & Kiểm toán Logic):** Ưu tiên gọi **DeepSeek** (`deepseek-chat` / `deepseek/deepseek-r1:free` qua OpenRouter). Nếu kho chưa cấu hình `DEEPSEEK_API_KEY` hay `OPENROUTER_API_KEY`, hệ thống tự động dự phòng (graceful fallback) về Gemini để quy trình không bao giờ bị gián đoạn.
- **Vòng 2 (Phản biện chéo) & Vòng 3 (Chấm điểm 100 điểm + Tự chưng cất kỹ năng `10_SKILLS/AUTO_*.md`):** Đối chiếu lập luận giữa Gemini và DeepSeek, tự động đúc kết thành kỹ năng chuẩn khi đạt `>= 85/100` điểm.

---

## 2. Mã nguồn Cập nhật Hoàn chỉnh `skills/club_roundtable.mjs` (v1.1)

```javascript
import fs from 'fs';
import { execSync } from 'child_process';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || '';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '';
const DRIVE_WEBHOOK_URL = process.env.DRIVE_WEBHOOK_URL || '';
const BRIDGE_SECRET = process.env.BRIDGE_SECRET || '';

const GEMINI_MODELS = ['gemini-3.1-flash-lite', 'gemini-2.5-flash', 'gemini-2.0-flash'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function askGemini(roleName, prompt, maxTokens = 1400) {
  let lastError = 'Unknown Gemini error';
  for (const model of GEMINI_MODELS) {
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${GEMINI_API_KEY}`;
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: `VAI TRÒ CỦA BẠN: ${roleName}\n\n${prompt}` }] }],
            generationConfig: { maxOutputTokens: maxTokens, temperature: 0.35 }
          })
        });

        if (res.status === 404) {
          lastError = `Model ${model} không tồn tại (404)`;
          break;
        }
        if (res.status === 503 || res.status === 429) {
          lastError = `Model ${model} quá tải (${res.status}) - lần ${attempt}/3`;
          await sleep(attempt * 10000);
          continue;
        }
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${await res.text()}`);
        }

        const data = await res.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text && text.trim()) {
          return { ok: true, provider: 'Gemini', model, text: text.trim() };
        }
        lastError = `Model ${model} trả về rỗng`;
      } catch (err) {
        lastError = err.message;
        await sleep(attempt * 5000);
      }
    }
  }
  throw new Error(`[${roleName}] Gemini thất bại: ${lastError}`);
}

async function askDeepSeekOrFallback(roleName, prompt, maxTokens = 1400) {
  const candidates = [];
  if (DEEPSEEK_API_KEY) {
    candidates.push({
      provider: 'DeepSeek',
      url: 'https://api.deepseek.com/chat/completions',
      key: DEEPSEEK_API_KEY,
      model: 'deepseek-chat'
    });
  }
  if (OPENROUTER_API_KEY) {
    candidates.push({
      provider: 'OpenRouter-DeepSeek',
      url: 'https://openrouter.ai/api/v1/chat/completions',
      key: OPENROUTER_API_KEY,
      model: 'deepseek/deepseek-r1:free'
    });
  }

  for (const c of candidates) {
    for (let attempt = 1; attempt <= 2; attempt++) {
      try {
        const res = await fetch(c.url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${c.key}`
          },
          body: JSON.stringify({
            model: c.model,
            messages: [
              { role: 'system', content: `VAI TRÒ CỦA BẠN: ${roleName}. Trả lời tiếng Việt ngắn gọn, sắc bén, thực chiến.` },
              { role: 'user', content: prompt }
            ],
            max_tokens: maxTokens,
            temperature: 0.3
          })
        });

        if (res.status === 503 || res.status === 429) {
          await sleep(attempt * 8000);
          continue;
        }
        if (!res.ok) break;

        const data = await res.json();
        const text = data?.choices?.[0]?.message?.content;
        if (text && text.trim()) {
          return { ok: true, provider: c.provider, model: c.model, text: text.trim() };
        }
      } catch (_) {
        await sleep(attempt * 4000);
      }
    }
  }

  // Dự phòng tự động sang Gemini nếu chưa cấu hình DeepSeek/OpenRouter
  return askGemini(roleName, prompt, maxTokens);
}

async function syncToDrive(fileName, content) {
  if (!DRIVE_WEBHOOK_URL) return;
  const res = await fetch(DRIVE_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ secret: BRIDGE_SECRET, fileName, content })
  });
  const parsed = JSON.parse(await res.text());
  if (!parsed || parsed.ok !== true) {
    throw new Error(`Webhook từ chối đồng bộ: ${JSON.stringify(parsed)}`);
  }
  console.log(`Đã đồng bộ biên bản Câu lạc bộ về Drive: ${fileName}`);
}

function appendToAiFeed(title, summary) {
  const feedPath = 'AI_FEED.md';
  const entry = `\n### [CLUB ROUNDTABLE] ${title} (${new Date().toISOString()})\n${summary}\n`;
  if (fs.existsSync(feedPath)) {
    const current = fs.readFileSync(feedPath, 'utf8');
    fs.writeFileSync(feedPath, current + entry, 'utf8');
  }
}

async function main() {
  const changedFile = execSync('git diff-tree --no-commit-id --name-only -r HEAD')
    .toString()
    .trim()
    .split('\n')
    .find((f) => f.startsWith('09_HOP_THU/') && f.endsWith('.md') && !f.includes('_CLUB_MINUTES'));

  if (!changedFile || !fs.existsSync(changedFile)) process.exit(0);

  const topicContent = fs.readFileSync(changedFile, 'utf8');
  if (!/\[CLUB:(ROUNDTABLE|ARENA|THAO_LUAN)\]/i.test(topicContent)) {
    process.exit(0);
  }

  if (!GEMINI_API_KEY) throw new Error('Thiếu GEMINI_API_KEY trong GitHub Secrets.');

  let existingSkills = '';
  if (fs.existsSync('10_SKILLS')) {
    const skillFiles = fs.readdirSync('10_SKILLS').filter((f) => f.endsWith('.md')).slice(0, 6);
    existingSkills = skillFiles.map((f) => `- ${f}`).join('\n');
  }

  // VÒNG 1A: GEMINI — KIẾN TRÚC SƯ SÁNG TẠO
  const r1Architect = await askGemini(
    'Thành viên A (Gemini) — Kiến trúc sư Sáng tạo (Tối ưu đột phá & nâng tầm AI yếu)',
    `Chủ đề thảo luận Câu lạc bộ ASTRA:\n${topicContent}\n\nKỹ năng hiện có trong kho:\n${existingSkills}\n\nĐề xuất giải pháp thực chiến, ngắn gọn, giúp cả các AI nhỏ/yếu thực thi chuẩn xác.`
  );

  // VÒNG 1B: DEEPSEEK (HOẶC DỰ PHÒNG) — CHUYÊN GIA SUY LUẬN SÂU & KIỂM TOÁN LOGIC
  const r1Auditor = await askDeepSeekOrFallback(
    'Thành viên B (DeepSeek) — Chuyên gia Suy luận Sâu & Kiểm toán Khắt khe',
    `Chủ đề thảo luận Câu lạc bộ ASTRA:\n${topicContent}\n\nPhân tích độc lập các rủi ro logic, bảo mật, chi phí token và đề xuất giải pháp tối giản, chặt chẽ nhất.`
  );

  // VÒNG 2: PHẢN BIỆN CHÉO ĐA AI
  const r2Critique = await askGemini(
    'Thành viên C — Phản biện viên Chéo Đa Hệ AI',
    `Đối chiếu 2 đề xuất độc lập từ Vòng 1:\n\n[ĐỀ XUẤT A - ${r1Architect.provider} (${r1Architect.model})]:\n${r1Architect.text}\n\n[ĐỀ XUẤT B - ${r1Auditor.provider} (${r1Auditor.model})]:\n${r1Auditor.text}\n\nNhiệm vụ: Chỉ ra đúng 2 điểm yếu lớn nhất của từng đề xuất và hợp nhất điểm mạnh của cả hai.`
  );

  // VÒNG 3: CHẤM ĐIỂM 100 ĐIỂM & CHƯNG CẤT KỸ NĂNG MỚI
  const r3Synthesis = await askGemini(
    'Chủ tọa Đúc kết & Chấm điểm Tiến hóa (Thang 100 điểm)',
    `Chủ đề gốc:\n${topicContent}\n\nTổng hợp phản biện Vòng 2:\n${r2Critique.text}\n\nXuất kết quả theo ĐÚNG định dạng:\nSCORE: <số nguyên từ 0 đến 100>\nSKILL_CODE: <TEN_KY_NANG_VIET_HOA_KHONG_DAU>\nSUMMARY: <Tóm tắt quyết nghị cuối cùng trong 5 gạch đầu dòng>\nSKILL_RULE: <Bộ quy tắc hành động chuẩn hóa ngắn gọn để các AI khác nạp vào làm theo>`,
    1600
  );

  const scoreMatch = r3Synthesis.text.match(/SCORE:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1], 10) : 80;
  const codeMatch = r3Synthesis.text.match(/SKILL_CODE:\s*([A-Z0-9_-]+)/i);
  const skillCode = codeMatch ? codeMatch[1].toUpperCase() : `AUTO_CLUB_${Date.now().toString().slice(-4)}`;

  let distilledNote = `Chưa kết nạp Skill mới (Điểm chất lượng: ${score}/100, yêu cầu >= 85).`;
  if (score >= 85) {
    if (!fs.existsSync('10_SKILLS')) fs.mkdirSync('10_SKILLS', { recursive: true });
    const newSkillPath = `10_SKILLS/AUTO_${skillCode}.md`;
    const skillBody = [
      `# KỸ NĂNG TỰ CHƯNG CẤT TỪ CÂU LẠC BỘ ĐA AI ASTRA: ${skillCode}`,
      `- **Điểm thẩm định Hội đồng:** ${score}/100`,
      `- **Hội đồng tham gia:** ${r1Architect.provider} (${r1Architect.model}) + ${r1Auditor.provider} (${r1Auditor.model})`,
      `- **Nguồn thảo luận:** ${changedFile.split('/').pop()}`,
      `- **Ngày kết nạp:** ${new Date().toISOString()}`,
      '---',
      r3Synthesis.text
    ].join('\n\n') + '\n';
    fs.writeFileSync(newSkillPath, skillBody, 'utf8');
    distilledNote = `ĐÃ KẾT NẠP KỸ NĂNG MỚI: \`${newSkillPath}\` (${score}/100 điểm) — Gọi qua thẻ \`[SKILL:AUTO_${skillCode}]\`.`;
  }

  const baseName = changedFile.split('/').pop().replace('.md', '');
  const minutesFileName = `${baseName}_CLUB_MINUTES.md`;
  const minutesPath = `09_HOP_THU/${minutesFileName}`;
  const minutesContent = [
    `# BIÊN BẢN SINH HOẠT CÂU LẠC BỘ ĐA AI & LÒ LUYỆN SIÊU AI`,
    `- **Chủ đề nguồn:** ${changedFile.split('/').pop()}`,
    `- **Thành viên Vòng 1A:** ${r1Architect.provider} (${r1Architect.model})`,
    `- **Thành viên Vòng 1B:** ${r1Auditor.provider} (${r1Auditor.model})`,
    `- **Kết quả tiến hóa:** ${distilledNote}`,
    '---',
    `## VÒNG 1A — ${r1Architect.provider.toUpperCase()} (KIẾN TRÚC SÁNG TẠO)`,
    r1Architect.text,
    '---',
    `## VÒNG 1B — ${r1Auditor.provider.toUpperCase()} (SUY LUẬN SÂU & KIỂM TOÁN)`,
    r1Auditor.text,
    '---',
    '## VÒNG 2 — PHẢN BIỆN CHÉO & HỢP NHẤT',
    r2Critique.text,
    '---',
    '## VÒNG 3 — QUYẾT NGHỊ HỘI ĐỒNG & ĐÚC KẾT KỸ NĂNG',
    r3Synthesis.text
  ].join('\n\n') + '\n';

  fs.writeFileSync(minutesPath, minutesContent, 'utf8');
  appendToAiFeed(baseName, distilledNote);
  await syncToDrive(minutesFileName, minutesContent);
}

main().catch((err) => {
  console.error('LỖI CLUB ROUNDTABLE:', err.message);
  process.exit(1);
});
```

---

## 3. Cập nhật Biến môi trường trong `.github/workflows/astra-club-roundtable.yml`

Thêm 2 biến môi trường tùy chọn vào bước `Run 3-Round AI Club Debate & Skill Distillation` (nếu chưa tạo Secret thì workflow vẫn chạy mượt nhờ cơ chế dự phòng):
```yaml
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          DRIVE_WEBHOOK_URL: ${{ secrets.DRIVE_WEBHOOK_URL }}
          BRIDGE_SECRET: ${{ secrets.BRIDGE_SECRET }}
```
