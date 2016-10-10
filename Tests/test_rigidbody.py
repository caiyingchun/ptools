
import os
import unittest

from ptools import Rigidbody, Coord3D, Atom

from . import assertCoordsAlmostEqual

TEST_1FINR_PDB = os.path.join(os.path.dirname(__file__), 'data', '1FIN_r.pdb')
TEST_2AAV_PDB = os.path.join(os.path.dirname(__file__), 'data', '2AAV.one.pdb')


class TestRigidbody(unittest.TestCase):
    def setUp(self):
        self.r = Rigidbody(TEST_1FINR_PDB)
        self.r2 = Rigidbody()
        at = Atom()
        at.coords = Coord3D(1, 0, 0)
        self.r2.AddAtom(at)
        at.coords = Coord3D(0, 1, 0)
        self.r2.AddAtom(at)
        at.coords = Coord3D(0, 0, 1)
        self.r2.AddAtom(at)

    def testCopy(self):
        s = Rigidbody(self.r)
        self.assertEqual(len(s), len(self.r))
        self.assertEqual(self.r.FindCenter(), s.FindCenter())

    def testSize(self):
        self.assertEqual(len(self.r), 2365)

    def testCopyAtom(self):
        atom = self.r.CopyAtom(3)
        coords = atom.coords
        assertCoordsAlmostEqual(self, coords, Coord3D(-16.159, 189.782, 106.402))
        self.assertEqual(atom.atomId, 4)
        self.assertEqual(atom.chainId, '')

    def testGetCoords(self):
        coords = self.r.getCoords(3)
        assertCoordsAlmostEqual(self, coords, Coord3D(-16.159, 189.782, 106.402))

    def testTranslate(self):
        tr = Coord3D(3.2, 2.98, 14.22)
        s = Rigidbody(self.r)
        s.Translate(tr)
        coords = s.getCoords(3)
        ref = Coord3D(-16.159 + 3.2, 189.782 + 2.98, 106.402 + 14.22)
        assertCoordsAlmostEqual(self, coords, ref)

    def testFindCenter(self):
        cen = self.r.FindCenter()
        ref = Coord3D(-20.171249, 215.498060, 119.427781)
        assertCoordsAlmostEqual(self, cen, ref)

    def testSetAtom(self):
        atom = self.r.CopyAtom(3)
        atom.coords = Coord3D(3, 4, 5)
        self.r.SetAtom(3, atom)
        # test to see if the mofification worked:
        atom2 = self.r.CopyAtom(3)
        coords2 = atom2.coords
        assertCoordsAlmostEqual(self, atom2.coords, Coord3D(3, 4, 5))
        assertCoordsAlmostEqual(self, coords2, Coord3D(3, 4, 5))

    def testUnsafeGetCoords(self):
        """in principle GetCoords(i,co) and unsafeGetCoords(i,co) should
        lead to the exact same coordinates if a sync has been done before
        calling the 'unsafe' version"""
        r2 = Rigidbody(TEST_1FINR_PDB)
        A = Coord3D(4.23, 5.72, 99.02)
        B = Coord3D(1.23, 6.33, 1.234)
        self.r.ABrotate(A, B, 2.2345)
        r2.ABrotate(A, B, 2.2345)
        self.r.Translate(Coord3D(34.23, 123.45, 11.972))
        r2.Translate(Coord3D(34.23, 123.45, 11.972))

        r2.syncCoords()
        # same rotation and translation for r and r2: should have exact
        # same coordinates
        for i in range(len(self.r)):
            co1 = Coord3D()
            co2 = Coord3D()
            co1 = self.r.getCoords(i)
            r2.unsafeGetCoords(i, co2)
            assertCoordsAlmostEqual(self, co1, co2)

    def testAddAtoms(self):
        r = Rigidbody()
        self.assertEqual(len(r), 0)
        at = Atom()
        at.coords = Coord3D(2, 3, 4)
        r.AddAtom(at)
        self.assertAlmostEqual(len(r), 1)

    def testGetAtomProperty(self):
        atprop = self.r.GetAtomProperty(8)
        self.assertEqual(atprop.residType, 'GLU')
        self.assertEqual(atprop.residId, 2)
        self.assertEqual(atprop.atomId, 9)

    def testNegativeResId(self):
        rigid = Rigidbody(TEST_2AAV_PDB)
        at1 = rigid.CopyAtom(0)
        self.assertEqual(at1.residId, -4)


if __name__ == '__main__':
    unittest.main()
