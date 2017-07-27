
import os
import unittest

from ptools import Rigidbody


TEST_1F88_PDB = os.path.join(os.path.dirname(__file__), 'data', '1F88.pdb')
TEST_2AAV_PDB = os.path.join(os.path.dirname(__file__), 'data', '2AAV.one.pdb')


class TestAtomSelection(unittest.TestCase):
    def setUp(self):
        self.rig = Rigidbody(TEST_1F88_PDB)

    def testSelectAll(self):
        allAtoms = self.rig.SelectAllAtoms()
        self.assertEqual(len(allAtoms), 5067)

    def testSelectget_CA(self):
        CAatoms = self.rig.get_CA()
        self.assertEqual(len(CAatoms), 643)

    def testSelectAtomType_simple(self):
        CAatoms = self.rig.SelectAtomType("CA")
        self.assertEqual(len(CAatoms), 643)

    def testSelectAtomType_wildcard(self):
        CAatoms = self.rig.SelectAtomType("C*")
        self.assertEqual(len(CAatoms), 3379)

    def testSelectbackbone(self):
        bbAtoms = self.rig.backbone()
        self.assertEqual(len(bbAtoms), 2572)

    def testSelectResRange(self):
        res_1_35 = self.rig.SelectResRange(1, 35)
        self.assertEqual(len(res_1_35), 566)  # two chains

    def testSelectResRangeNegativeResId(self):
        rigid = Rigidbody(TEST_2AAV_PDB)
        selection = rigid.SelectResRange(-4, -1) & rigid.get_CA()
        self.assertEqual(len(selection), 4)

    def testAnd(self):
        res_1_35 = self.rig.SelectResRange(1, 35)
        CAatoms = self.rig.SelectAtomType("CA")

        ca_1_35 = res_1_35 & CAatoms
        self.assertEqual(len(ca_1_35), 70)  # 2*35: two chains, A and B

    def testSelectResidType(self):
        met1 = self.rig.SelectResidType("MET") & self.rig.SelectResRange(1, 5)
        self.assertEqual(len(met1), 16)
        met1A = self.rig.SelectResidType("MET") & self.rig.SelectResRange(1, 5) & self.rig.SelectChainId("A")
        self.assertEqual(len(met1A), 8)

    def testSelectChainId(self):
        chainA = self.rig.SelectChainId("A")
        self.assertEqual(len(chainA), 2638)

    def testcreate_rigid(self):
        met1A = self.rig.SelectResidType("MET") & self.rig.SelectResRange(1, 5) & self.rig.SelectChainId("A")
        rigid = met1A.create_rigid()
        self.assertEqual(len(rigid), 8)

    def testNotOperator(self):
        sel_ca = self.rig.get_CA()
        sel_not_ca = ~ sel_ca  # operator NOT
        self.assertEqual(len(sel_ca) + len(sel_not_ca), len(self.rig))

    def testAlternateNotOperator(self):
        sel_ca = self.rig.get_CA()
        sel_not_ca = sel_ca.not_()  # operator NOT
        self.assertEqual(len(sel_ca) + len(sel_not_ca), len(self.rig))


if __name__ == '__main__':
    unittest.main()
