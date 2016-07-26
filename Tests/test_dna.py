
"""test_dna.py - unit tests for DNA.h."""

import os
import unittest
import warnings

import ptools
from ptools import DNA


PDB_BASE_PAIR = os.path.join(os.path.dirname(__file__), 'heligeom', 'bp.red.pdb')
PDB_BASE_PAIR2 = os.path.join(os.path.dirname(__file__), 'heligeom', 'bp.ato.pdb')
PDB_DNA = os.path.join(os.path.dirname(__file__), 'heligeom', 'generate_B_DNA.expected')


class TestDNABindings(unittest.TestCase):
    """Check that the DNA class provides required methods."""
    
    def test_has_Size(self):
        self.assertTrue(hasattr(DNA, 'Size'))

    def test_has_len(self):
        self.assertTrue(hasattr(DNA, '__len__'))

    def test_has_Add(self):
        self.assertTrue(hasattr(DNA, 'Add'))

    def test_has_ChangeType(self):
        self.assertTrue(hasattr(DNA, 'ChangeType'))

    def test_has_ApplyLocal(self):
        self.assertTrue(hasattr(DNA, 'ApplyLocal'))

    def test_has_SubDNA(self):
        self.assertTrue(hasattr(DNA, 'SubDNA'))

    def test_has_ChangeRepresentation(self):
        self.assertTrue(hasattr(DNA, 'ChangeRepresentation'))

    def test_has_PrintPDB(self):
        self.assertTrue(hasattr(DNA, 'PrintPDB'))


class TestDNA(unittest.TestCase):

    def setUp(self):
        self.dna = DNA(PDB_BASE_PAIR, PDB_DNA)
        self.assertEqual(self.dna[0].Size(), 11)
        self.assertEqual(len(self.dna[0].GetRigidBody()), 11)

    def test_Size(self):
        self.assertEqual(self.dna.Size(), 16)

    def test_len(self):
        self.assertEqual(len(self.dna), 16)
        self.assertEqual(len(self.dna), self.dna.Size())

    def test_Add(self):
        bp = ptools.BasePair(self.dna[0].GetRigidBody())
        self.dna.Add(bp)
        self.assertEqual(self.dna.Size(), 17)

        dna = ptools.DNA(self.dna)
        self.dna.Add(dna)
        self.assertEqual(self.dna.Size(), 34)

    def test_ChangeType(self):
        warnings.warn("only check the call, not the result")
        self.dna.ChangeType(0, "A", PDB_BASE_PAIR)

    def test_ApplyLocal(self):
        warnings.warn("only check the call, not the result")
        self.dna.ApplyLocal(ptools.Roll(30), self.dna.Size() / 2)

    def test_SubDNA(self):
        warnings.warn("only check the call, not the result")
        self.dna.SubDNA(2, self.dna.Size() - 3)

    def test_ChangeRepresentation(self):
        warnings.warn("only check the call, not the result")
        self.dna.ChangeRepresentation(PDB_BASE_PAIR2)

    def test_PrintPDB(self):
        s = self.dna.PrintPDB()
        self.assertNotEqual(s, '')



if __name__ == '__main__':
    unittest.main()
