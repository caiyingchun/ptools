
"""test_misc - Those tests should probably be moved somewhere adequat
at some point."""

import math
import unittest

from ptools import Rigidbody, Coord3D, Atom, Atomproperty, norm2, rmsd

from . import TEST_LIGAND_PDB


class TestBasicMoves(unittest.TestCase):
    def setUp(self):
        self.rigid1 = Rigidbody(TEST_LIGAND_PDB)
        self.rigid2 = Rigidbody(self.rigid1)
        self.rigid3 = Rigidbody(self.rigid2)

    def testBasicRmsd(self):
        rigtmp = Rigidbody(self.rigid1)
        self.assertEqual(rmsd(self.rigid1, self.rigid1), 0.0)
        self.rigid1.translate(Coord3D(4, 0, 0))
        self.assertEqual(rmsd(rigtmp, self.rigid1), 4)

    def testErrorsRmsd(self):
        rigid1 = Rigidbody()
        rigid2 = Rigidbody()
        # cannot calculate an rmsd on an empty object
        self.assertRaises(ValueError, rmsd, rigid1, rigid2)

        # check input paramter types:
        self.assertRaises(RuntimeError, rmsd, self.rigid1, "hello")
        self.assertRaises(RuntimeError, rmsd, "hello", self.rigid1)

    def testRmsdAtomSelection1(self):
        # tests rmsd with an AtomSelection object
        atsel = self.rigid1.select_all_atoms()
        self.assertEqual(rmsd(atsel, self.rigid2), 0)

    def testRmsdAtomSelection2(self):
        # tests rmsd with an AtomSelection object
        atsel = self.rigid1.select_all_atoms()
        self.assertEqual(rmsd(self.rigid2, atsel), 0)

    def testTranslation1(self):
        CoM1 = self.rigid1.find_center()
        self.rigid1.translate(Coord3D(3.0, -55.67, 1))
        CoM2 = self.rigid1.find_center()
        diff = CoM2 - CoM1
        self.assertAlmostEqual(norm2(diff + Coord3D(-3.0, 55.67, -1.0)), 0.0)
        self.rigid1.translate(Coord3D(-3.0, 55.67, -1.0))   # translate back
        self.assertAlmostEqual(rmsd(self.rigid1, self.rigid2), 0.0)

    def testTranslation2(self):
        vec1 = Coord3D(-123.54, 45.62, -99.003)
        vec2 = Coord3D(36.3125, 2.78, -36.378)
        self.rigid2.translate(vec1 + vec2)
        self.rigid2.translate(vec1 - vec2)
        self.rigid2.translate(Coord3D() - 2 * vec1)  # should be a global null translation + round error
        self.assertAlmostEqual(rmsd(self.rigid2, self.rigid3), 0)


class TestRotations(unittest.TestCase):
    def setUp(self):
        at1 = Atom(Atomproperty(), Coord3D(1, 0, 0))
        at2 = Atom(Atomproperty(), Coord3D(0, 1, 0))
        at3 = Atom(Atomproperty(), Coord3D(0, 0, 1))
        at4 = Atom(Atomproperty(), Coord3D(1, 1, 1))

        rig = Rigidbody()
        rig.add_atom(at1)
        rig.add_atom(at2)
        rig.add_atom(at3)
        rig.add_atom(at4)

        self.rig = rig

    def testRotZ(self):
        self.rig.ab_rotate(Coord3D(0, 0, 0), Coord3D(0, 0, 1), math.pi / 2)
        # i should now be j
        co1 = self.rig.copy_atom(0).coords
        self.assertAlmostEqual(co1.x, 0)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 1)

        # j becomes -i
        co2 = self.rig.copy_atom(1).coords
        self.assertAlmostEqual(co2.x, -1)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 0)

        # k is still k:
        co3 = self.rig.copy_atom(2).coords
        self.assertAlmostEqual(co3.x, 0)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 1)

    def testRotX(self):
        self.rig.ab_rotate(Coord3D(0, 0, 0), Coord3D(1, 0, 0), math.pi / 2)

        # i is still i
        co1 = self.rig.copy_atom(0).coords
        self.assertAlmostEqual(co1.x, 1)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 0)

        # j becomes k
        co2 = self.rig.copy_atom(1).coords
        self.assertAlmostEqual(co2.x, 0)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 1)

        # k becomes -j
        co3 = self.rig.copy_atom(2).coords
        self.assertAlmostEqual(co3.x, 0)
        self.assertAlmostEqual(co3.y, -1)
        self.assertAlmostEqual(co3.z, 0)

    def testRotY(self):
        self.rig.ab_rotate(Coord3D(0, 0, 0), Coord3D(0, 1, 0), math.pi / 2)

        # i becomes -j
        co1 = self.rig.copy_atom(0).coords
        self.assertAlmostEqual(co1.x, 0)
        self.assertAlmostEqual(co1.z, -1)
        self.assertAlmostEqual(co1.y, 0)

        # j is still j
        co2 = self.rig.copy_atom(1).coords
        self.assertAlmostEqual(co2.x, 0)
        self.assertAlmostEqual(co2.y, 1)
        self.assertAlmostEqual(co2.z, 0)

        # k becomes i
        co3 = self.rig.copy_atom(2).coords
        self.assertAlmostEqual(co3.x, 1)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 0)

    def testRotZ_trans(self):
        self.rig.ab_rotate(Coord3D(1, 1, 1), Coord3D(1, 1, 3), math.pi / 2)

        co1 = self.rig.copy_atom(0).coords
        self.assertAlmostEqual(co1.x, 2)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 1)

        co2 = self.rig.copy_atom(1).coords
        self.assertAlmostEqual(co2.x, 1)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 0)

        co3 = self.rig.copy_atom(2).coords
        self.assertAlmostEqual(co3.x, 2)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 1)

        co4 = self.rig.copy_atom(3).coords
        self.assertAlmostEqual(co4.x, 1)
        self.assertAlmostEqual(co4.y, 1)
        self.assertAlmostEqual(co4.z, 1)


if __name__ == '__main__':
    unittest.main()
