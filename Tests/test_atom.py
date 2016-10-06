
import unittest

from ptools import Atom, Atomproperty, Coord3D


class TestAtom(unittest.TestCase):
    def setUp(self):
        co = Coord3D(1, 2, 3)
        atom = Atom(Atomproperty(), co)
        atom.atomType = 'CA'
        # atom.atomElement = 'C'
        atom.residType = 'LEU'
        atom.residId = 6
        atom.atomId = 123
        atom.atomCharge = -1.23456
        self.atom = atom

    def testProperties(self):
        atom = self.atom
        self.assertEqual(atom.atomType, 'CA')
        self.assertEqual(atom.residType, "LEU")
        self.assertEqual(atom.residId, 6)
        self.assertEqual(atom.atomId, 123)
        self.assertEqual(atom.atomCharge, -1.23456)

    def testNegativeResId(self):
        atom = self.atom
        atom.residId = -5
        self.assertEqual(atom.residId, -5)


if __name__ == '__main__':
    unittest.main()
