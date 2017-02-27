
import random
import sys
import unittest

import ptools

from . import assertCoordsAlmostEqual
from . import TEST_LIGAND_PDB


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


class TestSuperposeBindings(unittest.TestCase):

    def test_ptools_has_superpose(self):
        self.assertTrue(hasattr(ptools, 'superpose'))


class TestSuperposition(unittest.TestCase):
    def setUp(self):
        self.prot1 = ptools.Rigidbody(TEST_LIGAND_PDB)
        random.seed(123)

    def testTransRot(self):
        prot2 = ptools.Rigidbody(self.prot1)

        for i in xrange(20):
            # random translation coordinates:
            x = (random.random() - 0.5) * 50.0
            y = (random.random() - 0.5) * 50.0
            z = (random.random() - 0.5) * 50.0
            prot2.Translate(ptools.Coord3D(x, y, z))
            a = (random.random() - 0.5) * 50.0
            b = (random.random() - 0.5) * 50.0
            c = (random.random() - 0.5) * 50.0
            prot2.AttractEulerRotate(a, b, c)

            sup = ptools.superpose(self.prot1, prot2)  # superpose(reference, mobile)
            matrix = sup.matrix
            prot2.ApplyMatrix(matrix)
            self.assertAlmostEqual(ptools.Rmsd(prot2, self.prot1), 0.0)



def random_float():
    """Return a random floatting point number in the range
    [-max_float; +max_float]."""
    max_float = sys.float_info.max
    return random.randrange(-max_float, +max_float)



if __name__ == '__main__':
    unittest.main()
