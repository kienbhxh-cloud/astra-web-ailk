import itertools, math, random
from datetime import date, datetime, timezone
from fractions import Fraction
import pytest
from astra_math import xsmb_audit as xa


def test_exact_probabilities_known_values():
    assert abs(float(xa.p_lo()) - 0.23765728565289646) < 1e-15
    assert abs(float(xa.p_xien(2)) - 0.05488209778544517) < 1e-15
    assert xa.p_xien(1) == xa.p_lo() and xa.p_de() == Fraction(1, 100)
    assert sum(xa.nhay_distribution()) == 1


def test_xien_matches_brute_force_small():
    # kiểm bao hàm–loại trừ bằng vét cạn trên mô hình thu nhỏ: 4 lần quay, 6 số
    n_draw, n_num, k = 4, 6, 2
    hit = sum(all(x in seq for x in range(k)) for seq in itertools.product(range(n_num), repeat=n_draw))
    formula = sum(((-1) ** j) * math.comb(k, j) * Fraction(n_num - j, n_num) ** n_draw for j in range(k + 1))
    assert Fraction(hit, n_num ** n_draw) == formula


def test_expected_value_and_break_even():
    be = xa.break_even_payout(1.0)
    assert abs(xa.expected_value(1.0, be) - 0) < 1e-12
    assert xa.expected_value(1.0, be * 0.9) < 0


def test_chi2_sf_against_known():
    # giá trị tham chiếu: chi2.sf(99, 99) ≈ 0.4813, chi2.sf(150, 99) ≈ 7.7e-4 (scipy)
    assert abs(xa.chi2_sf(99, 99) - 0.4813) < 2e-3
    assert 5e-4 < xa.chi2_sf(150, 99) < 1.1e-3
    assert abs(xa.chi2_sf(3.841458820694124, 1) - 0.05) < 1e-9


def test_fair_data_not_flagged_and_biased_flagged():
    fair = xa.simulate_draws(1000, seed=1)
    assert xa.fairness_test(fair)["p_value"] > 0.001
    biased = [xa.Draw(d.day, [7 if i < 3 else x for i, x in enumerate(d.numbers)]) for d in fair]
    assert xa.fairness_test(biased)["p_value"] < 1e-6


def test_walk_forward_no_lookahead():
    draws = xa.simulate_draws(60, seed=3)
    seen = []
    def strat(hist):
        seen.append(len(hist)); return [hist[-1].de if hist else 0]
    xa.evaluate_strategy(draws, strat, warmup=10)
    assert seen == list(range(10, 60))


def test_cheating_strategy_detected_and_fair_one_not():
    draws = xa.simulate_draws(200, seed=4)
    peek = {d.day: d.numbers[0] for d in draws}
    cheat = lambda hist: [peek[draws[len(hist)].day]]  # gian lận: nhìn trước kết quả
    assert xa.evaluate_strategy(draws, cheat).p_value_exact < 1e-30
    r = random.Random(0)
    fair = xa.evaluate_strategy(draws, lambda h: r.sample(range(100), 3), permutations=200, seed=1)
    assert fair.p_value_exact > 0.001 and fair.p_value_permutation > 0.001


def test_multiple_testing():
    p = [0.001, 0.01, 0.02, 0.04, 0.5]
    assert xa.holm(p, 0.05) == [True, True, False, False, False]
    assert xa.benjamini_hochberg(p, 0.05) == [True, True, True, True, False]
    assert abs(xa.sidak_threshold(0.05, 100) - 0.0005128014162623096) < 1e-15


def test_registry_hash_chain_and_lookahead(tmp_path):
    reg = xa.Registry(str(tmp_path / "reg.json"))
    code = "lambda h: [h[-1].de]"
    rec = reg.register("lap_lai_de", "chọn lại số đề hôm qua", code, 1, 30,
                       now=datetime(2025, 3, 1, 12, tzinfo=timezone.utc))
    assert reg.verify_chain() and rec["cham_tu_ngay"] == "2025-03-02"
    draws = xa.simulate_draws(120, seed=5, start=date(2025, 1, 1))
    res = reg.evaluate(rec["id"], draws, lambda h: [h[-1].de], code)
    assert res["so_ngay_da_cham"] == 30 and res["du_so_ngay"]
    with pytest.raises(ValueError):
        reg.evaluate(rec["id"], draws, lambda h: [h[-1].de], code + " ")  # sửa mã sau đăng ký
    reg.records[0]["quy_tac"] = "sửa ngầm"
    assert not reg.verify_chain()


