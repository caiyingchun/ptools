
import os
import unittest

from ptools import Rigidbody, Coord3D, Atom

from . import TEST_LIGAND_PDB
from . import assertCoordsAlmostEqual


TEST_2AAV_PDB = os.path.join(os.path.dirname(__file__), 'data', '2AAV.one.pdb')


class TestRigidbodyBindings(unittest.TestCase):

    def test_ptools_has_rigidbody(self):
        import ptools
        self.assertTrue(hasattr(ptools, 'Rigidbody'))

    def test_Rigidbody_has_len(self):
        self.assertTrue(hasattr(Rigidbody, '__len__'))

    def test_Rigidbody_has_size(self):
        self.assertTrue(hasattr(Rigidbody, 'size'))

    def test_Rigidbody_has_getCoords(self):
        self.assertTrue(hasattr(Rigidbody, 'getCoords'))

    def test_Rigidbody_has_unsafeGetCoords(self):
        self.assertTrue(hasattr(Rigidbody, 'unsafeGetCoords'))

    def test_Rigidbody_has_setCoords(self):
        self.assertTrue(hasattr(Rigidbody, 'setCoords'))

    def test_Rigidbody_has_Translate(self):
        self.assertTrue(hasattr(Rigidbody, 'Translate'))

    def test_Rigidbody_has_FindCenter(self):
        self.assertTrue(hasattr(Rigidbody, 'FindCenter'))

    def test_Rigidbody_has_ABrotate(self):
        self.assertTrue(hasattr(Rigidbody, 'ABrotate'))

    def test_Rigidbody_has_AttractEulerRotate(self):
        self.assertTrue(hasattr(Rigidbody, 'AttractEulerRotate'))

    def test_Rigidbody_has_syncCoords(self):
        self.assertTrue(hasattr(Rigidbody, 'syncCoords'))

    def test_Rigidbody_has_apply_matrix(self):
        self.assertTrue(hasattr(Rigidbody, 'apply_matrix'))

    def test_Rigidbody_has_CopyAtom(self):
        self.assertTrue(hasattr(Rigidbody, 'CopyAtom'))

    def test_Rigidbody_has_AddAtom(self):
        self.assertTrue(hasattr(Rigidbody, 'AddAtom'))

    def test_Rigidbody_has_SetAtom(self):
        self.assertTrue(hasattr(Rigidbody, 'SetAtom'))

    def test_Rigidbody_has_GetAtomProperty(self):
        self.assertTrue(hasattr(Rigidbody, 'GetAtomProperty'))

    def test_Rigidbody_has_Radius(self):
        self.assertTrue(hasattr(Rigidbody, 'Radius'))

    def test_Rigidbody_has_RadiusGyration(self):
        self.assertTrue(hasattr(Rigidbody, 'RadiusGyration'))

    def test_Rigidbody_has_SelectAllAtoms(self):
        self.assertTrue(hasattr(Rigidbody, 'SelectAllAtoms'))

    def test_Rigidbody_has_SelectAtomType(self):
        self.assertTrue(hasattr(Rigidbody, 'SelectAtomType'))

    def test_Rigidbody_has_SelectResidType(self):
        self.assertTrue(hasattr(Rigidbody, 'SelectResidType'))

    def test_Rigidbody_has_SelectChainId(self):
        self.assertTrue(hasattr(Rigidbody, 'SelectChainId'))

    def test_Rigidbody_has_SelectResRange(self):
        self.assertTrue(hasattr(Rigidbody, 'SelectResRange'))

    def test_Rigidbody_has_CA(self):
        self.assertTrue(hasattr(Rigidbody, 'CA'))

    def test_Rigidbody_has_Backbone(self):
        self.assertTrue(hasattr(Rigidbody, 'Backbone'))

    def test_has_operator_add(self):
        self.assertTrue(hasattr(Rigidbody, '__add__'))

    def test_has_center_to_origin(self):
        self.assertTrue(hasattr(Rigidbody, 'center_to_origin'))


class TestRigidbody(unittest.TestCase):
    def setUp(self):
        self.r = Rigidbody(TEST_LIGAND_PDB)
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

    def test_len(self):
        self.assertEqual(len(self.r), 2365)

    def test_size(self):
        self.assertEqual(self.r.size(), 2365)

    def test_operator_plus(self):
        r3 = self.r + self.r2
        self.assertTrue(isinstance(r3, Rigidbody))
        self.assertEqual(len(r3), len(self.r) + len(self.r2))

    def test_center_to_origin(self):
        def coordinates_equal(test, ref):
            t = 1e-6
            d = abs(test - ref)
            return d.x < t and d.y < t and d.z < t
        origin = Coord3D(0, 0, 0)
        self.assertFalse(coordinates_equal(origin, self.r.FindCenter()))  # assertEqual won't work
        self.r.center_to_origin()
        self.assertTrue(coordinates_equal(origin, self.r.FindCenter()))  # assertEqual won't work

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
        r2 = Rigidbody(TEST_LIGAND_PDB)
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
