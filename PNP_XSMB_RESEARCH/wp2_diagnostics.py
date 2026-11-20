"""Chẩn đoán THĂM DÒ sau WP2 (không phải kiểm định xác nhận). Tìm nguồn gốc của D03, D04, D11 (p<0,05 trước hiệu chỉnh)."""
import sys, lzma, collections, numpy as np
from astra_math import wp2_distinguishers as w, xsmb_audit as xa
dates, raw = w.load_raw(sys.argv[1]); T = w.tails(raw); P = w.presence(T); n = len(T)
yr = np.array([d.year for d in dates])
# --- D04: phân phối u theo thời kỳ
dist = np.array([float(p) for p in xa.distinct_tails_distribution()]); Eu = (np.arange(28) * dist).sum()
Vu = ((np.arange(28) - Eu) ** 2 * dist).sum()
u = P.sum(1)
print(f'D04: E[u] ly thuyet {Eu:.4f}, thuc {u.mean():.4f}, z = {(u.mean()-Eu)/np.sqrt(Vu/n):.2f}')
for a, b in ((2005, 2010), (2011, 2015), (2016, 2020), (2021, 2026)):
    m = (yr >= a) & (yr <= b); print(f'   {a}-{b}: {m.sum()} ky, TB u = {u[m].mean():.3f}, z = {(u[m].mean()-Eu)/np.sqrt(Vu/m.sum()):.2f}')
obs = collections.Counter(u.tolist())
print('   u : quan sat / ky vong :', [(k, obs.get(k, 0), round(dist[k]*n, 1)) for k in range(18, 28)])
# --- D03: hàng chữ số nào
for place in range(5):
    cnt = np.zeros(10)
    for row in raw:
        for v in row:
            if len(v) > place: cnt[int(v[-1-place])] += 1
    e = cnt.sum() / 10; st = ((cnt - e) ** 2 / e).sum()
    print(f'D03 hang {place}: chi2 = {st:.1f}, p = {xa.chi2_sf(st, 9):.4f}, chu so lech nhat = {int(np.argmax(abs(cnt-e)))} ({(cnt[np.argmax(abs(cnt-e))]-e)/np.sqrt(e*0.9):+.2f} SE)')
# --- D11: trùng lặp nguyên kỳ / nguyên giải; nén theo thời kỳ
rows = [tuple(r) for r in raw]
print('D11: ky trung toan bo 27 giai:', n - len(set(rows)))
same_prize = sum(1 for t in range(1, n) for j in range(27) if raw[t][j] == raw[t-1][j] and len(raw[t][j]) >= 4)
exp_same = (n - 1) * (10 * 1e-5 + 10 * 1e-4)
print(f'D11: giai 4-5 chu so trung y het hom qua cung vi tri: {same_prize} (ky vong ~{exp_same:.1f})')
rng = np.random.default_rng(1)
for a, b in ((2005, 2015), (2016, 2026)):
    m = (yr >= a) & (yr <= b); X = T[m]
    obs_c = len(lzma.compress(X.astype(np.uint8).tobytes(), preset=6))
    null = [len(lzma.compress(X[rng.permutation(len(X))].astype(np.uint8).tobytes(), preset=6)) for _ in range(99)]
    print(f'D11 {a}-{b}: nen that {obs_c}, hoan vi TB {np.mean(null):.0f}, p mot phia = {(1+sum(v <= obs_c for v in null))/100:.2f}')
