"""Bổ sung (LK: 'thường là đầu số'): c = a+b < 10 → trong 7 kỳ sau, đề có ĐẦU = c? So với ĐÍT = c.
Mốc ngẫu nhiên mỗi loại: 1 - 0,9^7. p: hoán vị thứ tự ngày, B = 9.999."""
import csv, sys, numpy as np
rows = list(csv.reader(open(sys.argv[1])))[1:]
a = np.array([int(r[1].zfill(5)[3]) for r in rows]); b = np.array([int(r[1].zfill(5)[4]) for r in rows]); K = 7
def stat(a, b):
    n = len(a); T = D = E = 0
    for t in range(n - K):
        c = a[t] + b[t]
        if c >= 10: continue
        w = slice(t + 1, t + 1 + K); T += 1
        D += bool((a[w] == c).any()); E += bool((b[w] == c).any())
    return T, D, E
T, D, E = stat(a, b)
rng = np.random.default_rng(20261121); nd, ne, ndiff = [], [], []
for _ in range(9999):
    p = rng.permutation(len(a)); t, d, e = stat(a[p], b[p]); nd.append(d / t); ne.append(e / t); ndiff.append((d - e) / t)
nd, ne, ndiff = map(np.array, (nd, ne, ndiff))
two = lambda obs, nul: (1 + (np.abs(nul - nul.mean()) >= abs(obs - nul.mean())).sum()) / (len(nul) + 1)
print(f'{T} lan kich hoat (tong 2 so cuoi DB < 10)')
print(f'DAU = c trong 7 ky: {D/T:.4%} | moc ngau nhien {1-0.9**K:.4%} (hoan vi TB {nd.mean():.4%}) | p = {two(D/T, nd):.4f}')
print(f'DIT = c trong 7 ky: {E/T:.4%} | moc ngau nhien {1-0.9**K:.4%} (hoan vi TB {ne.mean():.4%}) | p = {two(E/T, ne):.4f}')
print(f'DAU - DIT: {100*(D-E)/T:+.2f} diem % | p = {two((D-E)/T, ndiff):.4f}')
