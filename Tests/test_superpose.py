

from __future__ import print_function

import random
import unittest

import ptools

from . import assertCoordsAlmostEqual
from . import TEST_LIGAND_PDB


class TestSuperposeBindings(unittest.TestCase):

    def test_ptools_has_superpose(self):
        self.assertTrue(hasattr(ptools, 'superpose'))

    def test_ptools_has_MatTrans2screw(self):
        self.assertTrue(hasattr(ptools, 'MatTrans2screw'))


class TestMatTrans2screw(unittest.TestCase):
    def test_MatTrans2screw(self):
        m = ptools.Matrix(3, 3)  # Initialize 3 x 3 matrix
        s = ptools.MatTrans2screw(m)
        self.assertTrue(isinstance(s, ptools.Screw))

        self.assertAlmostEqual(s.angle, 1.57079632679)
        self.assertAlmostEqual(s.normtranslation, 0.0)
        assertCoordsAlmostEqual(self, s.unitVector, ptools.Coord3D(1.0, 0.0, 0.0))
        assertCoordsAlmostEqual(self, s.point, ptools.Coord3D(0.0, 0.0, 0.0))


class TestSuperposition(unittest.TestCase):
    def setUp(self):
        self.prot1 = ptools.Rigidbody(TEST_LIGAND_PDB)

    def testTransRot(self):
        prot2 = ptools.Rigidbody(self.prot1)

        for i in xrange(20):
            # random translation coordinates:
            x = (random.random() - 0.5) * 50.0
            y = (random.random() - 0.5) * 50.0
            z = (random.random() - 0.5) * 50.0
            prot2.translate(ptools.Coord3D(x, y, z))
            a = (random.random() - 0.5) * 50.0
            b = (random.random() - 0.5) * 50.0
            c = (random.random() - 0.5) * 50.0
            prot2.attract_euler_rotate(a, b, c)

            sup = ptools.superpose(self.prot1, prot2)  # superpose(reference, mobile)
            matrix = sup.matrix
            prot2.apply_matrix(matrix)
            self.assertAlmostEqual(ptools.Rmsd(prot2, self.prot1), 0.0)


if __name__ == '__main__':
    unittest.main()
