import unittest
from astra_math.pnp_benchmark import mask,coverage,exact_optimum,metrics,make_draws
class BenchmarkTests(unittest.TestCase):
    def test_exact_tie_and_duplicate(self):
        self.assertEqual(exact_optimum([mask([0,0,1]),mask([2])],[0,1,2],1),(1,-1,(0,)))
    def test_metrics_keep_multiplicity(self):
        self.assertEqual(metrics([0],[[0,0,1],[2,3]]),{'days':2,'any_hit_rate':.5,'distinct_hits_per_day':.5,'occurrences_per_day':1})
    def test_reproducible_generation_and_prefix(self):
        self.assertEqual(make_draws(11,'uniform',3),make_draws(11,'uniform',5)[:3])
        self.assertEqual(len(make_draws(11,'planted',2)[0]),27)
    def test_coverage(self):
        self.assertEqual(coverage([1],[mask([1]),mask([2]),mask([1,3])]),2)
