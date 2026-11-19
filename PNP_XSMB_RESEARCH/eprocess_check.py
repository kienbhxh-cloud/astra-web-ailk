"""Nghiệm thu độc lập e-process của KTST (PNP-QD-001).
Chạy trong thư mục chứa astra_math của nhánh claude/astra-math-research-wdvww8 (commit 48987ad):
  python3 PNP_XSMB_RESEARCH/eprocess_check.py
"""
import sys, random, math, statistics
sys.path.insert(0, '.')
from astra_math import xsmb_audit as xa
L = xa.DEFAULT_LAMBDAS
def binom(r, n, p): return sum(r.random() < p for _ in range(n))
def first_cross(ys, thr):
    path = xa.eprocess_mean(ys, 1.35, L)
    for i, w in enumerate(path):
        if w >= thr: return i + 1
    return None
# 1) H0 that: xo so cong bang day du (27 giai), bo 5 so co dinh, 3.000 ky, 400 lan
r = random.Random(7); fa20 = fa60 = 0; ah20 = 0; reps = 400
for _ in range(reps):
    ys = []; hits = []; p0s = []
    for t in range(3000):
        draw = [r.randrange(100) for _ in range(27)]
        ys.append(sum(draw.count(x) for x in (0, 1, 2, 3, 4)))
        u = len(set(draw)); hits.append(int(any(x in draw for x in range(5)))); p0s.append(float(xa.p_set_any_given_u(u)))
    fa20 += first_cross(ys, 20) is not None; fa60 += first_cross(ys, 60) is not None
    ah20 += max(xa.eprocess_any_hit(hits, p0s)) >= 20
print(f'H0 (3.000 ky x {reps}): bao nham nhay W>=20: {fa20/reps:.3f} (gioi han 0,05); W>=60: {fa60/reps:.3f} (gioi han 0,0167); any-hit W>=20: {ah20/reps:.3f}')
# 2) power
for edge, reps in ((0.0417, 100), (0.10, 100), (0.20, 100)):
    rr = random.Random(int(edge * 1e4)); ts = []
    for _ in range(reps):
        ys = [binom(rr, 27, 0.05 * (1 + edge)) for _ in range(6000)]
        ts.append(first_cross(ys, 60))
    det = [t for t in ts if t]
    print(f'loi the +{edge*100:.2f}%: phat hien {len(det)}/{reps}, trung vi so ky {statistics.median(det) if det else None}')
