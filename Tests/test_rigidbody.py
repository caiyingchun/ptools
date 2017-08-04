
import os
import unittest

from ptools import Rigidbody, Coord3D, Atom, Atomproperty

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

    def test_Rigidbody_has_get_coords(self):
        self.assertTrue(hasattr(Rigidbody, 'get_coords'))

    def test_Rigidbody_has_unsafeget_coords(self):
        self.assertTrue(hasattr(Rigidbody, 'unsafeget_coords'))

    def test_Rigidbody_has_set_coords(self):
        self.assertTrue(hasattr(Rigidbody, 'set_coords'))

    def test_Rigidbody_has_translate(self):
        self.assertTrue(hasattr(Rigidbody, 'translate'))

    def test_Rigidbody_has_find_center(self):
        self.assertTrue(hasattr(Rigidbody, 'find_center'))

    def test_Rigidbody_has_rotate(self):
        self.assertTrue(hasattr(Rigidbody, 'rotate'))

    def test_Rigidbody_has_euler_rotate(self):
        self.assertTrue(hasattr(Rigidbody, 'euler_rotate'))

    def test_Rigidbody_has_sync_coords(self):
        self.assertTrue(hasattr(Rigidbody, 'sync_coords'))

    def test_Rigidbody_has_apply_matrix(self):
        self.assertTrue(hasattr(Rigidbody, 'apply_matrix'))

    def test_Rigidbody_has_copy_atom(self):
        self.assertTrue(hasattr(Rigidbody, 'copy_atom'))

    def test_Rigidbody_has_add_atom(self):
        self.assertTrue(hasattr(Rigidbody, 'add_atom'))

    def test_Rigidbody_has_set_atom(self):
        self.assertTrue(hasattr(Rigidbody, 'set_atom'))

    def test_Rigidbody_has_get_atom_property(self):
        self.assertTrue(hasattr(Rigidbody, 'get_atom_property'))

    def test_Rigidbody_has_set_atom_property(self):
        self.assertTrue(hasattr(Rigidbody, 'set_atom_property'))

    def test_Rigidbody_has_radius(self):
        self.assertTrue(hasattr(Rigidbody, 'radius'))

    def test_Rigidbody_has_radius_of_gyration(self):
        self.assertTrue(hasattr(Rigidbody, 'radius_of_gyration'))

    def test_Rigidbody_has_select_all_atoms(self):
        self.assertTrue(hasattr(Rigidbody, 'select_all_atoms'))

    def test_Rigidbody_has_select_atomtype(self):
        self.assertTrue(hasattr(Rigidbody, 'select_atomtype'))

    def test_Rigidbody_has_select_restype(self):
        self.assertTrue(hasattr(Rigidbody, 'select_restype'))

    def test_Rigidbody_has_select_chainid(self):
        self.assertTrue(hasattr(Rigidbody, 'select_chainid'))

    def test_Rigidbody_has_select_resid_range(self):
        self.assertTrue(hasattr(Rigidbody, 'select_resid_range'))

    def test_Rigidbody_has_get_CA(self):
        self.assertTrue(hasattr(Rigidbody, 'get_CA'))

    def test_Rigidbody_has_backbone(self):
        self.assertTrue(hasattr(Rigidbody, 'backbone'))

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
        self.r2.add_atom(at)
        at.coords = Coord3D(0, 1, 0)
        self.r2.add_atom(at)
        at.coords = Coord3D(0, 0, 1)
        self.r2.add_atom(at)

    def test_copy(self):
        s = Rigidbody(self.r)
        self.assertEqual(len(s), len(self.r))
        self.assertEqual(self.r.find_center(), s.find_center())

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
        self.assertFalse(coordinates_equal(origin, self.r.find_center()))  # assertEqual won't work
        self.r.center_to_origin()
        self.assertTrue(coordinates_equal(origin, self.r.find_center()))  # assertEqual won't work

    def testcopy_atom(self):
        atom = self.r.copy_atom(3)
        coords = atom.coords
        assertCoordsAlmostEqual(self, coords, Coord3D(-16.159, 189.782, 106.402))
        self.assertEqual(atom.atomId, 4)
        self.assertEqual(atom.chainId, '')

    def testget_coords(self):
        coords = self.r.get_coords(3)
        assertCoordsAlmostEqual(self, coords, Coord3D(-16.159, 189.782, 106.402))

    def testtranslate(self):
        tr = Coord3D(3.2, 2.98, 14.22)
        s = Rigidbody(self.r)
        s.translate(tr)
        coords = s.get_coords(3)
        ref = Coord3D(-16.159 + 3.2, 189.782 + 2.98, 106.402 + 14.22)
        assertCoordsAlmostEqual(self, coords, ref)

    def testfind_center(self):
        cen = self.r.find_center()
        ref = Coord3D(-20.171249, 215.498060, 119.427781)
        assertCoordsAlmostEqual(self, cen, ref)

    def testset_atom(self):
        atom = self.r.copy_atom(3)
        atom.coords = Coord3D(3, 4, 5)
        self.r.set_atom(3, atom)
        # test to see if the mofification worked:
        atom2 = self.r.copy_atom(3)
        coords2 = atom2.coords
        assertCoordsAlmostEqual(self, atom2.coords, Coord3D(3, 4, 5))
        assertCoordsAlmostEqual(self, coords2, Coord3D(3, 4, 5))

    def testset_atom_with_out_of_bounds_position(self):
        maxpos = len(self.r) - 1
        with self.assertRaisesRegexp(IndexError, 'out of bounds'):
            self.r.set_atom_property(maxpos + 1, Atom())

    def testset_atom_with_negative_position(self):
        with self.assertRaisesRegexp(OverflowError, "can't convert negative value to unsigned int"):
            self.r.set_atom_property(-1, Atom())

    def test_unsafe_get_coords(self):
        """in principle get_coords(i,co) and unsafeget_coords(i,co) should
        lead to the exact same coordinates if a sync has been done before
        calling the 'unsafe' version"""
        r2 = Rigidbody(TEST_LIGAND_PDB)
        A = Coord3D(4.23, 5.72, 99.02)
        B = Coord3D(1.23, 6.33, 1.234)
        self.r.rotate(A, B, 2.2345)
        r2.rotate(A, B, 2.2345)
        self.r.translate(Coord3D(34.23, 123.45, 11.972))
        r2.translate(Coord3D(34.23, 123.45, 11.972))

        r2.sync_coords()
        # same rotation and translation for r and r2: should have exact
        # same coordinates
        for i in range(len(self.r)):
            co1 = Coord3D()
            co2 = Coord3D()
            co1 = self.r.get_coords(i)
            r2.unsafeget_coords(i, co2)
            assertCoordsAlmostEqual(self, co1, co2)

    def testadd_atoms(self):
        r = Rigidbody()
        self.assertEqual(len(r), 0)
        at = Atom()
        at.coords = Coord3D(2, 3, 4)
        r.add_atom(at)
        self.assertAlmostEqual(len(r), 1)

    def testget_atom_property(self):
        atprop = self.r.get_atom_property(8)
        self.assertEqual(atprop.residType, 'GLU')
        self.assertEqual(atprop.residId, 2)
        self.assertEqual(atprop.atomId, 9)

    def testset_atom_property(self):
        prop = Atomproperty()
        prop.residType = 'AAA'
        self.r.set_atom_property(0, prop)
        prop = self.r.get_atom_property(0)
        self.assertEqual(prop.residType, 'AAA')

    def test_set_atom_property_with_out_of_bounds_position(self):
        maxpos = len(self.r) - 1
        with self.assertRaisesRegexp(IndexError, 'out of bounds'):
            self.r.set_atom_property(maxpos + 1, Atomproperty())

    def test_set_atom_property_with_negative_position(self):
        with self.assertRaisesRegexp(OverflowError, "can't convert negative value to unsigned int"):
            self.r.set_atom_property(-1, Atomproperty())

    def test_negative_residId(self):
        rigid = Rigidbody(TEST_2AAV_PDB)
        at1 = rigid.copy_atom(0)
        self.assertEqual(at1.residId, -4)


if __name__ == '__main__':
    unittest.main()
