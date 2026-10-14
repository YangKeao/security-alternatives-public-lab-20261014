import unittest
from batch import valid_batch
class CaseB(unittest.TestCase):
    def test_oversized_rejected(self): self.assertFalse(valid_batch(101))
    def test_boundary(self): self.assertTrue(valid_batch(100))