def test_load_csv(tmp_path):
    p = tmp_path / "kq.csv"
    rows = ["ngay," + ",".join(f"g{i}" for i in range(27))]
    rows.append("2025-01-02," + ",".join(str(10000 + i) for i in range(27)))
    p.write_text("\n".join(rows), encoding="utf-8")
    d = xa.load_draws(str(p))
    assert d[0].de == 0 and d[0].numbers[5] == 5


def test_load_rejects_placeholder_and_bad_lengths(tmp_path):
    hdr = "ngay," + ",".join(f"g{i}" for i in range(27))
    good = ["12345"] * 10 + ["0123"] * 10 + ["045"] * 3 + ["07"] * 4
    good[0] = "54321"
    p = tmp_path / "kq.csv"
    p.write_text("\n".join([hdr, "2025-01-02," + ",".join(good),
                             "2025-01-03," + ",".join(["0"] * 27)]), encoding="utf-8")
    with pytest.raises(ValueError, match="placeholder"):
        xa.load_draws(str(p))
    bad = list(good); bad[20] = "45"          # mất số 0 đầu ở giải 6
    p.write_text("\n".join([hdr, "2025-01-02," + ",".join(bad)]), encoding="utf-8")
    assert len(xa.load_draws(str(p))) == 1    # mặc định không soát độ dài
    with pytest.raises(ValueError, match="21"):
        xa.load_draws(str(p), strict_lengths=True)
    p.write_text("\n".join([hdr, "2025-01-02," + ",".join(good), "2025-01-08," + ",".join(good)]),
                 encoding="utf-8")
    assert xa.date_gaps(xa.load_draws(str(p), strict_lengths=True)) == [
        {"tu": "2025-01-02", "den": "2025-01-08", "so_ngay_thieu": 5}]
def test_binom_tail_float_matches_exact():
    from fractions import Fraction
    for n, k in [(30, 12), (50, 20), (80, 0), (80, 81), (60, 60)]:
        exact = float(xa.binom_tail(n, k, xa.p_lo()))
        approx = xa.binom_tail_float(n, k, xa.p_lo())
        assert abs(exact - approx) <= 1e-12 + 1e-9 * exact


def test_evaluate_strategy_fast_on_many_years():
    import time
    draws = xa.simulate_draws(3650, seed=7)
    t = time.time()
    res = xa.evaluate_strategy(draws, lambda h: [h[-1].de], warmup=1)
    assert time.time() - t < 5
    assert 0.0 <= res.p_value_exact <= 1.0


def test_benjamini_yekutieli_stricter_than_bh():
    pv = [0.001, 0.008, 0.039, 0.041, 0.042, 0.06, 0.074, 0.205, 0.212, 0.216]
    bh, by = xa.benjamini_hochberg(pv), xa.benjamini_yekutieli(pv)
    assert all(b or not y for b, y in zip(bh, by))   # BY ⊆ BH
    assert sum(by) <= sum(bh)
    assert xa.benjamini_yekutieli([]) == []


def test_load_rejects_blank_cell_shifting_columns(tmp_path):
    hdr = "ngay," + ",".join(f"g{i}" for i in range(27))
    vals = [str(10000 + i) for i in range(27)]
    shifted = vals[:5] + [""] + vals[5:]        # 1 ô trống + 1 ô thừa: vẫn 27 giá trị khác rỗng
    p = tmp_path / "kq.csv"
    p.write_text(hdr + "\n2025-01-02," + ",".join(shifted), encoding="utf-8")
    with pytest.raises(ValueError):
        xa.load_draws(str(p))
    p.write_text(hdr + "\n2025-01-02," + ",".join(vals) + ",,", encoding="utf-8")
    assert len(xa.load_draws(str(p))) == 1      # ô trống ở cuối dòng vẫn chấp nhận


