
import os
import unittest

import ptools
from ptools import (DNA, BasePair, ADNA, BDNA, Roll, Rigidbody, Coord3D,
                    AttractRigidbody, AttractForceField1, AttractPairList)
from ptools.heligeom import heli_analyze

HELI_PI = 3.141592653589793

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
        result = dna.print_PDB()
        expected = open(TEST_BDNA_EXPECTED_PDB).read()
        self.assertEqual(result, expected)

    def testBasicManipulation(self):
        # translate the DNA in coarse grain representation
        dna = DNA(TEST_BP_RED, TEST_BDNA_EXPECTED_PDB)
        self.assertEqual(dna[0].size(), 11)
        self.assertEqual(len(dna[0].get_rigid_body()), 11)

        # add a base Pair
        bp = BasePair(dna[0].get_rigid_body())
        dna.add(bp)

        # add itself
        new = DNA(dna)
        dna.add(new, BDNA())

        # change the type of a base
        dna.change_type(0, "A", TEST_BP_RED)

        # turn the center base
        dna.apply_local(Roll(30), dna.size() / 2)

        # trim the extremities
        dna = dna.sub_DNA(2, dna.size() - 3)

        # change to a All Atom representation
        dna.change_representation(TEST_BP_PDB)

        result = dna.print_PDB()
        with open(TEST_BASIC_MANIP_EXPECTED_PDB, 'rt') as f:
            expected = f.read()
        self.assertEqual(result, expected)

    def testCGfromPDBFile(self):
        dna = DNA(TEST_BP_PDB, TEST_BDNA_EXPECTED_PDB)  # gros grain
        result = dna.print_PDB()
        expected = open(TEST_CG_FROM_PDBFILE_EXPECTED_PDB).read()
        self.assertEqual(result, expected)

    def testEnergy(self):
        prot = AttractRigidbody(TEST_1A74_PROT_RED)
        dna = AttractRigidbody(TEST_1A74_OPT_RED)

        cutoff = 1000

        forcefield = AttractForceField1(TEST_FF_AMINON, surreal(cutoff))
        ener = forcefield.nonbon8(prot, dna, AttractPairList(prot, dna, cutoff))

        self.assertAlmostEqual(ener, -51.6955215854)
        self.assertEqual(prot.size(), 706)
        self.assertEqual(dna.size(), 231)


class TestHeligeom2(unittest.TestCase):

    def test_analyze_x_translate(self):
        mono1 = ptools.Rigidbody(TEST_1A74_PROT_RED)
        mono2 = ptools.Rigidbody(TEST_1A74_PROT_RED)
        deltax = 15.0
        tr = ptools.Coord3D(deltax, 0, 0)
        mono2.translate(tr)
        hp = heli_analyze(mono1, mono2, True)
        print hp
        self.assertAlmostEqual(hp.angle, 0.0)
        self.assertAlmostEqual(hp.normtranslation, deltax)
        self.assertAlmostEqual(hp.unit_vector.x, 1.0)
        self.assertAlmostEqual(hp.unit_vector.y, 0.0)
        self.assertAlmostEqual(hp.unit_vector.z, 0.0)


    def test_analyze_x_translate_rotate(self):
        mono1 = ptools.Rigidbody(TEST_1A74_PROT_RED)
        mono2 = ptools.Rigidbody(TEST_1A74_PROT_RED)
        delta = 15.0
        tr = ptools.Coord3D(delta, 0, 0)
        mono2.translate(tr)
        point = Coord3D(0,0,0)
        axis = Coord3D(1,0,0)
        angle = HELI_PI /4
        mono2.ab_rotate(point, axis, angle)
        hp = heli_analyze(mono1, mono2, True)
        print hp
        self.assertAlmostEqual(hp.angle, angle)
        self.assertAlmostEqual(hp.normtranslation, delta)
        self.assertAlmostEqual(hp.unit_vector.x, 1.0)
        self.assertAlmostEqual(hp.unit_vector.y, 0.0)
        self.assertAlmostEqual(hp.unit_vector.z, 0.0)


if __name__ == "__main__":
    unittest.main()
