"""Kiểm định quy luật 'tổng đề < 10 → trong 7 kỳ sau đề có chữ số đó ở đầu hoặc đít' (thăm dò, 20/11/2026).
Biến thể A (chính): c = a + b của 2 số cuối ĐB, chỉ khi c < 10.
Biến thể B: c = (a + b) mod 10 (bóng tổng), mọi ngày.
Biến thể C: c = tổng 5 chữ số ĐB mod 10.
Mốc: P(chữ số c xuất hiện ở đầu/đít đề ít nhất 1 lần trong 7 kỳ) = 1 - 0,81^7 (đề ngẫu nhiên).
p-value: hoán vị thứ tự ngày (giữ nguyên chồng lấp cửa sổ), B = 9.999."""
import csv, sys, numpy as np
rows = list(csv.reader(open(sys.argv[1])))[1:]
de5 = [r[1].zfill(5) for r in rows]
a = np.array([int(s[3]) for s in de5]); b = np.array([int(s[4]) for s in de5]); full = np.array([sum(map(int, s)) for s in de5])
K = 7
def rate(a, b, full, variant):
    n = len(a); trig = hit = 0
    for t in range(n - K):
        if variant == 'A':
            c = a[t] + b[t]
            if c >= 10: continue
        elif variant == 'B': c = (a[t] + b[t]) % 10
        else: c = full[t] % 10
        w = slice(t + 1, t + 1 + K)
        trig += 1; hit += bool(((a[w] == c) | (b[w] == c)).any())
    return trig, hit
base = 1 - 0.81 ** K
rng = np.random.default_rng(20261120)
for v in 'ABC':
    trig, hit = rate(a, b, full, v)
    obs = hit / trig
    null = []
    for _ in range(2000 if v != 'A' else 9999):
        p = rng.permutation(len(a)); r = rate(a[p], b[p], full[p], v); null.append(r[1] / r[0])
    null = np.array(null)
    pv = (1 + (np.abs(null - null.mean()) >= abs(obs - null.mean())).sum()) / (len(null) + 1)
    print(f'Bien the {v}: {trig} lan kich hoat, dung {hit} = {obs:.4%} | moc ngau nhien {base:.4%} (hoan vi TB {null.mean():.4%}) | chenh {100*(obs-null.mean()):+.2f} diem % | p hai phia = {pv:.4f}')
