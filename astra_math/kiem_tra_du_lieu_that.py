"""Kiểm tra dữ liệu XSMB thật (ASTRA-LO-MATH-002).

Cách dùng: python3 -m astra_math.kiem_tra_du_lieu_that <THU_MUC>
<THU_MUC>/data/source.csv: tải từ https://raw.githubusercontent.com/khiemdoan/vietnam-lottery-xsmb-analysis/refs/heads/main/data/xsmb.csv
<THU_MUC>/dl/doichieu/xsmb_lab/sources/: giải nén Doi_chieu_XSMB_11_moc.zip (Drive 07_TAI_LIEU).
"""
import csv, re, sys, json, math, datetime as dt
sys.path.insert(0, '/home/user/astra-web-ailk')
from astra_math import xsmb_audit as xa
S = sys.argv[1]
rows = list(csv.DictReader(open(f'{S}/data/source.csv')))
cols = list(rows[0])[1:]; widths = [5]*10+[4]*10+[3]*3+[2]*4
bad = [r['date'] for r in rows if any(not re.fullmatch(r'\d+', r[c]) or int(r[c]) >= 10**w for c, w in zip(cols, widths))]
print('so ky', len(rows), rows[0]['date'], '->', rows[-1]['date'], '| dong loi dinh dang:', len(bad), bad[:5])
dates = [r['date'] for r in rows]
print('trung ngay:', len(dates)-len(set(dates)), '| sap xep:', dates == sorted(dates))
lk = {r['date']: r for r in rows}
# doi chieu 11 trang minhngoc
ok = 0
for date in ['2016-10-11']+[f'{y}-10-10' for y in range(2017, 2027)]:
    s = open(f'{S}/dl/doichieu/xsmb_lab/sources/minhngoc_{date}.html', encoding='utf-8', errors='replace').read()
    v = []
    for k in ['giaidb','giai1','giai2','giai3','giai4','giai5','giai6','giai7']:
        m = re.search(r'<td class="'+k+r'">(.*?)</td>', s, re.S)
        v += re.findall(r'<div[^>]*>(\d+)</div>', m.group(1)) if m else []
    exp = [lk[date][c].zfill(w) for c, w in zip(cols, widths)]
    y, mo, d = date.split('-'); t = f'{d}/{mo}/{y}' in s[:3000]
    good = t and v == exp; ok += good
    if not good: print('  LECH', date, len(v))
print('doi chieu minhngoc:', ok, '/ 11')
# ngay vang
def gaps(a, b):
    s, e = dt.date.fromisoformat(a), dt.date.fromisoformat(b); have = set(dates)
    return [(s+dt.timedelta(i)).isoformat() for i in range((e-s).days+1) if (s+dt.timedelta(i)).isoformat() not in have]
g = gaps('2016-10-11', rows[-1]['date']); print('ngay vang tu 2016-10-11:', len(g), '| 2020-04:', [x for x in g if x.startswith('2020-04')][:1], '..', [x for x in g if x.startswith('2020-04')][-1:], len([x for x in g if x.startswith('2020-04')]))
# CSV theo dinh dang xsmb_audit
for name, a in [('10nam', '2016-10-11'), ('toanbo', '0000')]:
    with open(f'{S}/data/ket_qua_{name}.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['ngay']+cols)
        for r in rows:
            if r['date'] >= a: w.writerow([r['date']]+[r[c].zfill(wd) for c, wd in zip(cols, widths)])
    draws = xa.load_draws(f'{S}/data/ket_qua_{name}.csv')
    ft = xa.fairness_test(draws)
    print(f'\n[{name}] {len(draws)} ky, chi2={ft["chi2"]}, p={ft["p_value"]:.4g}, top={ft["so_ve_nhieu_nhat"]}')
    # do cong bang theo tung vi tri giai (27 vi tri, moi vi tri chi2 df=99)
    pv = []
    for j in range(27):
        cnt = [0]*100
        for d in draws: cnt[d.numbers[j]] += 1
        n = len(draws); e = n/100; pv.append(xa.chi2_sf(sum((c-e)**2/e for c in cnt), 99))
    print('  27 vi tri: min p=%.4g; p<0.05: %d; Holm bac bo: %d' % (min(pv), sum(p < .05 for p in pv), sum(xa.holm(pv))))
    # do doc lap tre 1: so co mat ky t-1 -> co mat ky t (gop 100 so)
    a = b = c = dd = 0
    for t in range(1, len(draws)):
        prev = set(draws[t-1].numbers); cur = set(draws[t].numbers)
        for x in range(100):
            p_, c_ = x in prev, x in cur
            if p_ and c_: a += 1
            elif p_: b += 1
            elif c_: c += 1
            else: dd += 1
    p1, p0 = a/(a+b), c/(c+dd); se = math.sqrt(p1*(1-p1)/(a+b)+p0*(1-p0)/(c+dd))
    z = (p1-p0)/se; pz = math.erfc(abs(z)/math.sqrt(2))
    print(f'  tre 1: P(ve|hom qua ve)={p1:.5f}  P(ve|hom qua khong)={p0:.5f}  ly thuyet={float(xa.p_lo()):.5f}  z={z:.2f} p={pz:.3g}')
    # cau mau: lap lai de hom qua
    res = xa.evaluate_strategy(draws, lambda h: [h[-1].de], warmup=1)
    print(f'  cau "lap de hom qua": trung {res.hit_days}/{res.days} ngay, ky vong {res.expected_hit_days:.1f}, p={res.p_value_exact:.3g}')
