
import sys

from ptools import norm2


def assertCoordsAlmostEqual(testcase, source, target, places=6):
    """Assert that two `ptools.Coord3D` instances are almost equal.

    Args:
        testcase (unittest.TestCase): provides regular
            `testcase.assertAlmostEqual` method
        source (ptools.Coord3D): tested coordinates
        target (ptools.Coord3D): reference coordinates
        places (int): equivalent to unittest.TestCase.assertAlmostEqual
            places argument (see original documentation)
    """
    testcase.assertAlmostEqual(source.x, target.x, places=places)
    testcase.assertAlmostEqual(source.y, target.y, places=places)
    testcase.assertAlmostEqual(source.z, target.z, places=places)
