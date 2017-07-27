
import os
import unittest

import ptools
from ptools import (DNA, BasePair, ADNA, BDNA, Roll,
                    AttractRigidbody, AttractForceField1, AttractPairList)


TEST_BP_RED = os.path.join(ptools.DATA_DIR, 'bp.red.pdb')
TEST_BP_PDB = os.path.join(ptools.DATA_DIR, 'bp.ato.pdb')
TEST_BDNA_EXPECTED_PDB = os.path.join(os.path.dirname(__file__), 'data', 'generate_B_DNA.expected.pdb')
TEST_BASIC_MANIP_EXPECTED_PDB = os.path.join(os.path.dirname(__file__), 'data', 'basicManipulation.expected.pdb')
TEST_CG_FROM_PDBFILE_EXPECTED_PDB = os.path.join(os.path.dirname(__file__), 'data', 'CGfromPDBFile.expected.pdb')
TEST_1A74_PROT_RED = os.path.join(os.path.dirname(__file__), 'data', '1A74_prot.red')
TEST_1A74_OPT_RED = os.path.join(os.path.dirname(__file__), 'data', '1A74_opt.red')
TEST_FF_AMINON = os.path.join(os.path.dirname(__file__), 'data', 'aminon.par')


# deactivate auto-diff for now:
def surreal(r):
    return r


class TestHeligeom(unittest.TestCase):

    def testGenerateBDNA(self):
        dna = DNA(TEST_BP_PDB, "AAAAAATCGATCTATC", ADNA())  # tout atom
        result = dna.PrintPDB()
        expected = open(TEST_BDNA_EXPECTED_PDB).read()
        self.assertEqual(result, expected)

    def testBasicManipulation(self):
        # translate the DNA in coarse grain representation
        dna = DNA(TEST_BP_RED, TEST_BDNA_EXPECTED_PDB)
        self.assertEqual(dna[0].Size(), 11)
        self.assertEqual(len(dna[0].GetRigidBody()), 11)

        # add a base Pair
        bp = BasePair(dna[0].GetRigidBody())
        dna.add(bp)

        # add itself
        new = DNA(dna)
        dna.add(new, BDNA())

        # change the type of a base
        dna.change_type(0, "A", TEST_BP_RED)

        # turn the center base
        dna.apply_local(Roll(30), dna.Size() / 2)

        # trim the extremities
        dna = dna.SubDNA(2, dna.Size() - 3)

        # change to a All Atom representation
        dna.change_representation(TEST_BP_PDB)

        result = dna.PrintPDB()
        with open(TEST_BASIC_MANIP_EXPECTED_PDB, 'rt') as f:
            expected = f.read()
        self.assertEqual(result, expected)

    def testCGfromPDBFile(self):
        dna = DNA(TEST_BP_PDB, TEST_BDNA_EXPECTED_PDB)  # gros grain
        result = dna.PrintPDB()
        expected = open(TEST_CG_FROM_PDBFILE_EXPECTED_PDB).read()
        self.assertEqual(result, expected)

    def testEnergy(self):
        prot = AttractRigidbody(TEST_1A74_PROT_RED)
        dna = AttractRigidbody(TEST_1A74_OPT_RED)

        cutoff = 1000

        forcefield = AttractForceField1(TEST_FF_AMINON, surreal(cutoff))
        ener = forcefield.nonbon8(prot, dna, AttractPairList(prot, dna, cutoff))

        self.assertAlmostEqual(ener, -51.6955215854)
        self.assertEqual(prot.Size(), 706)
        self.assertEqual(dna.Size(), 231)


if __name__ == "__main__":
    unittest.main()
