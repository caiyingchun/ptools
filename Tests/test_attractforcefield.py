
import os
import unittest

from ptools import AttractRigidbody, AttractForceField2


TEST_PK6A_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6a.red')
TEST_PK6C_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6c.red')
TEST_FF_MBEST1K = os.path.join(os.path.dirname(__file__), 'data', 'mbest1k.par')


class TestAttractForceField2(unittest.TestCase):
    """ test if calculated energies are stable through library versions """
    def test_FF2k(self):
        a = AttractRigidbody(TEST_PK6C_RED)
        c = AttractRigidbody(TEST_PK6A_RED)

        a.set_rotation(False)
        a.set_translation(False)
        FF = AttractForceField2(TEST_FF_MBEST1K, 20.0)
        FF.add_ligand(a)
        FF.add_ligand(c)
        x = []
        for i in range(6):
            x.append(0.0)
        self.assertAlmostEqual(FF.function(x), -32.9487770656)  # energy from ptools 0.3
        self.assertAlmostEqual(FF.function(x), FF.get_vdw() + FF.get_coulomb())

    def test_has_nonbon8(self):
        self.assertTrue(hasattr(AttractForceField2, 'nonbon8'))


if __name__ == '__main__':
    unittest.main()
