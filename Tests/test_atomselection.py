
import os
import unittest

from ptools import Rigidbody


TEST_1F88_PDB = os.path.join(os.path.dirname(__file__), 'data', '1F88.pdb')
TEST_2AAV_PDB = os.path.join(os.path.dirname(__file__), 'data', '2AAV.one.pdb')


class TestAtomSelection(unittest.TestCase):
    def setUp(self):
        self.rig = Rigidbody(TEST_1F88_PDB)

    def testSelectAll(self):
        allAtoms = self.rig.select_all_atoms()
        self.assertEqual(len(allAtoms), 5067)

    def testSelectCA(self):
        CAatoms = self.rig.alpha()
        self.assertEqual(len(CAatoms), 643)

    def testSelectAtomType_simple(self):
        CAatoms = self.rig.select_atom_type("CA")
        self.assertEqual(len(CAatoms), 643)

    def testSelectAtomType_wildcard(self):
        CAatoms = self.rig.select_atom_type("C*")
        self.assertEqual(len(CAatoms), 3379)

    def testSelectBackbone(self):
        bbAtoms = self.rig.backbone()
        self.assertEqual(len(bbAtoms), 2572)

    def testSelectResRange(self):
        res_1_35 = self.rig.select_res_range(1, 35)
        self.assertEqual(len(res_1_35), 566)  # two chains

    def testSelectResRangeNegativeResId(self):
        rigid = Rigidbody(TEST_2AAV_PDB)
        selection = rigid.select_res_range(-4, -1) & rigid.alpha()
        self.assertEqual(len(selection), 4)

    def testAnd(self):
        res_1_35 = self.rig.select_res_range(1, 35)
        CAatoms = self.rig.select_atom_type("CA")

        ca_1_35 = res_1_35 & CAatoms
        self.assertEqual(len(ca_1_35), 70)  # 2*35: two chains, A and B

    def testselect_resid_type(self):
        met1 = self.rig.select_resid_type("MET") & self.rig.select_res_range(1, 5)
        self.assertEqual(len(met1), 16)
        met1A = self.rig.select_resid_type("MET") & self.rig.select_res_range(1, 5) & self.rig.select_chain_id("A")
        self.assertEqual(len(met1A), 8)

    def testSelectChainId(self):
        chainA = self.rig.select_chain_id("A")
        self.assertEqual(len(chainA), 2638)

    def testCreateRigid(self):
        met1A = self.rig.select_resid_type("MET") & self.rig.select_res_range(1, 5) & self.rig.select_chain_id("A")
        rigid = met1A.create_rigid()
        self.assertEqual(len(rigid), 8)

    def testNotOperator(self):
        sel_ca = self.rig.alpha()
        sel_not_ca = ~ sel_ca  # operator NOT
        self.assertEqual(len(sel_ca) + len(sel_not_ca), len(self.rig))

    def testAlternateNotOperator(self):
        sel_ca = self.rig.alpha()
        sel_not_ca = sel_ca.not_()  # operator NOT
        self.assertEqual(len(sel_ca) + len(sel_not_ca), len(self.rig))


if __name__ == '__main__':
    unittest.main()
