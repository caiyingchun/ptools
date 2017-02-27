
"""test_screw - Unit tests for ptools.Screw."""

import random
import sys
import unittest

import ptools

from . import assertCoordsAlmostEqual


class TestScrewBindings(unittest.TestCase):

    def test_ptools_has_Screw(self):
        self.assertTrue(hasattr(ptools, 'Screw'))

    def test_Screw_has_attributes(self):
        self.assertTrue(hasattr(ptools.Screw, 'unitVector'))
        self.assertTrue(hasattr(ptools.Screw, 'point'))
        self.assertTrue(hasattr(ptools.Screw, 'normtranslation'))
        self.assertTrue(hasattr(ptools.Screw, 'angle'))


class TestScrew(unittest.TestCase):

    def setUp(self):
        self.s = ptools.Screw()

    def test_get_set_angle(self):
        self.assertEqual(self.s.angle, 0)
        value = random_float()
        self.s.angle = value
        self.assertAlmostEqual(self.s.angle, value)

    def test_get_set_normtranslation(self):
        self.assertEqual(self.s.normtranslation, 0)
        value = random_float()
        self.s.normtranslation = value
        self.assertAlmostEqual(self.s.normtranslation, value)

    def test_get_set_unitVector(self):
        assertCoordsAlmostEqual(self, self.s.unitVector, ptools.Coord3D())
        u = ptools.Coord3D(random_float(), random_float(), random_float())
        self.s.unitVector = u
        assertCoordsAlmostEqual(self, self.s.unitVector, u)

    def test_get_set_point(self):
        assertCoordsAlmostEqual(self, self.s.point, ptools.Coord3D())
        u = ptools.Coord3D(random_float(), random_float(), random_float())
        self.s.point = u
        assertCoordsAlmostEqual(self, self.s.point, u)


def random_float():
    """Return a random floatting point number in the range
    [-max_float; +max_float]."""
    max_float = sys.float_info.max
    return random.randrange(-max_float, +max_float)
