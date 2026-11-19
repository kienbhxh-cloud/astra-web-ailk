"""Hiệu chỉnh WP2 trên DỮ LIỆU GIẢ LẬP (không dùng XSMB thật).
(1) Sai lầm loại I: N bộ H0 → tỷ lệ p<0,05 từng phép và tỷ lệ Holm bác bỏ ít nhất 1 (FWER).
(2) Lực: các tín hiệu cài sẵn.
Chạy: PYTHONPATH=. python3 PNP_XSMB_RESEARCH/wp2_calibration.py out.json"""
import json, sys, time
import numpy as np
from datetime import date
from astra_math import wp2_distinguishers as w

w.B_PERM, w.B_LZMA = 99, 39          # giảm B cho hiệu chỉnh (độ phân giải p = 0,01 / 0,025)
N_NULL, N_DAYS = 120, 1500

def planted(kind, n, seed):
    d, raw = w.simulate_raw(n, seed)
    r = np.random.default_rng(seed + 7)
    for t in range(1, n):
        if kind == 'lap_hom_qua' and r.random() < 0.15:      # 1 giải lặp đuôi của hôm qua với xác suất 0,15
            j = int(r.integers(0, 27)); raw[t][j] = raw[t][j][:-2] + raw[t - 1][int(r.integers(0, 27))][-2:]
        if kind == 'lech_chu_so' and r.random() < 0.10:       # lồng hàng đơn vị G7 lệch về '7'
            j = 23 + int(r.integers(0, 4)); raw[t][j] = raw[t][j][:-1] + '7'
        if kind == 'thu_trong_tuan' and d[t].weekday() == 0 and r.random() < 0.3:   # thứ Hai: ĐB đuôi 00
            raw[t][0] = raw[t][0][:-2] + '00'
    return d, raw

out = {'null': {}, 'power': {}}
t0 = time.time(); P = []
for s in range(N_NULL):
    P.append(w.run_all(*w.simulate_raw(N_DAYS, 10_000 + s), seed=s))
keys = list(P[0])
out['null'] = {k: round(float(np.mean([p[k] < 0.05 for p in P])), 3) for k in keys}
out['null']['FWER_holm'] = round(float(np.mean([bool(w.holm_report(p)['bac_bo_holm']) for p in P])), 3)
out['null']['_n'] = N_NULL; out['null']['_ngay'] = N_DAYS
print('H0 xong', round(time.time() - t0), 's', out['null'], flush=True)
for kind in ('lap_hom_qua', 'lech_chu_so', 'thu_trong_tuan'):
    R = [w.holm_report(w.run_all(*planted(kind, N_DAYS, 500 + s), seed=s)) for s in range(10)]
    out['power'][kind] = {'ty_le_holm_bac_bo_it_nhat_1': sum(bool(r['bac_bo_holm']) for r in R) / len(R),
                          'phep_bat_duoc': {k: sum(k in r['bac_bo_holm'] for r in R) for k in keys}}
    print(kind, out['power'][kind], flush=True)
json.dump(out, open(sys.argv[1], 'w'), ensure_ascii=False, indent=1)
