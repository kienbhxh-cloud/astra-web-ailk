import itertools
import unittest

from astra_math.pnp_prototypes import (
    maximize_set_coverage,
    select_rules_maxsat,
    synthesize_affine_modular,
)


class MaxSATTests(unittest.TestCase):
    def test_planted_boolean_rule_and_replay(self):
        inputs = {"correct": [0, 1, 0, 1], "noise": [1, 0, 1, 0]}
        first = select_rules_maxsat(inputs, [0, 1, 0, 1], max_rules=1)
        second = select_rules_maxsat(inputs, [0, 1, 0, 1], max_rules=1)
        self.assertEqual(first["status"], "optimal")
        self.assertTrue(first["optimal"])
        self.assertEqual(first["selected_rules"], ["correct"])
        self.assertEqual(first["training_cost"], 1)
        self.assertEqual(first["training_errors"], 0)
        for key in ("selected_rules", "training_predictions", "objective_bounds", "training_cost"):
            self.assertEqual(first[key], second[key])
        self.assertGreaterEqual(first["elapsed_seconds"], 0)

    def test_infeasible_hard_required_rule(self):
        result = select_rules_maxsat({"a": [1]}, [1], max_rules=0,
                                     required_rules=["a"])
        self.assertEqual(result["status"], "unsat")
        self.assertFalse(result["optimal"])
        self.assertIsNone(result["selected_rules"])

    def test_surrogate_optimum_matches_enumeration(self):
        rules = {"a": [1, 0, 1, 0], "b": [0, 1, 0, 0], "c": [0, 0, 0, 1]}
        y = [1, 1, 1, 0]
        result = select_rules_maxsat(rules, y, max_rules=2,
                                     mistake_weight=5, rule_penalty=2)
        costs = []
        for count in range(3):
            for chosen in itertools.combinations(rules, count):
                predictions = [any(rules[name][i] for name in chosen) for i in range(len(y))]
                costs.append(5 * sum(a != bool(b) for a, b in zip(predictions, y)) + 2 * count)
        self.assertEqual(result["training_cost"], min(costs))


class SynthesisTests(unittest.TestCase):
    def test_planted_modular_program(self):
        examples = [(x, (3 * x + 7) % 100) for x in range(10)]
        result = synthesize_affine_modular(examples, max_a=9, max_b=9)
        self.assertEqual(result["status"], "sat")
        self.assertEqual(result["parameters"], {"a": 3, "b": 7})
        self.assertIsNone(result["optimal"])
        self.assertEqual(result["training_predictions"], [y for _, y in examples])
        again = synthesize_affine_modular(examples, max_a=9, max_b=9)
        self.assertEqual(result["parameters"], again["parameters"])

    def test_conflicting_examples_are_unsat(self):
        result = synthesize_affine_modular([(2, 3), (2, 4)])
        self.assertEqual(result["status"], "unsat")
        self.assertIsNone(result["parameters"])


class CoverageTests(unittest.TestCase):
    def test_optimum_matches_exhaustive_small_combinations(self):
        scenarios = [[0, 1], [1, 2], [3], [2, 4], [4, 5], [0, 5]]
        weights = [1, 2, 1, 3, 1, 2]
        result = maximize_set_coverage(scenarios, list(range(6)), k=2, weights=weights)
        expected = max(sum(w for row, w in zip(scenarios, weights) if set(chosen) & set(row))
                       for chosen in itertools.combinations(range(6), 2))
        self.assertEqual(result["status"], "optimal")
        self.assertTrue(result["optimal"])
        self.assertEqual(len(result["selected_labels"]), 2)
        self.assertEqual(result["weighted_coverage"], expected)
        again = maximize_set_coverage(scenarios, list(range(6)), k=2, weights=weights)
        self.assertEqual(result["selected_labels"], again["selected_labels"])

    def test_infeasible_cardinality(self):
        result = maximize_set_coverage([[0], [1]], [0, 1], k=3)
        self.assertEqual(result["status"], "unsat")
        self.assertIsNone(result["weighted_coverage"])

    def test_zero_k_and_repeated_labels(self):
        result = maximize_set_coverage([[0, 0], [1, 2]], [0, 1], k=0)
        self.assertEqual(result["selected_labels"], [])
        self.assertEqual(result["weighted_coverage"], 0)


class InputValidationTests(unittest.TestCase):
    def test_empty_candidate_sets_are_well_defined(self):
        rule = select_rules_maxsat({}, [False, True], max_rules=0)
        self.assertEqual(rule["status"], "optimal")
        self.assertEqual(rule["training_errors"], 1)
        self.assertEqual(rule["selected_rules"], [])
        coverage = maximize_set_coverage([[]], [], k=0)
        self.assertEqual(coverage["status"], "optimal")
        self.assertEqual(coverage["weighted_coverage"], 0)

    def test_invalid_inputs(self):
        cases = [
            lambda: select_rules_maxsat({"a": [True]}, [True, False]),
            lambda: select_rules_maxsat({"a": [2]}, [1]),
            lambda: synthesize_affine_modular([(1, 100)]),
            lambda: synthesize_affine_modular([]),
            lambda: maximize_set_coverage([[1]], [1, 1], k=1),
            lambda: maximize_set_coverage([[1]], [1], k=1, weights=[-1]),
        ]
        for call in cases:
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
