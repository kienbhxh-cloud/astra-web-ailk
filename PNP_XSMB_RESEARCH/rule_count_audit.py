# Chạy trong thư mục chứa astra_math của nhánh claude/astra-math-research-wdvww8 (commit 8440b65): python3 rule_count_audit.py
"""Nghiệm thu độc lập rule_count.py (PNP-QD-002) — Claude Code."""
import itertools, random, sys
sys.path.insert(0, '.')
from astra_math.pnp import rule_count as rc

def all_solutions(n, clauses):
    for bits in itertools.product((False, True), repeat=n):
        if all(any(bits[v] == pol for v, pol in cl) for cl in clauses):
            yield bits

def bijection(groups, s, extra=()):
    n, clauses, F = rc.build_cnf(groups, s, extra)
    sols = list(all_solutions(n, clauses))
    xs = [b[:F] for b in sols]
    assert len(set(xs)) == len(xs), 'hai nghiem cung x -> khong song anh'
    # moi x hop le (theo vet can) phai co dung 1 nghiem
    want = rc.count_rules_brute(groups, s, extra) + 1   # + tap rong
    assert len(sols) == want, (len(sols), want)
    return len(sols)

# 1) song anh tren toan bo phep gan (n nho)
cases = [([1], 1), ([2], 1), ([1, 1], 2), ([1, 1, 1], 3), ([2, 1], 2), ([3], 1), ([1, 2, 1], 2), ([2, 2], 1), ([1,1,1,1], 2)]
for g, s in cases:
    bijection(g, s)
bijection([1, 1, 1], 3, [(0, 2)]); bijection([2, 1, 1], 2, [(0, 3), (1, 2)])
print('[1] song anh vet can tren moi phep gan:', len(cases) + 2, 'ca DAT')

# 2) bien: s = F, moi nhom 1 phan tu, F = 1
r = random.Random(0)
for F in range(1, 9):
    g = [1] * F
    for s in range(1, F + 1):
        t, _, _ = rc.count_rules_tensor(g, s)
        assert t == rc.count_rules_brute(g, s) == sum(__import__('math').comb(F, k) for k in range(1, s + 1))
print('[2] bien nhom 1 phan tu, s = 1..F (F <= 8): DAT')

# 3) ngau nhien co rang buoc cheo, gom s = F
bad = 0
for it in range(150):
    g = [r.randint(1, 3) for _ in range(r.randint(1, 6))]; F = sum(g)
    if F > 10: g = g[:3]; F = sum(g)
    s = r.randint(1, F)
    extra = [tuple(r.sample(range(F), 2)) for _ in range(r.randint(0, 4))] if F >= 2 else []
    t, _, _ = rc.count_rules_tensor(g, s, extra_exclusions=extra)
    bad += t != rc.count_rules_brute(g, s, extra)
wide = []
for F in (12, 14, 16, 18, 20):
    try: rc.count_rules_tensor([1] * F, F)
    except ValueError as e: wide.append((F, str(e)))
print('[3b] s = F, nhom 1 phan tu: vuot do rong o', wide)
print('[3] 150 ngu phap ngau nhien (co rang buoc cheo, gom s=F): sai =', bad)

# 4) dau vao xau
for desc, fn in [('s = 0', lambda: rc.build_cnf([2, 2], 0)), ('s > F', lambda: rc.build_cnf([2], 3))]:
    try: fn(); print('[4]', desc, ': KHONG bao loi')
    except ValueError: print('[4]', desc, ': bao loi dung')
# rang buoc cheo tro ra ngoai pham vi dac trung -> rang buoc nham bien dem
n, cl, F = rc.build_cnf([1, 1, 1], 2, [(0, 5)])
print('[4] extra_exclusions chi so >= F (0,5) duoc chap nhan:', True, '-> rang buoc ca bien dem; dem tensor =',
      rc.count_rules_tensor([1, 1, 1], 2, extra_exclusions=[(0, 5)])[0], 'vs vet can =', rc.count_rules_brute([1, 1, 1], 2, [(0, 5)]))
print('[4] tu loai tru (2,2):', rc.count_rules_tensor([1, 1, 1], 2, extra_exclusions=[(2, 2)])[0], 'vs vet can', rc.count_rules_brute([1, 1, 1], 2, [(2, 2)]))
# 5) tai lap bang KTST
G = [2] * 10 + [5] * 4
print('[5] F1-v0 khong rang buoc cheo, s=1..5:', [rc.count_rules_tensor(G, s)[0] == rc.count_rules_closed_form(G, s) for s in range(1, 6)])
