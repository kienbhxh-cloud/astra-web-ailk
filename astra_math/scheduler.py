"""Web ASTRA — Bộ xếp việc tối ưu cho nhóm AI (U4) bằng CP-SAT.

Đầu vào: danh sách việc (thời lượng theo từng AI có thể làm), quan hệ phụ thuộc (DAG),
cấm phân công (vd Claude không rà bài Anthropic), hạn chót. Mỗi AI làm 1 việc một lúc.
Mục tiêu: tối thiểu thời điểm xong toàn bộ (makespan), sau đó tổng trễ hạn.
Baseline so sánh: lập lịch tham lam theo thứ tự topo, giao cho AI rảnh sớm nhất.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model


@dataclass
class Task:
    name: str
    durations: Dict[str, int]          # AI -> thời lượng (chỉ các AI làm được)
    after: Sequence[str] = ()           # phải làm sau các việc này
    deadline: Optional[int] = None


def solve(tasks: List[Task], time_limit: float = 10.0):
    m = cp_model.CpModel()
    H = sum(max(t.durations.values()) for t in tasks)
    start, end, assign, intervals = {}, {}, {}, {}
    ais = sorted({a for t in tasks for a in t.durations})
    for t in tasks:
        start[t.name] = m.NewIntVar(0, H, f"s_{t.name}")
        end[t.name] = m.NewIntVar(0, H, f"e_{t.name}")
        lits = []
        for a, d in t.durations.items():
            x = m.NewBoolVar(f"x_{t.name}_{a}")
            iv = m.NewOptionalIntervalVar(start[t.name], d, end[t.name], x, f"i_{t.name}_{a}")
            assign[(t.name, a)] = x
            intervals.setdefault(a, []).append(iv)
            lits.append(x)
        m.AddExactlyOne(lits)
    for a in ais:
        m.AddNoOverlap(intervals.get(a, []))
    for t in tasks:
        for p in t.after:
            m.Add(start[t.name] >= end[p])
    mk = m.NewIntVar(0, H, "makespan")
    m.AddMaxEquality(mk, list(end.values()))
    late = []
    for t in tasks:
        if t.deadline is not None:
            l = m.NewIntVar(0, H, f"late_{t.name}")
            m.Add(l >= end[t.name] - t.deadline)
            late.append(l)
    m.Minimize(mk * (H + 1) + sum(late))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = time_limit; sv.parameters.num_workers = 4
    st = sv.Solve(m)
    plan = []
    for t in tasks:
        who = next(a for a in t.durations if sv.Value(assign[(t.name, a)]))
        plan.append({"viec": t.name, "ai": who, "bat_dau": sv.Value(start[t.name]), "ket_thuc": sv.Value(end[t.name])})
    plan.sort(key=lambda r: (r["bat_dau"], r["ai"]))
    return {"status": sv.StatusName(st), "makespan": sv.Value(mk), "tong_tre": sum(sv.Value(l) for l in late), "lich": plan}


def greedy_baseline(tasks: List[Task]):
    """Theo thứ tự topo; mỗi việc giao cho AI cho thời điểm xong sớm nhất."""
    done, free, plan, by = {}, {}, [], {t.name: t for t in tasks}
    order, seen = [], set()
    def visit(n):
        if n in seen: return
        seen.add(n)
        for p in by[n].after: visit(p)
        order.append(n)
    for t in tasks: visit(t.name)
    for n in order:
        t = by[n]
        ready = max([done[p] for p in t.after], default=0)
        a, d = min(t.durations.items(), key=lambda kv: max(ready, free.get(kv[0], 0)) + kv[1])
        s = max(ready, free.get(a, 0)); done[n] = s + d; free[a] = s + d
        plan.append({"viec": n, "ai": a, "bat_dau": s, "ket_thuc": s + d})
    late = sum(max(0, done[t.name] - t.deadline) for t in tasks if t.deadline is not None)
    return {"makespan": max(done.values()), "tong_tre": late, "lich": plan}


def validate(tasks: List[Task], plan: List[dict]) -> List[str]:
    """Kiểm tra độc lập: đúng AI được phép, đúng thời lượng, phụ thuộc, không chồng việc."""
    by = {t.name: t for t in tasks}; row = {r["viec"]: r for r in plan}; err = []
    for r in plan:
        t = by[r["viec"]]
        if r["ai"] not in t.durations: err.append(f"{r['viec']}: {r['ai']} không được phép")
        elif r["ket_thuc"] - r["bat_dau"] != t.durations[r["ai"]]: err.append(f"{r['viec']}: sai thời lượng")
        for p in t.after:
            if r["bat_dau"] < row[p]["ket_thuc"]: err.append(f"{r['viec']} bắt đầu trước khi {p} xong")
    for a in {r["ai"] for r in plan}:
        rs = sorted((r for r in plan if r["ai"] == a), key=lambda r: r["bat_dau"])
        for x, y in zip(rs, rs[1:]):
            if y["bat_dau"] < x["ket_thuc"]: err.append(f"{a} chồng việc {x['viec']}/{y['viec']}")
    return err
