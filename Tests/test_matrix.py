
"""test_matrix -- unit tests for the Matrix type."""


import unittest

import ptools


class TestMatrixBindings(unittest.TestCase):

    def test_ptools_has_Matrix(self):
        self.assertTrue(hasattr(ptools, 'Matrix'))

    def test_has_detach(self):
        self.assertTrue(hasattr(ptools.Matrix, 'detach'))

    def test_has_str(self):
        self.assertTrue(hasattr(ptools.Matrix, 'str'))
        self.assertTrue(hasattr(ptools.Matrix, '__str__'))

    def test_has_get_nrows(self):
        self.assertTrue(hasattr(ptools.Matrix, 'get_nrows'))

    def test_has_get_ncolumns(self):
        self.assertTrue(hasattr(ptools.Matrix, 'get_ncolumns'))

    def test_has_get_dim(self):
        self.assertTrue(hasattr(ptools.Matrix, 'get_dim'))


class TestMatrix(unittest.TestCase):

    def setUp(self):
        # Initialize a 4 x 4 matrix.
        self.nrows = 2
        self.ncols = 4
        self.mat = ptools.Matrix(self.nrows, self.ncols)

    def test_get_nrows(self):
        self.assertEqual(self.mat.get_nrows(), self.nrows)

    def test_get_columns(self):
        self.assertEqual(self.mat.get_ncolumns(), self.ncols)

    def test_get_dim(self):
        self.assertEqual(self.mat.get_dim(), (self.nrows, self.ncols))

    def test_detach(self):
        # Just check that function call doesn't raise any error.
        self.mat.detach()

    def test_getitem(self):
        self.assertEqual(self.mat[0, 0], 0)

    def test_setitem(self):
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.mat[i, j] = i
        for i in xrange(self.nrows):
            for j in xrange(self.ncols):
                self.assertEqual(self.mat[i, j], i)
