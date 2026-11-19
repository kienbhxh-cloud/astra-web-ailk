"""PNP-MASTER-005: luc thong ke F1/F3 va moc random-5 chinh xac.
Chay: PYTHONPATH=. python3 PNP_XSMB_RESEARCH/power_analysis.py ket_qua_10nam.csv
"""
import sys, math, random
from astra_math import xsmb_audit as xa
p0 = float(xa.p_set_hit(5)); a6 = 0.05 / 6
print(f'p0 bo5 = {p0:.6f}')
d = xa.load_draws(sys.argv[1])
print('random-5 chinh xac tren 3.629 ky that:', round(xa.random_k_baseline(d[-3629:], 5), 6))
dist = xa.distinct_tails_distribution(); print('E[u]=', round(float(sum(u*p for u,p in enumerate(dist))),4), ' P(u=23)=', round(float(dist[23]),4))
print('\n== F3: ty le ky trung >=1 cua bo 5 (alpha=0.05/6, power 80%) ==')
for n in (60, 180, 365, 1000):
    m = xa.min_detectable_rate(n, p0, a6)
    print(f'  n={n:5d}: phat hien duoc khi ty le that >= {m:.4f} (+{(m-p0)*100:.1f} diem %)')
for gain in (0.01, 0.02, 0.05):
    print(f'  muc tang +{gain*100:.0f} diem %: can {xa.days_needed(p0, p0+gain, a6)} ky')
# lo/lai: hit-rate khong quyet dinh tien; can so nhay. Hoa von: E[nhay] >= 1.4375 (575k/400k) hoac 22.500d: 562.5/400
for price in (22500, 23000):
    be = 5*5*price/(5*80000)
    print(f'  gia {price}: hoa von can {be:.4f} nhay/ky = ty le moi so {be/27:.5f} (ngau nhien 0.05, +{(be/27/0.05-1)*100:.2f}%)')
print('\n== F1: Brier 100 bien hien dien, mo hinh "biet" lech that delta ==')
pz = float(xa.p_lo())
def sim(delta, n=180, reps=400, seed=0):
    r = random.Random(seed); wins = 0; diffs = []
    for _ in range(reps):
        tot = 0.0
        for _ in range(n):
            # 100 so, nua co p cao, nua co p thap; mo hinh biet dung p, baseline dung p0
            dd = 0.0
            for i in range(100):
                pi = pz + (delta if i < 50 else -delta)
                y = 1.0 if r.random() < pi else 0.0
                dd += (y - pz) ** 2 - (y - pi) ** 2
            tot += dd / 100
        diffs.append(tot / n)
    mu = sum(diffs) / reps; sd = (sum((x - mu) ** 2 for x in diffs) / reps) ** .5
    return mu, sd
for delta in (0.005, 0.01, 0.022):
    mu, sd = sim(delta)
    z = 2.394 + 0.842
    print(f'  delta={delta}: cai thien Brier TB={mu:.6f} (ly thuyet delta^2={delta**2:.6f}), SD tren 180 ky={sd:.6f}, z={mu/sd:.2f}; can ~{math.ceil(180*(z*sd/mu)**2)} ky de dat power 80%')
