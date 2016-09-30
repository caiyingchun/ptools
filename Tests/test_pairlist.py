
import unittest

from ptools import (Rigidbody, AttractRigidbody, AttractPairList, Coord3D,
                    Atom, AtomPair)


class TestAttractPairList(unittest.TestCase):

    def setUp(self):
        # test that the generated pairlist is correct
        #
        #  two atoms are created for the receptor (R) and the ligand (L)
        #  as described below:
        #  x axis:
        #  0----1-----2-----3-----4-----5-------------------------------> x
        #
        #       R     R           L     L
        #

        r = Rigidbody()
        at = Atom()
        at.coords = Coord3D(1, 0, 0)
        r.AddAtom(at)
        at.coords = Coord3D(2, 0, 0)
        r.AddAtom(at)

        l = Rigidbody()
        at.coords = Coord3D(4, 0, 0)
        l.AddAtom(at)
        at.coords = Coord3D(5, 0, 0)
        l.AddAtom(at)

        self.ar = AttractRigidbody(r)
        self.al = AttractRigidbody(l)

    def testAtomPair(self):
        atp = AtomPair()
        atp.atlig = 23
        atp.atrec = 45
        self.assertEqual(atp.atlig, 23)
        self.assertEqual(atp.atrec, 45)

    def test_onepair(self):
        # use a small cutoff to only get one pair
        pl = AttractPairList(self.ar, self.al, 2.01)
        self.assertEqual(len(pl), 1)

        count = 0
        for p in pl:
            count += 1
            self.assertTrue(count < 2)
        self.assertEqual(count, 1)

    def test_three_pairs(self):
        # use a slightly bigger cutoff to get 3 pairs:
        # (1,4) (2,4) and (2,5)
        pl = AttractPairList(self.ar, self.al, 3.01)
        self.assertEqual(len(pl), 3)


if __name__ == '__main__':
    unittest.main()
