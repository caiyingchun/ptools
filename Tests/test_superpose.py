
import random
import unittest

import ptools
# from ptools import Rigidbody, Coord3D, superpose, Rmsd

from . import TEST_LIGAND_PDB



class TestScrewBindings(unittest.TestCase):

    def test_ptools_has_Screw(self):
        self.assertTrue(hasattr(ptools, 'Screw'))


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


if __name__ == '__main__':
    unittest.main()
