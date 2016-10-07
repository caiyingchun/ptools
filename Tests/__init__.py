
import sys

from ptools import norm2


def assertCoordsAlmostEqual(testcase, source, target):
    """Assert that two `ptools.Coord3D` instances are almost equal.

    Args:
        testcase (unittest.TestCase): provides regular
            `testcase.assertAlmostEqual` method
        source (ptools.Coord3D): tested coordinates
        target (ptools.Coord3D): reference coordinates
    """
   testcase.assertAlmostEqual(norm2(source - target), 0.0)
