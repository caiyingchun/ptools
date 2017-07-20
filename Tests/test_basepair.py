
"""test_basepair.py - unit tests for BasePair.h."""

import os
import unittest

import ptools
from ptools import BasePair


PDB_BASE_PAIR = os.path.join(ptools.DATA_DIR, 'bp.red.pdb')
PDB_BASE_PAIR2 = os.path.join(ptools.DATA_DIR, 'bp.ato.pdb')
PDB_DNA = os.path.join(os.path.dirname(__file__), 'heligeom', 'data', 'generate_B_DNA.expected.pdb')


class TestBasePairBindings(unittest.TestCase):
    """Check that the BasePair class provides required methods."""

    def test_has_Size(self):
        self.assertTrue(hasattr(BasePair, 'Size'))

    def test_has_len(self):
        self.assertTrue(hasattr(BasePair, '__len__'))

    def test_has_GetRigidBody(self):
        self.assertTrue(hasattr(BasePair, 'GetRigidBody'))


class TestBasePair(unittest.TestCase):

    def setUp(self):
        dna = ptools.DNA(PDB_BASE_PAIR, PDB_DNA)
        self.bp = dna[0]
        self.assertEqual(type(dna[0]), BasePair)

    def test_Size(self):
        self.assertEqual(self.bp.Size(), 11)

    def test_len(self):
        self.assertEqual(len(self.bp), 11)
        self.assertEqual(len(self.bp), self.bp.Size())


if __name__ == '__main__':
    unittest.main()