def test_eprocess_valid_under_null_and_detects_edge():
    import random
    r = random.Random(11)
    def nhay(p):   # số nháy của bộ 5 số trong 1 kỳ: Nhị thức(27, p)
        return sum(r.random() < p for _ in range(27))
    reps, false_alarm = 400, 0
    for _ in range(reps):
        if max(xa.eprocess_mean([nhay(0.05) for _ in range(1000)], 1.35)) >= 20:
            false_alarm += 1
    assert false_alarm / reps <= 0.06            # Ville: <= 5% (thêm dung sai mô phỏng)
    # lợi thế +20% số nháy: phải phát hiện trong phần lớn các lần, trước 1.000 kỳ
    hit = sum(max(xa.eprocess_mean([nhay(0.06) for _ in range(1000)], 1.35)) >= 20 for _ in range(100))
    assert hit >= 80
    with pytest.raises(ValueError):
        xa.eprocess_mean([1], 1.35, lambdas=(0.9,))


def test_eprocess_any_hit_and_exact_baseline():
    assert xa.p_set_any_given_u(24) == 1 - xa.Fraction(math.comb(76, 5), math.comb(100, 5))
    p0 = float(xa.p_set_any_given_u(24))
    w = xa.eprocess_any_hit([1] * 50, [p0] * 50)
    assert w[-1] > w[0] > 1
def test_distinct_tails_distribution_exact():
    from fractions import Fraction
    dist = xa.distinct_tails_distribution()
    assert sum(dist) == 1
    # E[u] = 100·(1 − 0,99^27)
    assert sum(u * p for u, p in enumerate(dist)) == 100 * (1 - Fraction(99, 100) ** 27)
    # vét cạn với bài nhỏ: 3 giải, 4 số
    import itertools
    def small(n, m):
        cnt = [0] * (n + 1)
        for t in itertools.product(range(m), repeat=n):
            cnt[len(set(t))] += 1
        return [Fraction(c, m ** n) for c in cnt]
    for u in range(4):
        exact = Fraction(math.comb(4, u) * math.factorial(u) * xa._stirling2(3, u), 4 ** 3)
        assert exact == small(3, 4)[u]


def test_random_k_baseline_identity():
    # Σ_u P(U=u)·P(hit | u) = 1 − 0,95^27 (bộ 5 cố định)
    dist = xa.distinct_tails_distribution()
    total = sum(p * xa.p_set_hit_given_u(5, u) for u, p in enumerate(dist))
    assert total == xa.p_set_hit(5)
    assert abs(float(total) - (1 - 0.95 ** 27)) < 1e-15


def test_binom_power_alpha_respected():
    r = xa.binom_power(180, 0.7497, 0.85, alpha=0.05 / 6)
    assert r["alpha_thuc"] <= 0.05 / 6
    assert 0 < r["power"] < 1
    assert xa.min_detectable_rate(180, 0.7497, 0.05 / 6) > 0.8


def test_leakage_check_catches_future_use():
    draws = xa.simulate_draws(300, seed=3)
    honest = lambda d, t: sorted(set(d[t - 1].numbers))[:5]
    cheat = lambda d, t: sorted(set(d[t].numbers))[:5]          # nhìn trước kỳ t
    subtle = lambda d, t: sorted(set(d[t - 1].numbers))[:5] if len(d) < 0 else \
        sorted(range(100), key=lambda x: -sum(dr.numbers.count(x) for dr in d))[:5]  # dùng tần suất TOÀN bộ dữ liệu
    assert xa.leakage_check(honest, draws, 30)["dat"]
    assert not xa.leakage_check(cheat, draws, 30)["dat"]
    assert not xa.leakage_check(subtle, draws, 30)["dat"]


def test_leakage_check_catches_length_dependence():
    draws = xa.simulate_draws(300, seed=5)
    # không đọc nội dung tương lai nhưng phụ thuộc số kỳ còn lại → vẫn là rò rỉ
    by_len = lambda d, t: [(len(d) - t) % 100, 1, 2, 3, 4]
    r = xa.leakage_check(by_len, draws, 20)
    assert not r["dat"]


def test_duplicate_draws_detects_overwritten_row(tmp_path):
    hdr = "ngay," + ",".join(f"g{i}" for i in range(27))
    r = random.Random(3)
    def row():
        return ",".join(str(r.randrange(10 ** n)).zfill(n) for n in xa.PRIZE_DIGITS)
    a, b, c = row(), row(), row()
    p = tmp_path / "kq.csv"
    p.write_text("\n".join([hdr, "2006-09-21," + a, "2006-09-22," + b, "2006-09-25," + a, "2006-09-26," + c]),
                 encoding="utf-8")
    assert xa.duplicate_draws(str(p)) == [{"ky": "2006-09-25", "trung_voi": "2006-09-21", "so_giai_trung": 27}]
