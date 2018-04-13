
"""test_dna.py - unit tests for DNA.h."""

import os
import unittest
import warnings

import ptools
from ptools import DNA


PDB_BASE_PAIR = os.path.join(ptools.DATA_DIR, 'bp.red.pdb')
PDB_BASE_PAIR2 = os.path.join(ptools.DATA_DIR, 'bp.ato.pdb')
PDB_DNA = os.path.join(os.path.dirname(__file__), 'heligeom', 'data', 'generate_B_DNA.expected.pdb')


class TestDNABindings(unittest.TestCase):
    """Check that the DNA class provides required methods."""

    def test_has_size(self):
        self.assertTrue(hasattr(DNA, 'size'))

    def test_has_len(self):
        self.assertTrue(hasattr(DNA, '__len__'))

    def test_has_add(self):
        self.assertTrue(hasattr(DNA, 'add'))

    def test_has_change_type(self):
        self.assertTrue(hasattr(DNA, 'change_type'))

    def test_has_apply_local(self):
        self.assertTrue(hasattr(DNA, 'apply_local'))

    def test_has_sub_DNA(self):
        self.assertTrue(hasattr(DNA, 'sub_DNA'))

    def test_has_change_representation(self):
        self.assertTrue(hasattr(DNA, 'change_representation'))

    def test_has_print_PDB(self):
        self.assertTrue(hasattr(DNA, 'print_PDB'))


class TestDNA(unittest.TestCase):

    def setUp(self):
        self.dna = DNA(PDB_BASE_PAIR, PDB_DNA)
        self.assertEqual(self.dna[0].size(), 11)
        self.assertEqual(len(self.dna[0].get_rigid_body()), 11)

    def test_Size(self):
        self.assertEqual(self.dna.size(), 16)

    def test_len(self):
        self.assertEqual(len(self.dna), 16)
        self.assertEqual(len(self.dna), self.dna.size())

    def test_Add(self):
        bp = ptools.BasePair(self.dna[0].get_rigid_body())
        self.dna.add(bp)
        self.assertEqual(self.dna.size(), 17)

        dna = ptools.DNA(self.dna)
        self.dna.add(dna)
        self.assertEqual(self.dna.size(), 34)

    def test_change_type(self):
        warnings.warn("only check the call, not the result")
        self.dna.change_type(0, "A", PDB_BASE_PAIR)

    def test_apply_local(self):
        warnings.warn("only check the call, not the result")
        self.dna.apply_local(ptools.Roll(30), self.dna.size() / 2)

    def test_sub_DNA(self):
        warnings.warn("only check the call, not the result")
        self.dna.sub_DNA(2, self.dna.size() - 3)

    def test_change_representation(self):
        warnings.warn("only check the call, not the result")
        self.dna.change_representation(PDB_BASE_PAIR2)

    def test_print_PDB(self):
        s = self.dna.print_PDB()
        self.assertNotEqual(s, '')


if __name__ == '__main__':
    unittest.main()
