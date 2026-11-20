import itertools
import numpy as np
import pytest
from astra_math.pnp import f1v1 as f
from astra_math.pnp.rule_count import count_rules_brute, count_rules_tensor
from astra_math.pnp.rule_count_poly import count_rules_poly


def _X(seed=5, n=1500):
    tails = np.random.default_rng(seed).integers(0, 100, (n, 27))
    return tails, f.feature_tensor(tails, 20).reshape(-1, f.F)


def test_exclusions_exactly_contradictory_or_redundant():
    _, X = _X()
    ex = set(f.cross_exclusions())
    grp = [gi for gi, g in enumerate(f.GROUP_SIZES) for _ in range(g)]
    for a, b in itertools.combinations(range(f.F), 2):
        if grp[a] == grp[b]:
            continue
        both = X[:, a] & X[:, b]
        degenerate = (not both.any()) or (both == X[:, a]).all() or (both == X[:, b]).all()
        assert ((a, b) in ex) == degenerate, (f.NAMES[a], f.NAMES[b])


def test_features_use_only_past():
    tails, _ = _X(n=200)
    t = 150
    X0 = f.features(tails, t)
    alt = tails.copy(); alt[t:] = np.random.default_rng(1).integers(0, 100, alt[t:].shape)
    assert (f.features(alt, t) == X0).all()
    assert (f.features(tails[:t], t) == X0).all()        # cắt bỏ tương lai


def test_poly_counter_matches_tensor_on_f1v1():
    ex = f.cross_exclusions()
    for s in (1, 2, 3):
        assert count_rules_poly(f.GROUP_SIZES, s, ex) == count_rules_tensor(f.GROUP_SIZES, s, extra_exclusions=ex)[0]
    assert count_rules_poly(f.GROUP_SIZES, 14, ex) == 606032


def test_b1_out_of_range_rejected():
    with pytest.raises(ValueError):
        count_rules_tensor([1, 1, 1], 2, extra_exclusions=[(0, 5)])
