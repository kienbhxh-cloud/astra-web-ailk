import unittest
from astra_math.pnp_integration import probability_compatibility

class IntegrationTests(unittest.TestCase):
    def test_upstream_exact_probabilities_agree(self):
        self.assertTrue(all(probability_compatibility().values()))

if __name__=='__main__':unittest.main()
