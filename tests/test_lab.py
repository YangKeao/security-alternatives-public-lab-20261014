import unittest
from policy import same_tenant
from batch import valid_batch
class Baseline(unittest.TestCase):
    def test_same_tenant(self): self.assertTrue(same_tenant("demo-a", "demo-a"))
    def test_normal_batch(self): self.assertTrue(valid_batch(10))
