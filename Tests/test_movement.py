
import math
import unittest

import ptools

"""test_movement -- unit test for Movement.h."""


class TestMovementBindings(unittest.TestCase):

    def test_has_Movement(self):
        self.assertTrue(hasattr(ptools, 'Movement'))

    def test_has_Shift(self):
        self.assertTrue(hasattr(ptools, 'Shift'))

    def test_has_Slide(self):
        self.assertTrue(hasattr(ptools, 'Slide'))

    def test_has_Rise(self):
        self.assertTrue(hasattr(ptools, 'Rise'))

    def test_has_Twist(self):
        self.assertTrue(hasattr(ptools, 'Twist'))

    def test_has_Roll(self):
        self.assertTrue(hasattr(ptools, 'Roll'))

    def test_has_Tilt(self):
        self.assertTrue(hasattr(ptools, 'Tilt'))

    def test_has_ADNA(self):
        self.assertTrue(hasattr(ptools, 'ADNA'))

    def test_has_BDNA(self):
        self.assertTrue(hasattr(ptools, 'BDNA'))


class MatrixAssertions:
    # Floatting points numbers are tested to be equal at a precision of 1E-6.
    ALMOST_EQUAL_DECIMAL = 6

    def assertIsSquare(self, source, n=0):
        """Assert that a matrix is square.

        If `n` > 0, check the dimension of the matrix is `n`.
        """
        nrow = len(source)
        ncol = len(source[0])
        if nrow != ncol:
            err = 'matrix is not square (dims are ({},{})'.format(nrow, ncol)
            raise AssertionError(err)
        if n > 0 and nrow != n:
            err = 'matrix is not {1}x{1} (dims are ({2},{2})'.format(n, nrow)
            raise AssertionError(err)

    def assertSameDimensions(self, source, target):
        """Assert that two matrices have the same dimensions."""
        nrow = len(source)
        ncol = len(source[0])
        if nrow != len(target) or ncol != len(target[0]):
            err = 'matrices do not have the same dimensions: ({},{}) != ({},{})'
            err = err.format(nrow, ncol, len(target), len(target[0]))
            raise AssertionError(err)

    def assertMatrixAlmostEqual(self, source, target):
        """Assert that two square matrices elements are almost equal."""
        self.assertSameDimensions(source, target)
        nrow, ncol = len(source), len(source[0])
        for i in xrange(nrow):
            for j in xrange(ncol):
                if round(source[i][j] - target[i][j], self.ALMOST_EQUAL_DECIMAL) != 0:
                    err = 'matrix differs on element at ({},{}): {} != {}'
                    err = err.format(i, j, source[i][j], target[i][j])
                    raise AssertionError(err)


class TestMovement(unittest.TestCase, MatrixAssertions):

    def setUp(self):
        self.alpha = 12
        self.ralpha = math.radians(self.alpha)
        self.target = identity(4)

    def test_Movement(self):
        mov = ptools.Movement()
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), zeros(4, 4))

    def test_Shift(self):
        mov = ptools.Shift(self.alpha)
        self.target[0][3] = self.alpha
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_Slide(self):
        mov = ptools.Slide(self.alpha)
        self.target[1][3] = self.alpha
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_Rise(self):
        mov = ptools.Rise(self.alpha)
        self.target[2][3] = self.alpha
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_Twist(self):
        mov = ptools.Twist(self.alpha)
        self.target[0][0] = math.cos(self.ralpha)
        self.target[0][1] = -math.sin(self.ralpha)
        self.target[1][0] = math.sin(self.ralpha)
        self.target[1][1] = math.cos(self.ralpha)
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_Roll(self):
        mov = ptools.Roll(self.alpha)
        self.target[0][0] = math.cos(self.ralpha)
        self.target[0][2] = math.sin(self.ralpha)
        self.target[2][0] = -math.sin(self.ralpha)
        self.target[2][2] = math.cos(self.ralpha)
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_Tilt(self):
        mov = ptools.Tilt(self.alpha)
        self.target[1][1] = math.cos(self.ralpha)
        self.target[1][2] = -math.sin(self.ralpha)
        self.target[2][1] = math.sin(self.ralpha)
        self.target[2][2] = math.cos(self.ralpha)
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_ADNA(self):
        mov = ptools.ADNA(self.alpha)
        self.target = [[ 0.8555460,    -0.515319,    0.0498794,    0.940426],
                       [ 0.5164770,     0.856201,   -0.0131009,   -2.391840],
                       [-0.0359557,     0.036970,    0.9986690,    3.305990],
                       [ 0.0000000,     0.0000000,   0.0000000,    1.000000]]
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)

    def test_BDNA(self):
        mov = ptools.ADNA(self.alpha)
        self.target = [[ 0.8555460,    -0.515319,    0.0498794,    0.940426],
                       [ 0.5164770,     0.856201,   -0.0131009,   -2.391840],
                       [-0.0359557,     0.036970,    0.9986690,    3.305990],
                       [ 0.0000000,     0.0000000,   0.0000000,    1.000000]]
        self.assertMatrixAlmostEqual(get_movement_matrix(mov), self.target)


def zeros(n, m):
    """Return a matrix of dimension `n`x`m` filled with zeros."""
    return [[0 for i in xrange(m)] for j in xrange(n)]


def identity(n):
    """Return an identity matrix of dimension `n`."""
    m = zeros(n, n)
    m[0][0] = m[1][1] = m[2][2] = m[3][3] = 1
    return m


def get_movement_matrix(mov):
    """Return a Movement matrix."""
    return string_to_matrix(mov.toString())


def string_to_matrix(s):
    """Convert a string to a matrix (list of list) or floats."""
    return [[float(tok) for tok in line.split()] for line in s.splitlines()]
        

def print_movement(mov, indent=0):
    """Print a movement on stdout."""
    print_matrix(get_movement_matrix(mov), indent)


def print_matrix(m, indent=0):
    """Print a matrix on stdout."""
    for row in m:
        print ' ' * indent + '    '.join(str(col) for col in row)


if __name__ == '__main__':
    unittest.main()
