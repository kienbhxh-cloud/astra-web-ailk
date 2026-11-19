import itertools, random
from fractions import Fraction
import numpy as np
import pytest

from astra_math import wmc, tail_risk as tr, hose_order as ho, portfolio as pf, scheduler as sc


# ---------- wmc ----------
@pytest.mark.parametrize("seed", range(15))
def test_wmc_matches_brute_force(seed):
    r = random.Random(seed); n = r.randint(3, 12)
    cl = [[(v, r.random() < 0.5) for v in r.sample(range(n), r.randint(1, min(3, n)))] for _ in range(r.randint(1, 2 * n))]
    val, _ = wmc.count_cnf(n, cl)
    assert val == wmc.brute_force_count(n, cl)
    w = {v: Fraction(r.randint(1, 9), 10) for v in range(n)}
    pv, _ = wmc.count_cnf(n, cl, weights=w)
    assert pv == wmc.brute_force_count(n, cl, w)


def test_wmc_large_chain_exact_integer():
    n = 300  # chuỗi x_i OR x_{i+1}: số nghiệm = Fibonacci(n+2), vét cạn bất khả
    cl = [[(i, True), (i + 1, True)] for i in range(n - 1)]
    val, width = wmc.count_cnf(n, cl)
    a, b = 1, 2
    for _ in range(n - 1): a, b = b, a + b
    assert val == b and isinstance(val, int) and width <= 3


# ---------- tail risk ----------
def small_model():
    stocks = [tr.Stock(f"S{g}{j}", f"G{g}", 0.02, 0.5, loss_if_down=1 + j) for g in range(3) for j in range(4)]
    return tr.HierarchicalModel(0.1, {f"G{g}": 0.05 for g in range(3)}, {f"G{g}": 0.6 for g in range(3)}, stocks)


def brute_tail(model, use_loss):
    secs = model.sectors(); dist = {}
    for M in (0, 1):
        wM = model.p_market_shock if M else 1 - model.p_market_shock
        pS = model.p_sector_shock_market if M else model.p_sector_shock_normal
        for S in itertools.product((0, 1), repeat=len(secs)):
            wS = wM
            for g, s in zip(secs, S): wS *= pS[g] if s else 1 - pS[g]
            sm = dict(zip(secs, S))
            for X in itertools.product((0, 1), repeat=len(model.stocks)):
                w = wS; tot = 0
                for st, x in zip(model.stocks, X):
                    q = st.p_down_shock if sm[st.sector] else st.p_down_normal
                    w *= q if x else 1 - q
                    tot += (st.loss_if_down if use_loss else 1) * x
                dist[tot] = dist.get(tot, 0) + w
    return dist


def test_tail_matches_brute_force_and_known_value():
    m = small_model()
    d = tr.count_down_distribution(m); b = brute_tail(m, False)
    for k, v in b.items(): assert abs(d[k] - v) < 1e-12
    assert abs(tr.tail_prob(d, 8) - 0.0045362039772423556) < 1e-12   # giá trị vét cạn 2^16, phân số chính xác
    dl = tr.loss_distribution(m); bl = brute_tail(m, True)
    for k, v in bl.items(): assert abs(dl[k] - v) < 1e-12
    assert abs(dl.sum() - 1) < 1e-12


def test_var_es_consistent():
    d = tr.loss_distribution(small_model())
    var, es = tr.var_es(d, 0.99)
    cdf = np.cumsum(d)
    assert cdf[var] >= 0.99 - 1e-12 and (var == 0 or cdf[var - 1] < 0.99)
    assert es >= var


# ---------- hose order ----------
def test_order_functions_exhaustive():
    for P in range(1000, 200_001, 7):
        p = ho.round_down_tick(P)
        assert ho.is_valid_tick(p) and p <= P and P - p < ho.tick_size(P)
        for B in (0, 5_000_000, 123_456_789):
            q, s = ho.buy_order(B, P)
            assert s % 100 == 0 and s * q <= B and (s + 100) * q > B
        R = ho.round_down_tick(P)
        lo, hi = ho.floor_price(R), ho.ceiling_price(R)
        assert ho.is_valid_tick(lo) and ho.is_valid_tick(hi) and lo * 100 >= R * 93 and hi * 100 <= R * 107


def test_floor_bug_regression():
    assert ho.floor_price(7570) == 7050      # bản ngây thơ cho 7.040 < 93% * 7.570
    assert not ho.validate_order("BUY", 50050, 100, 50000).ok
    assert not ho.validate_order("BUY", 32500, 307, 32500).ok
    assert ho.validate_order("BUY", 32500, 300, 32500, cash_vnd=10_000_000).ok


def test_z3_proofs():
    pytest.importorskip("z3")
    from astra_math.proofs.hose_order_z3 import run
    assert all(v == "DA CHUNG MINH" for v in run().values())


# ---------- portfolio ----------
def assets_from_csv():
    import csv, os
    rows = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), "..", "data", "hose30_minh_hoa.csv"))))
    return [pf.Asset(r["ticker"], r["sector"], int(r["price"]), (float(r["alpha"]) - 0.6) * 0.2,
                     float(r["adv20"]) * 1e9, r["restricted"] == "1") for r in rows]


def test_portfolio_feasible_and_beats_or_ties_greedy():
    a = assets_from_csv()
    c = pf.Constraints(exclusive_pairs=[("TCB", "MBB"), ("HSG", "NKG"), ("SSI", "HCM"), ("VHM", "VIC"), ("MWG", "PNJ")])
    opt = pf.optimize(a, c, time_limit=20)
    g = pf.greedy(a, c)
    assert opt["status"] == "OPTIMAL" and not opt["errors"] and not g["errors"]
    assert opt["objective"] >= g["objective"] - 1


def test_portfolio_rebalance_fee():
    a = assets_from_csv()
    c0 = pf.Constraints()
    base = pf.optimize(a, c0, time_limit=20)
    c1 = pf.Constraints(current_shares=base["shares"], prop_fee=0.02)  # phí giao dịch cao -> giữ nguyên
    again = pf.optimize(a, c1, time_limit=20)
    assert again["shares"] == base["shares"]


# ---------- scheduler ----------
def test_scheduler_valid_and_not_worse_than_greedy():
    T = sc.Task
    tasks = [T("thu_thap", {"Grok": 2, "Gemini": 3}), T("chuan_hoa", {"Gemini": 2, "Codex": 3}),
             T("build_lean", {"Codex": 4}), T("pilot", {"Claude": 3, "Codex": 4}, after=["chuan_hoa"]),
             T("ra_Anthropic", {"ChatGPT": 2, "Gemini": 3}),  # không có Claude: xung đột lợi ích
             T("kien_truc", {"Claude": 3}, after=["pilot", "build_lean", "ra_Anthropic"]),
             T("phan_bien", {"ChatGPT": 2, "Grok": 2}, after=["kien_truc"]), T("trinh_LK", {"ChatGPT": 1}, after=["phan_bien"], deadline=12)]
    s = sc.solve(tasks); g = sc.greedy_baseline(tasks)
    assert not sc.validate(tasks, s["lich"]) and not sc.validate(tasks, g["lich"])
    assert s["makespan"] <= g["makespan"]
    assert all(r["ai"] != "Claude" for r in s["lich"] if r["viec"] == "ra_Anthropic")
