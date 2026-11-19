"""B-ETH-1: đếm chính xác số luật |G_s| của ngữ pháp F1 bằng co mạng tensor (wmc.py).

Ngữ pháp (đặc tả KTST, PNP-QD-002):
- Có F đặc trưng Boolean chia thành các NHÓM loại trừ (vd "về ở trễ 1" / "không về ở trễ 1";
  các ngưỡng gan >=2, >=3, ... của cùng một đại lượng). Mỗi nhóm chọn tối đa 1 đặc trưng.
- Một luật = tập con S các đặc trưng (hội AND), 1 <= |S| <= s.
- |G_s| = số luật hợp lệ = số phép thử ngầm khi bộ giải duyệt ngữ pháp này.

Mã hóa CNF:
- biến x_i (đặc trưng i có trong luật);
- loại trừ trong nhóm: (¬x_a ∨ ¬x_b) với mọi cặp trong cùng nhóm;
- |S| <= s: bộ đếm tuần tự (Sinz 2005) dạng TƯƠNG ĐƯƠNG (r_{i,j} <=> "có >= j đặc trưng trong x_1..x_i"),
  nên mỗi luật ứng với đúng một nghiệm — đếm nghiệm = đếm luật;
- |S| >= 1: mệnh đề (x_1 ∨ ... ∨ x_F) — thay bằng trừ đi 1 (tập rỗng) để giữ độ rộng nhỏ.

Đối chiếu: công thức đóng (hệ số đa thức ∏(1 + g_k t)) và vét cạn khi F nhỏ.
Đây là công cụ ĐO số phép thử, không phải công cụ dự báo.
"""
from __future__ import annotations

import itertools
import math
import random
import time
from typing import Dict, List, Sequence, Tuple

from astra_math import wmc

Clause = List[Tuple[int, bool]]


def build_cnf(group_sizes: Sequence[int], s: int,
              extra_exclusions: Sequence[Tuple[int, int]] = ()) -> Tuple[int, List[Clause], int]:
    """Trả về (số biến, danh sách mệnh đề, F). Biến 0..F-1 là đặc trưng; phần sau là bộ đếm."""
    F = sum(group_sizes)
    if not 1 <= s <= F:
        raise ValueError("cần 1 <= s <= F")
    clauses: List[Clause] = []
    # loại trừ trong nhóm
    start = 0
    for g in group_sizes:
        for a, b in itertools.combinations(range(start, start + g), 2):
            clauses.append([(a, False), (b, False)])
        start += g
    # ràng buộc mâu thuẫn GIỮA các nhóm (vd "về ở trễ 1" mâu thuẫn "gan >= 2"): không có công thức đóng
    for a, b in extra_exclusions:
        clauses.append([(a, False), (b, False)])
    # bộ đếm tuần tự tương đương: r[i][j], i = 0..F-1, j = 1..s
    nxt = F
    r: Dict[Tuple[int, int], int] = {}
    for i in range(F):
        for j in range(1, s + 1):
            r[i, j] = nxt
            nxt += 1
    for i in range(F):
        x = i
        for j in range(1, s + 1):
            v = r[i, j]
            prev_j = r.get((i - 1, j))          # >= j trong x_0..x_{i-1}
            prev_j1 = r.get((i - 1, j - 1)) if j > 1 else None  # >= j-1 trước đó (j=1: luôn đúng)
            # v <=> prev_j ∨ (x ∧ prev_{j-1})
            if i == 0:
                if j == 1:
                    clauses += [[(v, False), (x, True)], [(x, False), (v, True)]]
                else:
                    clauses.append([(v, False)])
                continue
            # (prev_j -> v)
            clauses.append([(prev_j, False), (v, True)])
            if j == 1:
                clauses.append([(x, False), (v, True)])                       # x -> v
                clauses.append([(v, False), (prev_j, True), (x, True)])        # v -> prev ∨ x
            else:
                clauses.append([(x, False), (prev_j1, False), (v, True)])      # x ∧ prev_{j-1} -> v
                clauses.append([(v, False), (prev_j, True), (x, True)])        # v -> prev_j ∨ x
                clauses.append([(v, False), (prev_j, True), (prev_j1, True)])  # v -> prev_j ∨ prev_{j-1}
        # cấm vượt s: x_i ∧ (>= s trước đó) là sai
        if i > 0:
            clauses.append([(x, False), (r[i - 1, s], False)])
    return nxt, clauses, F


