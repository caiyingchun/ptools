
import unittest

from ptools import Rigidbody, AttractRigidbody

from . import TEST_LIGAND_PDB


class TestAttractRigidbody(unittest.TestCase):
    def setUp(self):
        rigid = Rigidbody(TEST_LIGAND_PDB)
        self.attrigid = AttractRigidbody(rigid)

    def test_len(self):
        self.assertEqual(len(self.attrigid), 2365)


if __name__ == '__main__':
    unittest.main()
