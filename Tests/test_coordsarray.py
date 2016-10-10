
import unittest

from ptools import CoordsArray, Coord3D

from . import assertCoordsAlmostEqual


class TestCoordsArray(unittest.TestCase):
    def setUp(self):
        c = CoordsArray()
        coo1 = Coord3D(3.0, 4.0, 5.0)
        coo2 = Coord3D(1.0, 2.0, 7.5)

        c.AddCoord(coo1)
        c.AddCoord(coo2)
        self.c = c
        self.tr = Coord3D(3.0, 4.5, -3.0)

    def testSize(self):
        self.assertEqual(len(self.c), 2)

    def testGetAtom(self):
        c1 = Coord3D()
        self.c.GetCoords(0, c1)
        assertCoordsAlmostEqual(self, c1, Coord3D(3.0, 4.0, 5.0))

    def testBasicTranslation(self):
        self.c.Translate(self.tr)
        c1 = Coord3D()
        c2 = Coord3D()
        self.c.GetCoords(0, c1)
        self.c.GetCoords(1, c2)
        assertCoordsAlmostEqual(self, c1, Coord3D(6.0, 8.5, 2.0))

    def testSetCoords(self):
        """brief explanation:
        For lazy evaluation, corrdinates are stored unrotated/untranslated
        along with the rotation/translation 4x4 matrix.
        When user set the coordinates, this means: 'change the current
        coordinates of atom i' and not 'change the initial coordinates of
        atom i' so here we check that this is the case"""
        self.c.Translate(self.tr)  # do some translation
        self.c.AttractEulerRotate(2.0, 4.0, 5.0)  # do a rotation
        co = Coord3D(3, 2, 1)  # new coordinates to be added
        self.c.SetCoords(0, co)
        co2 = Coord3D()
        self.c.GetCoords(0, co2)  # get the coordinates back
        assertCoordsAlmostEqual(self, co, co2)


if __name__ == '__main__':
    unittest.main()
