
import unittest

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


if __name__ == '__main__':
    unittest.main()
