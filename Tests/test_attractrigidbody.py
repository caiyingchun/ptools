
import os
import unittest

from ptools import Rigidbody, AttractRigidbody


TEST_1FINR_PDB = os.path.join(os.path.dirname(__file__), 'data', '1FIN_r.pdb')


class TestAttractRigidbody(unittest.TestCase):
    def setUp(self):
        rigid = Rigidbody(TEST_1FINR_PDB)
        self.attrigid = AttractRigidbody(rigid)

    def testlen(self):
        self.assertEqual(len(self.attrigid), 2365)


if __name__ == '__main__':
    unittest.main()
