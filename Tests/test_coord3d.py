
import unittest

import ptools
from ptools import Coord3D


class TestCoord3D(unittest.TestCase):
    def setUp(self):
        self.coo1 = Coord3D(3.0, 4.0, 5.0)
        self.coo2 = Coord3D(1.0, 2.0, 7.5)

    def test_plus_operator(self):
        coo3 = self.coo1 + self.coo2
        self.assertEqual(coo3.x, 4.0)
        self.assertEqual(coo3.y, 6.0)
        self.assertEqual(coo3.z, 12.5)

    def test_minus_operator(self):
        coo3 = self.coo1 - self.coo2
        self.assertEqual(coo3.x, 2.0)
        self.assertEqual(coo3.y, 2.0)
        self.assertEqual(coo3.z, -2.5)

    def test_plus_equal_operator(self):
        coo3 = Coord3D(self.coo1)
        coo3 += self.coo2
        self.assertEqual(coo3.x, 4.0)
        self.assertEqual(coo3.y, 6.0)
        self.assertEqual(coo3.z, 12.5)

    def test_unary_minus_operator(self):
        coo3 = - self.coo1
        self.assertEqual(coo3.x, -3.0)
        self.assertEqual(coo3.y, -4.0)
        self.assertEqual(coo3.z, -5.0)

    def test_norm(self):
        self.assertAlmostEqual(ptools.norm(self.coo1), 7.0710678118654755)
        self.assertAlmostEqual(ptools.norm(self.coo2), 7.8262379212492643)

    def test_norm2(self):
        self.assertAlmostEqual(ptools.norm2(self.coo1), 7.0710678118654755 ** 2)
        self.assertAlmostEqual(ptools.norm2(self.coo2), 7.8262379212492643 ** 2)

    def test_dotproduct(self):
        res = ptools.dotproduct(self.coo1, self.coo2)
        self.assertAlmostEqual(res, 48.5)

    def test_crossproduct(self):
        res = ptools.crossproduct(self.coo1, self.coo2)
        self.assertAlmostEqual(res.x, 20.)
        self.assertAlmostEqual(res.y, -17.5)
        self.assertAlmostEqual(res.z, 2.)


if __name__ == '__main__':
    unittest.main()
