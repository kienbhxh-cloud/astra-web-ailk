#!/usr/bin/env python3
"""ASTRA Skill Runner: verify SHA-256, rebuild AI_FEED.md, append api/skill_logs.json.
Stdlib only, no LLM tokens. Exit 1 if integrity check fails."""
import hashlib, json, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://kienbhxh-cloud.github.io/astra-web-ailk"
sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
load = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))

def main():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
    inbox, tasks, logs = load("api/inbox.json"), load("api/tasks.json"), load("api/skill_logs.json")
    problems = []
    for m in inbox["messages"]:
        if sha(m["body"]) != m.get("sha256"):
            problems.append("inbox sha256 mismatch: " + m["id"])
    for t in tasks["tasks"]:
        expect = sha(json.dumps({k: t[k] for k in sorted(t) if k != "sha256"}, ensure_ascii=False, sort_keys=True))
        if expect != t.get("sha256"):
            problems.append("task sha256 mismatch: " + t["id"])
    ids = [m["id"] for m in inbox["messages"]]
    if len(ids) != len(set(ids)):
        problems.append("duplicate inbox ids")

    L = ["# ASTRA AI_FEED (văn bản thuần cho AI đọc trực tiếp, không cần JavaScript hay Google Drive)", "",
         f"Cập nhật: {now} (ICT) | Nguồn: api/inbox.json, api/tasks.json | Kiểm tra SHA-256: " + ("PASS" if not problems else "FAIL"),
         f"JSON: {SITE}/api/inbox.json , {SITE}/api/tasks.json , {SITE}/api/skill_logs.json",
         "Kỷ luật: FACT / UNVERIFIED. Nội dung này chỉ là bản đồng bộ, Google Drive 09_HOP_THU là kho gốc.", "",
         "## NHIỆM VỤ ĐANG MỞ", ""]
    for t in tasks["tasks"]:
        L.append(f"- [{t['id']}] {t['title']} | owner={t['owner']} reviewer={t['reviewer'] or '-'} | {t['status']} | {t['priority']} | {t['note']}")
    L += ["", "## THƯ (mới nhất trước)", ""]
    for m in sorted(inbox["messages"], key=lambda x: x["time"], reverse=True):
        L += [f"### {m['file']}", f"Task: {m['task_id']} | {m['sender']} -> {m['recipient']} | {m['time']} | sha256={m['sha256'][:16]}",
              f"Chủ đề: {m['topic']}", "", m["body"], ""]
    L += ["## GỬI PHẢN HỒI", f"Tạo Issue tại https://github.com/kienbhxh-cloud/astra-web-ailk/issues/new (tiêu đề bắt đầu bằng Task ID). Mọi phản hồi chưa được LK/Claude đưa vào api/inbox.json thì chưa phải thư chính thức.", ""]
    # Giữ phần phản hồi Skill Agent (sau dấu mốc) để không bị ghi đè mỗi lần chạy theo lịch
    MARK = "<!-- ASTRA_SKILL_REPLIES -->"
    feed = ROOT / "AI_FEED.md"
    tail = ""
    if feed.exists():
        old = feed.read_text(encoding="utf-8")
        if MARK in old:
            tail = "\n" + MARK + old.split(MARK, 1)[1]
    feed.write_text("\n".join(L).rstrip() + "\n" + tail, encoding="utf-8")

    logs["runs"].append(dict(time=now, skill="sync_and_verify", result="PASS" if not problems else "FAIL",
                             messages=len(inbox["messages"]), tasks=len(tasks["tasks"]), problems=problems, llm_tokens=0))
    logs["runs"] = logs["runs"][-100:]
    (ROOT / "api/skill_logs.json").write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
    print("PASS" if not problems else "FAIL: " + "; ".join(problems))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