def count_rules_tensor(group_sizes: Sequence[int], s: int, max_width: int = 22,
                       extra_exclusions: Sequence[Tuple[int, int]] = ()) -> Tuple[int, int, float]:
    """|G_s| bằng co mạng tensor. Trả về (số luật, độ rộng khử biến, giây)."""
    t = time.perf_counter()
    n, clauses, _ = build_cnf(group_sizes, s, extra_exclusions)
    val, width = wmc.count_cnf(n, clauses, exact=True, max_width=max_width)
    return int(val) - 1, width, time.perf_counter() - t   # trừ tập rỗng


def count_rules_closed_form(group_sizes: Sequence[int], s: int) -> int:
    """Hệ số t^1..t^s của ∏(1 + g_k t)."""
    poly = [1]
    for g in group_sizes:
        new = [0] * (len(poly) + 1)
        for d, c in enumerate(poly):
            new[d] += c
            new[d + 1] += c * g
        poly = new
    return sum(poly[1:s + 1])


def count_rules_brute(group_sizes: Sequence[int], s: int,
                      extra_exclusions: Sequence[Tuple[int, int]] = ()) -> int:
    """Vét cạn trên mọi tập con đặc trưng (chỉ dùng cho F nhỏ)."""
    groups = []
    start = 0
    for g in group_sizes:
        groups.append(range(start, start + g))
        start += g
    F = start
    tot = 0
    for k in range(1, s + 1):
        for S in itertools.combinations(range(F), k):
            if all(sum(1 for x in S if x in grp) <= 1 for grp in groups) and \
                    not any(a in S and b in S for a, b in extra_exclusions):
                tot += 1
    return tot


def count_rules_monte_carlo(group_sizes: Sequence[int], s: int, seconds: float, seed: int = 0) -> Tuple[float, int]:
    """Ước lượng Monte Carlo cùng ngân sách thời gian: lấy tập con đều trong các tập |S|<=s."""
    rng = random.Random(seed)
    F = sum(group_sizes)
    gid = [k for k, g in enumerate(group_sizes) for _ in range(g)]
    total_space = sum(math.comb(F, k) for k in range(1, s + 1))
    weights = [math.comb(F, k) for k in range(1, s + 1)]
    ok = n = 0
    t_end = time.perf_counter() + seconds
    while time.perf_counter() < t_end:
        k = rng.choices(range(1, s + 1), weights)[0]
        S = rng.sample(range(F), k)
        ok += len({gid[x] for x in S}) == k
        n += 1
    return total_space * ok / max(n, 1), n


def benchmark(group_sizes: Sequence[int], s_values: Sequence[int]) -> List[dict]:
    rows = []
    for s in s_values:
        cnt, width, sec = count_rules_tensor(group_sizes, s)
        exact = count_rules_closed_form(group_sizes, s)
        mc, n_mc = count_rules_monte_carlo(group_sizes, s, max(sec, 0.05), seed=s)
        rows.append(dict(s=s, tensor=cnt, closed_form=exact, khop=cnt == exact, do_rong=width,
                         giay=round(sec, 3), monte_carlo=round(mc), mc_mau=n_mc,
                         mc_sai_so_pct=round(100 * abs(mc - exact) / exact, 2)))
    return rows


if __name__ == "__main__":
    import json, sys
    # Ngữ pháp mẫu F1-v0: 10 cặp "về/không về ở trễ L" (L=1..10) + 4 đại lượng gan, mỗi đại lượng 5 ngưỡng
    G = [2] * 10 + [5] * 4
    print("Ngữ pháp mẫu: F =", sum(G), "đặc trưng, nhóm =", G)
    print(json.dumps(benchmark(G, range(1, int(sys.argv[1]) + 1 if len(sys.argv) > 1 else 7)),
                     ensure_ascii=False, indent=1))
