
import unittest

import ptools

"""test_movement -- unit test for Movement.h.


What those tests do
-------------------

Check that every class defined in Movement.h is available from Python.


What those tests don't do
-------------------------

Check that the functions and methods work properly i.e. return the proper result.

"""



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


if __name__ == '__main__':
    unittest.main()
