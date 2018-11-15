
import os
import unittest

from ptools import AttractRigidbody, AttractForceField2


TEST_PK6A_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6a.red')
TEST_PK6C_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6c.red')
TEST_FF_MBEST1K = os.path.join(os.path.dirname(__file__), 'data', 'mbest1k.par')
TEST_FF_MBEST1U = os.path.join(os.path.dirname(__file__), 'data', 'mbest1u.par')


class TestAttractForceField2(unittest.TestCase):
    """ test if calculated energies are stable through library versions """
    def setUp(self):
        self.a = AttractRigidbody(TEST_PK6C_RED)
        self.c = AttractRigidbody(TEST_PK6A_RED)

    def test_FF2k(self):
        #self.a = AttractRigidbody(TEST_PK6C_RED)
        #self.c = AttractRigidbody(TEST_PK6A_RED)

        self.a.set_rotation(False)
        self.a.set_translation(False)
        FF = AttractForceField2(TEST_FF_MBEST1K, 20.0)
        FF.add_ligand(self.a)
        FF.add_ligand(self.c)
        x = []
        for i in range(6):
            x.append(0.0)
        print "mbest1k", FF.function(x)
        self.assertAlmostEqual(FF.function(x), -32.9487770656)  # energy from ptools 0.3
        self.assertAlmostEqual(FF.function(x), FF.get_vdw() + FF.get_coulomb())
        assert(False)

    def test_has_nonbon8(self):
        self.assertTrue(hasattr(AttractForceField2, 'nonbon8'))

    #def tearDown(self):
    #    del self.a, self.c


class TestAttractForceField2_bis(unittest.TestCase):
    """ test if calculated energies are stable through library versions """
    def setUp(self):
        self.a = AttractRigidbody(TEST_PK6C_RED)
        self.c = AttractRigidbody(TEST_PK6A_RED)

    def test_FF2K_bis(self):
        #self.a = AttractRigidbody(TEST_PK6C_RED)
        #self.c = AttractRigidbody(TEST_PK6A_RED)

        self.a.set_rotation(False)
        self.a.set_translation(False)
        FF = AttractForceField2(TEST_FF_MBEST1U, 20.0)
        FF.add_ligand(self.a)
        FF.add_ligand(self.c)
        x = []
        for i in range(6):
            x.append(0.0)
        print "mbest1u.par", FF.function(x)
        self.assertAlmostEqual(FF.function(x), -32.9487770656)  # energy from ptools 0.3
        self.assertAlmostEqual(FF.function(x), FF.get_vdw() + FF.get_coulomb())
        assert(False)

    #def tearDown(self):
    #    del self.a, self.c


if __name__ == '__main__':
    unittest.main()
