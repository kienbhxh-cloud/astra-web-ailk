"""PNP-READ-007 / PRODUCT-002 — Benchmark bài toán phủ tối đa (max coverage) chọn 5 số, CHỈ DỮ LIỆU GIẢ LẬP.

So sánh trên cùng tập huấn luyện → chấm trên tập kiểm tra độc lập:
  A. top5_freq   : 5 số nhiều lượt nhất (= nghiệm MILP 'tối đa tổng lượt' của PRODUCT-002)
  B. milp_sum    : CP-SAT giải đúng bài 'tối đa tổng lượt' (để chứng minh A ≡ B)
  C. greedy_cov  : tham lam cho 'tối đa số kỳ có ≥1 số về' (xấp xỉ 1−1/e)
  D. cpsat_cov   : CP-SAT tối ưu CHÍNH XÁC 'tối đa số kỳ có ≥1 số về' (NP-khó, có chứng nhận OPTIMAL)
Mốc: random-5 chính xác theo u từng kỳ kiểm tra. Không dùng dữ liệu XSMB thật (protocol chưa khóa).
Chạy: PYTHONPATH=. python3 PNP_XSMB_RESEARCH/coverage_benchmark.py
"""
import json, math, random, time, sys
from ortools.sat.python import cp_model
from astra_math import xsmb_audit as xa

K = 5

def gen(n, seed, kind):
    r = random.Random(seed); out = []
    for t in range(n):
        d = [r.randrange(100) for _ in range(27)]
        if kind == 'planted07' and r.random() < 0.6:
            d[0] = 7                                   # giống PRODUCT-002
        if kind == 'complement':                       # tín hiệu cần 'phủ': nhóm A ngày chẵn, nhóm B ngày lẻ
            grp = (11, 22, 33) if t % 2 == 0 else (44, 55, 66)
            if r.random() < 0.5:
                d[1] = r.choice(grp)
        out.append(d)
    return out

def top5_freq(train):
    c = [0] * 100
    for d in train:
        for x in d: c[x] += 1
    return sorted(range(100), key=lambda i: (-c[i], i))[:K]

def milp_sum(train):
    c = [0] * 100
    for d in train:
        for x in d: c[x] += 1
    m = cp_model.CpModel(); x = [m.NewBoolVar(f'x{i}') for i in range(100)]
    m.Add(sum(x) == K); m.Maximize(sum(c[i] * x[i] for i in range(100)))
    s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.random_seed = 0
    st = s.Solve(m)
    return sorted(i for i in range(100) if s.Value(x[i])), s.StatusName(st)

def greedy_cov(train):
    sets = [set(d) for d in train]; chosen = []; covered = [False] * len(sets)
    for _ in range(K):
        best = max((i for i in range(100) if i not in chosen),
                   key=lambda i: (sum(1 for j, s in enumerate(sets) if not covered[j] and i in s), -i))
        chosen.append(best)
        for j, s in enumerate(sets):
            if best in s: covered[j] = True
    return sorted(chosen)

def cpsat_cov(train, time_limit=60):
    sets = [set(d) for d in train]
    m = cp_model.CpModel(); x = [m.NewBoolVar(f'x{i}') for i in range(100)]
    y = [m.NewBoolVar(f'y{j}') for j in range(len(sets))]
    m.Add(sum(x) == K)
    for j, s in enumerate(sets):
        m.Add(y[j] <= sum(x[i] for i in s))
    m.Maximize(sum(y))
    s = cp_model.CpSolver(); s.parameters.num_workers = 1; s.parameters.random_seed = 0
    s.parameters.max_time_in_seconds = time_limit
    st = s.Solve(m)
    return sorted(i for i in range(100) if s.Value(x[i])), s.StatusName(st), s.ObjectiveValue(), s.BestObjectiveBound()

def score(pick, test):
    hits = sum(any(p in d for p in pick) for d in test)
    base = sum(float(xa.p_set_hit_given_u(K, len(set(d)))) for d in test)
    nhay = sum(sum(d.count(p) for p in pick) for d in test)
    return hits, base, nhay

def main():
    res = []
    for kind in ('iid', 'planted07', 'complement'):
        for rep in range(3):
            tr = gen(1000, 20261120 + rep, kind); te = gen(1000, 30261120 + rep, kind)
            row = {'kind': kind, 'rep': rep}
            t0 = time.perf_counter(); a = top5_freq(tr); ta = time.perf_counter() - t0
            t0 = time.perf_counter(); b, bst = milp_sum(tr); tb = time.perf_counter() - t0
            t0 = time.perf_counter(); g = greedy_cov(tr); tg = time.perf_counter() - t0
            t0 = time.perf_counter(); c, cst, obj, bnd = cpsat_cov(tr); tc = time.perf_counter() - t0
            row['milp_sum_equals_top5'] = (a == b); row['milp_status'] = bst
            for name, pick, tt in (('top5_freq', a, ta), ('greedy_cov', g, tg), ('cpsat_cov', c, tc)):
                h_tr = sum(any(p in d for p in pick) for d in tr)
                h, base, nh = score(pick, te)
                row[name] = {'pick': pick, 'train_cov': h_tr, 'test_hits': h, 'test_random5_expected': round(base, 1),
                             'test_nhay': nh, 'test_nhay_expected': 1.35 * len(te), 'seconds': round(tt, 3)}
            row['cpsat_status'] = cst; row['cpsat_obj'] = obj; row['cpsat_bound'] = bnd
            res.append(row)
            print(json.dumps(row, ensure_ascii=False))
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else 'coverage_benchmark_results.json', 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
