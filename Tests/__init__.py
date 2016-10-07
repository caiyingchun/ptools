
import sys

from ptools import norm2


def assertCoordsAlmostEqual(testcase, source, target):
    """Assert that two `ptools.Coord3D` instances are almost equal.

    The comparison method differs between Python 2.6 and Python 2.7,
    which is why this function is required.

    Args:
        testcase (unittest.TestCase): provides regular
            `testcase.assertAlmostEqual` method
        source (ptools.Coord3D): tested coordinates
        target (ptools.Coord3D): reference coordinates
    """
    if sys.version_info < (2, 7):
        testcase.assertAlmostEqual(source, target)
    else:
        testcase.assertAlmostEqual(norm2(source - target), 0.0)
