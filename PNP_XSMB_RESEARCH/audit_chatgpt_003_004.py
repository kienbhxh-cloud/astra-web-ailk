"""Kiểm toán độc lập REAL_BACKTEST_003 và MILP_REAL_004 (ChatGPT) — Claude Code, 20/11/2026.
Dùng: PYTHONPATH=. python3 PNP_XSMB_RESEARCH/audit_chatgpt_003_004.py clean.csv wf003.csv wf004.csv
Chỉ chấm lại các dự báo ĐÃ CÓ; không tạo dự báo hay tìm mô hình mới trên dữ liệu thật."""
import csv, sys, math, random
from collections import Counter
from astra_math import xsmb_audit as xa

clean, f3, f4 = sys.argv[1:4]
W = [5]*10 + [4]*10 + [3]*3 + [2]*4
rows = list(csv.reader(open(clean)))[1:]
draw = {r[0]: [int(v[-2:]) for v in r[1:]] for r in rows}
dates = [r[0] for r in rows]; idx = {d: i for i, d in enumerate(dates)}

def score(picks_by_date):
    hits = nh = 0; base = 0.0; ys = []; hs = []; p0s = []
    for d, pk in picks_by_date:
        dr = draw[d]; h = int(any(p in dr for p in pk)); y = sum(dr.count(p) for p in pk)
        u = len(set(dr)); p0 = float(xa.p_set_hit_given_u(5, u))
        hits += h; nh += y; base += p0; ys.append(y); hs.append(h); p0s.append(p0)
    n = len(ys)
    W_mean = xa.eprocess_mean(ys, 1.35) if hasattr(xa, 'eprocess_mean') else None
    return dict(n=n, hits=hits, base_u=round(base, 1), z_u=round((hits - base) / math.sqrt(sum(p*(1-p) for p in p0s)), 3),
                nhay_per_ky=round(nh / n, 5), z_nhay=round((nh - 1.35*n) / math.sqrt(n*27*.05*.95), 3),
                pnl_22500=round(nh*400000 - n*562500), _hs=hs)

def read(f):
    return list(csv.DictReader(open(f)))

def picks(col, R):
    return [(r['date'], [int(x) for x in r[col].split()]) for r in R]

out = {}
R3 = read(f3); R4 = read(f4)
for col, hc in (('top5_90', 'hit_top5_90'), ('top5_365', 'hit_top5_365')):
    s = score(picks(col, R3)); s['hit_cot_csv_khop'] = s['hits'] == sum(int(r[hc]) for r in R3); out['003_' + col] = s
for col, hc in (('maxcov', 'hit_maxcov'), ('top5', 'hit_top5'), ('random5', 'hit_random5')):
    s = score(picks(col, R4)); s['hit_cot_csv_khop'] = s['hits'] == sum(int(r[hc]) for r in R4); out['004_' + col] = s

# kiem tra khong nhin truoc: top5_90 phai la top-5 tan suat (so luot) trong 90 ky TRUOC ngay do (cho phep hoa)
viol = 0
for r in R3:
    i = idx[r['date']]; win = [x for d in dates[i-90:i] for x in draw[d]]; c = Counter(win)
    pk = [int(x) for x in r['top5_90'].split()]
    fifth = sorted(c.values(), reverse=True)[4]
    viol += any(c[p] < fifth for p in pk)
out['003_top5_90_kiem_tra_chi_dung_qua_khu'] = f'{len(R3) - viol}/{len(R3)} ky nhat quan (vi pham {viol})'

# MILP: chat luong nghiem kha thi so voi tham lam tren cung cua so 90 ky truoc block
blocks = sorted({r['block_start'] for r in R4}); worse = 0; gaps = []
for b in blocks:
    i = idx[b]; win = [set(draw[d]) for d in dates[i-90:i]]
    pk = [int(x) for x in next(r['maxcov'] for r in R4 if r['block_start'] == b).split()]
    cov = sum(any(p in s for p in pk) for s in win)
    ch = []
    for _ in range(5):
        best = max((x for x in range(100) if x not in ch), key=lambda x: (sum(1 for s in win if x in s and not any(c in s for c in ch)), -x)); ch.append(best)
    g = sum(any(p in s for p in ch) for s in win); worse += cov < g; gaps.append(cov - g)
out['004_milp_vs_greedy_90ky'] = f'{len(blocks)} block; MILP kem greedy {worse} block; chenh (MILP-greedy) = {gaps}'

# so cap MILP vs Top5 (McNemar chinh xac)
a = out['004_maxcov']['_hs']; b = out['004_top5']['_hs']
n10 = sum(x and not y for x, y in zip(a, b)); n01 = sum(y and not x for x, y in zip(a, b))
k = min(n10, n01); p = min(1.0, 2 * sum(math.comb(n10 + n01, j) for j in range(k + 1)) / 2 ** (n10 + n01))
out['004_mcnemar_maxcov_vs_top5'] = dict(chi_maxcov_trung=n10, chi_top5_trung=n01, p_hai_phia=round(p, 4))
# Holm tren 5 cau hinh co chon (chuan u, mot phia)
pv = {k: 0.5 * math.erfc(v['z_u'] / math.sqrt(2)) for k, v in out.items() if isinstance(v, dict) and 'z_u' in v}
rej = xa.holm(list(pv.values())); out['holm_mot_phia_5_cau_hinh'] = {k: (round(p, 4), r) for (k, p), r in zip(pv.items(), rej)}
for v in out.values():
    if isinstance(v, dict): v.pop('_hs', None)
import json; print(json.dumps(out, ensure_ascii=False, indent=1))
