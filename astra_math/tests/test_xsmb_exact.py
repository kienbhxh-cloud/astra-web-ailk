"""Exact small-space cross-checks; no historical empirical testing."""
from fractions import Fraction
from itertools import combinations, product
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from astra_math import xsmb_exact as x


class ExactOccupancyTests(unittest.TestCase):
    def test_presence_against_full_enumeration(self):
        for alphabet in range(1, 5):
            for draws in range(5):
                outcomes = list(product(range(alphabet), repeat=draws))
                favorable = sum(0 in v for v in outcomes)
                self.assertEqual(x.p_presence(draws, alphabet), Fraction(favorable, len(outcomes)))

    def test_all_specified_labels_against_full_enumeration(self):
        for alphabet in range(1, 5):
            for draws in range(5):
                outcomes = list(product(range(alphabet), repeat=draws))
                for k in range(alphabet + 1):
                    favorable = sum(set(range(k)) <= set(v) for v in outcomes)
                    self.assertEqual(x.p_all_distinct(k, draws, alphabet),
                                     Fraction(favorable, len(outcomes)))

    def test_nhay_against_full_enumeration(self):
        for alphabet in range(1, 5):
            for draws in range(5):
                outcomes = list(product(range(alphabet), repeat=draws))
                distribution = x.nhay_distribution(draws, alphabet)
                for j, p in enumerate(distribution):
                    self.assertEqual(p, Fraction(sum(v.count(0) == j for v in outcomes), len(outcomes)))
                self.assertEqual(sum(distribution), 1)
                self.assertEqual(sum(j * p for j, p in enumerate(distribution)),
                                 x.expected_occurrences(draws, alphabet))

    def test_joint_occupancy_against_full_enumeration(self):
        for alphabet in range(1, 5):
            for draws in range(5):
                outcomes = list(product(range(alphabet), repeat=draws))
                for k in range(alphabet + 1):
                    dist = x.selected_occupancy_distribution(k, draws, alphabet)
                    for r, p in enumerate(dist):
                        favorable = sum(len(set(v) & set(range(k))) == r for v in outcomes)
                        self.assertEqual(p, Fraction(favorable, len(outcomes)))
                    self.assertEqual(sum(dist), 1)
                    self.assertEqual(dist[k], x.p_all_distinct(k, draws, alphabet))

    def test_random_k_hypergeometric_against_all_subsets(self):
        for alphabet in range(1, 8):
            for k in range(alphabet + 1):
                selected = list(combinations(range(alphabet), k))
                for u in range(alphabet + 1):
                    favorable = sum(bool(set(v) & set(range(u))) for v in selected)
                    self.assertEqual(x.random_k_anyhit(u, k, alphabet),
                                     Fraction(favorable, len(selected)))

    def test_reference_xsmb_probabilities(self):
        self.assertAlmostEqual(float(x.p_presence()), .23765728565289646, places=15)
        self.assertAlmostEqual(float(x.p_all_distinct(2)), .05488209778544517, places=15)
        expected_three = 1 - 3 * Fraction(99, 100)**27 + 3 * Fraction(98, 100)**27 - Fraction(97, 100)**27
        self.assertEqual(x.p_all_distinct(3), expected_three)
        self.assertEqual(x.expected_occurrences(), Fraction(27, 100))
        self.assertNotEqual(x.p_all_distinct(2), x.p_presence()**2)

    def test_empty_draw_and_empty_selection(self):
        self.assertEqual(x.p_presence(0), 0)
        self.assertEqual(x.p_all_distinct(0, 0), 1)
        self.assertEqual(x.p_all_distinct(1, 0), 0)
        self.assertEqual(x.nhay_distribution(0), (Fraction(1),))
        self.assertEqual(x.selected_occupancy_distribution(0, 0), (Fraction(1),))
        self.assertEqual(x.random_k_anyhit(100, 0), 0)
        self.assertEqual(x.random_k_anyhit(100, 1), 1)
        self.assertEqual(x.random_k_anyhit(0, 100), 0)

    def test_rejects_invalid_count_inputs(self):
        calls = [lambda: x.p_presence(-1), lambda: x.p_presence(1, 0),
                 lambda: x.p_presence(True), lambda: x.p_presence(2.0),
                 lambda: x.p_all_distinct(101), lambda: x.p_all_distinct(-1),
                 lambda: x.p_selected_occupancy(3, 4), lambda: x.p_selected_occupancy(2, -1),
                 lambda: x.random_k_anyhit(101, 1), lambda: x.random_k_anyhit(1, 101),
                 lambda: x.random_k_anyhit(True, 1), lambda: x.nhay_distribution(1, False)]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises(ValueError):
                    call()


class ExactExpectationTests(unittest.TestCase):
    def test_fixed_gross_return_and_stake(self):
        self.assertEqual(x.expected_net(100, 400, Fraction(1, 4)), 0)
        self.assertEqual(x.expected_net(100, 300, Fraction(1, 4)), -25)
        self.assertEqual(x.expected_net(100, 400, Fraction(1, 4), 25), Fraction(75, 4))
        self.assertEqual(x.expected_net(1, 3, 0), -1)
        self.assertEqual(x.expected_net(1, 3, 1), 2)

    def test_linear_occurrence_payment(self):
        self.assertEqual(x.expected_net_occurrences(1, 3), Fraction(-19, 100))
        self.assertEqual(x.expected_net_occurrences(1, Fraction(100, 27)), 0)
        self.assertEqual(x.expected_net_occurrences(1, Fraction(100, 27),
                                                   additional_return_on_any_hit=1), x.p_presence())

    def test_occurrence_ev_against_full_enumeration(self):
        alphabet, draws = 4, 4
        outcomes = list(product(range(alphabet), repeat=draws))
        payoffs = [Fraction(3, 2) * v.count(0) + (Fraction(1, 3) if 0 in v else 0) - 2
                   for v in outcomes]
        self.assertEqual(x.expected_net_occurrences(2, '3/2', draws, alphabet, '1/3'),
                         sum(payoffs) / len(payoffs))

    def test_decimal_money_inputs(self):
        self.assertEqual(x.expected_net('0.1', '0.4', '0.25'), 0)
        self.assertEqual(x.expected_net(.1, .4, .25), 0)

    def test_invalid_money_and_probability(self):
        calls = [lambda: x.expected_net(-1, 1, .5),
                 lambda: x.expected_net(1, -1, .5),
                 lambda: x.expected_net(1, 2, 1.01),
                 lambda: x.expected_net(1, 2, -.1),
                 lambda: x.expected_net(1, 2, True),
                 lambda: x.expected_net(math.nan, 2, .5),
                 lambda: x.expected_net(1, math.inf, .5),
                 lambda: x.expected_net_occurrences(1, -1),
                 lambda: x.expected_net_occurrences(1, 2, additional_return_on_any_hit=-1)]
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises(ValueError):
                    call()


if __name__ == '__main__':
    unittest.main(verbosity=2)
