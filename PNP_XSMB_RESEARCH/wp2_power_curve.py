import json, numpy as np
from astra_math import wp2_distinguishers as w
w.B_PERM, w.B_LZMA = 999, 199
def planted(kind, q, n, seed):
    d, raw = w.simulate_raw(n, seed); r = np.random.default_rng(seed + 7)
    for t in range(1, n):
        if kind == 'lap' and r.random() < q:
            j = int(r.integers(0, 27)); raw[t][j] = raw[t][j][:-2] + raw[t-1][int(r.integers(0, 27))][-2:]
        if kind == 'lech' and r.random() < q:
            j = 23 + int(r.integers(0, 4)); raw[t][j] = raw[t][j][:-1] + '7'
    return d, raw
res = {}
for kind, qs in (('lap', (0.15, 0.3, 0.6)),):
    for q in qs:
        R = [w.holm_report(w.run_all(*planted(kind, q, 1500, 900 + s), seed=s)) for s in range(6)]
        hit = {}
        for r in R:
            for k in r['bac_bo_holm']: hit[k] = hit.get(k, 0) + 1
        res[f'{kind}_{q}'] = {'holm_bat_duoc': sum(bool(r['bac_bo_holm']) for r in R) / 6, 'phep': hit}
        print(kind, q, res[f'{kind}_{q}'], flush=True)
json.dump(res, open('PNP_XSMB_RESEARCH/wp2_power_curve_B999.json', 'w'), indent=1)
