
import random
import sys
import unittest

import pytest

from ptools import cgopt


class TestCgoptBindings(unittest.TestCase):
    """Check that the cgopt module provides required classes and functions."""
    def test_has_optimize(self):
        self.assertTrue(hasattr(cgopt, 'optimize'))


class TestCgopt(unittest.TestCase):
    @pytest.mark.skipif(sys.platform == 'darwin',
                reason="currently not working on OS X")
    def test_optimize(self):
        """This is a very empirical test that only ensures that optimize
        returns the same values as older versions.

        Todo:
            Find a test that checks that optimize calculations are right.
        """
        def random_vector(a, b, size):
            return [random.uniform(a, b) for i in xrange(size)]

        # cgopt.optimize result vector found with seed = 42.
        ref = [-0.7789141972987039, -1.7429578153710739, -1.3981330677053199,
               2.6199275262749637, 0.8882123114795615, 0.6547860340019289,
               -1.973168110811418, 1.3747607877020949, -2.0195850374284294,
               -0.7232673494541135]

        random.seed(42)
        natoms = 10
        charges = random_vector(-3.0, 3.0, natoms)
        radii = random_vector(0.0, 3.0, natoms)
        x = random_vector(-100.0, 100.0, natoms)
        y = random_vector(-100.0, 100.0, natoms)
        z = random_vector(-100.0, 100.0, natoms)

        nbeads = 10
        bcharges = random_vector(-3.0, 3.0, nbeads)
        bradii = random_vector(0.0, 3.0, nbeads)
        bx = random_vector(-100.0, 100.0, nbeads)
        by = random_vector(-100.0, 100.0, nbeads)
        bz = random_vector(-100.0, 100.0, nbeads)

        delgrid = 1.5

        res = cgopt.optimize(natoms, charges, radii, x, y, z,
                             nbeads, bcharges, bradii, bx, by, bz,
                             delgrid)
        
        self.assertEqual(len(ref), len(res))
        self.assertListEqual(ref, res)


if __name__ == '__main__':
    unittest.main()
