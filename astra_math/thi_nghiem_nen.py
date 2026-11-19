"""ASTRA-LO-PNP-001: thí nghiệm nén (xấp xỉ độ phức tạp Kolmogorov).
Cách dùng: python3 -m astra_math.thi_nghiem_nen ket_qua_10nam.csv
"""
# Thí nghiệm nén (xấp xỉ độ phức tạp Kolmogorov): dữ liệu thật có nén tốt hơn dữ liệu ngẫu nhiên công bằng không?
import sys, lzma, bz2, zlib, random
from astra_math import xsmb_audit as xa
d = xa.load_draws(sys.argv[1])
real = bytes(x for dr in d for x in dr.numbers)
def sizes(b): return {'lzma': len(lzma.compress(b, preset=9 | lzma.PRESET_EXTREME)), 'bz2': len(bz2.compress(b, 9)), 'zlib': len(zlib.compress(b, 9))}
R = sizes(real); sims = []
for s in range(200):
    r = random.Random(s); sims.append(sizes(bytes(r.randrange(100) for _ in range(len(real)))))
print('so byte', len(real), '| gioi han Shannon (log2 100 bit/so):', round(len(real) * 6.643856 / 8))
for k in R:
    v = sorted(x[k] for x in sims); p = (sum(x <= R[k] for x in v) + 1) / (len(v) + 1)
    print(f'{k}: that={R[k]}  ngau nhien: min={v[0]} trung vi={v[100]} max={v[-1]}  p(nen tot bang/hon)={p:.3f}')
