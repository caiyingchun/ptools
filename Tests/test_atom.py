
import unittest

from ptools import Atom, Atomproperty, Coord3D


class TestAtomBindings(unittest.TestCase):

    def test_Atom_has_atom_type(self):
        self.assertTrue(hasattr(Atom, 'atom_type'))

    def test_Atom_has_resid_type(self):
        self.assertTrue(hasattr(Atom, 'resid_type'))

    def test_Atom_has_resid_id(self):
        self.assertTrue(hasattr(Atom, 'resid_id'))

    def test_Atom_has_atom_id(self):
        self.assertTrue(hasattr(Atom, 'atom_id'))

    def test_Atom_has_atom_charge(self):
        self.assertTrue(hasattr(Atom, 'atom_charge'))

    def test_Atom_has_atom_element(self):
        self.assertTrue(hasattr(Atom, 'atom_element'))

    def test_Atom_has_coords(self):
        self.assertTrue(hasattr(Atom, 'coords'))

    def test_Atom_has_set_coords(self):
        self.assertTrue(hasattr(Atom, 'set_coords'))

    def test_Atom_has_chain_id(self):
        self.assertTrue(hasattr(Atom, 'chain_id'))



class TestAtom(unittest.TestCase):
    def setUp(self):
        self.atom = Atom(Atomproperty(), Coord3D(1, 2, 3))

    def test_get_atom_type(self):
        self.assertEqual(self.atom.atom_type, 'X')

    def test_set_atom_type(self):
        self.atom.atom_type = 'A'
        self.assertEqual(self.atom.atom_type, 'A')

    def test_get_atom_element(self):
        self.assertEqual(self.atom.atom_element, 'X')

    def test_set_atom_element(self):
        self.atom.atom_element = 'A'
        self.assertEqual(self.atom.atom_element, 'A')

    def test_get_atom_chain_id(self):
        self.assertEqual(self.atom.chain_id, 'X')

    def test_set_atom_chain_id(self):
        self.atom.chain_id = 'XXX'
        self.assertEqual(self.atom.chain_id, 'XXX')

    def test_get_resid_type(self):
        self.assertEqual(self.atom.resid_type, 'XXX')

    def test_set_resid_type(self):
        self.atom.resid_type = 'AAA'
        self.assertEqual(self.atom.resid_type, 'AAA')

    def test_get_resid_id(self):
        self.assertEqual(self.atom.resid_id, 1)

    def test_set_resid_id(self):
        self.atom.resid_id = 123
        self.assertEqual(self.atom.resid_id, 123)

    def test_get_atom_id(self):
        self.assertEqual(self.atom.atom_id, 1)

    def test_set_atom_id(self):
        self.atom.atom_id = 123
        self.assertEqual(self.atom.atom_id, 123)

    def test_get_atom_charge(self):
        self.assertAlmostEqual(self.atom.atom_charge, 0.0)

    def test_set_atom_charge(self):
        self.atom.atom_charge = 123.2
        self.assertAlmostEqual(self.atom.atom_charge, 123.2)

    def test_set_negative_resid_id(self):
        self.atom.resid_id = -5
        self.assertEqual(self.atom.resid_id, -5)

    def test_get_coords(self):
        self.assertAlmostEqual(self.atom.coords.x, 1.)
        self.assertAlmostEqual(self.atom.coords.y, 2.)
        self.assertAlmostEqual(self.atom.coords.z, 3.)

    def test_set_coords(self):
        self.atom.coords = Coord3D(-12, 12, 17)
        self.assertAlmostEqual(self.atom.coords.x, -12)
        self.assertAlmostEqual(self.atom.coords.y, 12)
        self.assertAlmostEqual(self.atom.coords.z, 17)

    def test_set_coords_with_method(self):
        self.atom.set_coords(Coord3D(-12, 12, 17))
        self.assertAlmostEqual(self.atom.coords.x, -12)
        self.assertAlmostEqual(self.atom.coords.y, 12)
        self.assertAlmostEqual(self.atom.coords.z, 17)


if __name__ == '__main__':
    unittest.main()
