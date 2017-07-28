
import unittest

from ptools import Atom, Atomproperty, Coord3D


class TestAtomBindings(unittest.TestCase):

    def test_atom_has_atomType(self):
        self.assertTrue(hasattr(Atom, 'atomType'))

    def test_atom_has_residType(self):
        self.assertTrue(hasattr(Atom, 'residType'))

    def test_atom_has_residId(self):
        self.assertTrue(hasattr(Atom, 'residId'))

    def test_atom_has_atomId(self):
        self.assertTrue(hasattr(Atom, 'atomId'))

    def test_atom_has_atomCharge(self):
        self.assertTrue(hasattr(Atom, 'atomCharge'))

    def test_atom_has_atomElement(self):
        self.assertTrue(hasattr(Atom, 'atomElement'))

    def test_atom_has_coords(self):
        self.assertTrue(hasattr(Atom, 'coords'))

    def test_atom_has_set_coords(self):
        self.assertTrue(hasattr(Atom, 'set_coords'))


class TestAtom(unittest.TestCase):
    def setUp(self):
        self.atom = Atom(Atomproperty(), Coord3D(1, 2, 3))

    def test_get_atomType(self):
        self.assertEqual(self.atom.atomType, 'X')

    def test_set_atomType(self):
        self.atom.atomType = 'A'
        self.assertEqual(self.atom.atomType, 'A')

    def test_get_atomElement(self):
        self.assertEqual(self.atom.atomElement, 'X')

    def test_set_atomElement(self):
        self.atom.atomElement = 'A'
        self.assertEqual(self.atom.atomElement, 'A')

    def test_get_residType(self):
        self.assertEqual(self.atom.residType, 'XXX')

    def test_set_residType(self):
        self.atom.residType = 'AAA'
        self.assertEqual(self.atom.residType, 'AAA')

    def test_get_residId(self):
        self.assertEqual(self.atom.residId, 1)

    def test_set_residId(self):
        self.atom.residId = 123
        self.assertEqual(self.atom.residId, 123)

    def test_get_atomId(self):
        self.assertEqual(self.atom.atomId, 1)

    def test_set_atomId(self):
        self.atom.atomId = 123
        self.assertEqual(self.atom.atomId, 123)

    def test_get_atomCharge(self):
        self.assertAlmostEqual(self.atom.atomCharge, 0.0)

    def test_set_atomCharge(self):
        self.atom.atomCharge = 123.2
        self.assertAlmostEqual(self.atom.atomCharge, 123.2)

    def test_set_negative_residId(self):
        self.atom.residId = -5
        self.assertEqual(self.atom.residId, -5)

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
