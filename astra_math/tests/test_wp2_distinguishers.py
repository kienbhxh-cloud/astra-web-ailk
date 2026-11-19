import numpy as np
import pytest
from astra_math import wp2_distinguishers as w


@pytest.fixture(autouse=True)
def small_b(monkeypatch):
    monkeypatch.setattr(w, "B_PERM", 99)
    monkeypatch.setattr(w, "B_LZMA", 19)


def test_all_pvalues_valid_and_count_locked():
    d, raw = w.simulate_raw(300, 1)
    p = w.run_all(d, raw)
    assert list(p) == list(w.TESTS)            # đúng 13 phép, đúng thứ tự đã khóa
    assert all(0 < v <= 1 for v in p.values())
    assert w.holm_report(p)["so_phep"] == 13


def test_resolution_rule():
    assert 1 / (9999 + 1) < w.ALPHA / len(w.TESTS)   # B chính thức đủ lớn cho Holm


def test_detects_strong_lag1_repetition():
    d, raw = w.simulate_raw(800, 5)
    r = np.random.default_rng(1)
    for t in range(1, 800):
        j = int(r.integers(0, 27)); raw[t][j] = raw[t][j][:-2] + raw[t - 1][int(r.integers(0, 27))][-2:]
    P = w.presence(w.tails(raw))
    assert w.d06(P, np.random.default_rng(0)) <= 0.02


def test_detects_digit_bias():
    d, raw = w.simulate_raw(800, 6)
    r = np.random.default_rng(2)
    for t in range(800):
        if r.random() < 0.5:
            raw[t][23] = raw[t][23][:-1] + "7"
    assert w.d03(raw) < 1e-4


def test_permutation_preserves_days():
    d, raw = w.simulate_raw(50, 3)
    T = w.tails(raw); P = w.presence(T)
    assert P.sum(1).tolist() == [len(set(r.tolist())) for r in T]
