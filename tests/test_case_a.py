import unittest
from policy import same_tenant
class CaseA(unittest.TestCase):
    def test_cross_tenant_rejected(self): self.assertFalse(same_tenant("demo-a", "demo-b"))
