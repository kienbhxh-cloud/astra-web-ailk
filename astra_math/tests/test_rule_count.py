import itertools, random
from astra_math.pnp import rule_count as rc


def test_tensor_matches_closed_form_and_brute():
    for G in ([2, 2, 3], [1, 2, 2, 3], [3, 3, 1, 2], [2] * 5):
        for s in range(1, len(G) + 1):
            a = rc.count_rules_tensor(G, s)[0]
            assert a == rc.count_rules_closed_form(G, s) == rc.count_rules_brute(G, s)


def test_tensor_matches_brute_with_cross_group_exclusions():
    r = random.Random(7)
    for _ in range(20):
        G = [r.randint(1, 3) for _ in range(r.randint(3, 5))]
        F = sum(G)
        ex = [tuple(r.sample(range(F), 2)) for _ in range(r.randint(1, 4))]
        s = r.randint(1, len(G))
        assert rc.count_rules_tensor(G, s, extra_exclusions=ex)[0] == rc.count_rules_brute(G, s, ex)


def test_sample_grammar_counts():
    G = [2] * 10 + [5] * 4
    assert rc.count_rules_tensor(G, 3)[0] == 8830
