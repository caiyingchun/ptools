# -*- coding: utf-8 -*-
from ptools import *
import random
import unittest
import sys
import math
import os


TEST_1FINR_PDB = os.path.join(os.path.dirname(__file__), 'data', '1FIN_r.pdb')
TEST_1F88_PDB = os.path.join(os.path.dirname(__file__), 'data', '1F88.pdb')
TEST_2AAV_PDB = os.path.join(os.path.dirname(__file__), 'data', '2AAV.one.pdb')
TEST_FF_MBEST1K = os.path.join(os.path.dirname(__file__), 'data', 'mbest1k.par')
TEST_PK6A_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6a.red')
TEST_PK6C_RED = os.path.join(os.path.dirname(__file__), 'data', 'pk6c.red')



class TestBasicMoves(unittest.TestCase):
    def setUp(self):
        self.rigid1=Rigidbody(TEST_1FINR_PDB)
        self.rigid2=Rigidbody(self.rigid1)
        self.rigid3=Rigidbody(self.rigid2)

    def testBasicRmsd(self):
        rigtmp=Rigidbody(self.rigid1)
        self.assertEqual(Rmsd(self.rigid1, self.rigid1), 0.0)
        self.rigid1.Translate(Coord3D(4,0,0))
        self.assertEqual(Rmsd(rigtmp, self.rigid1), 4)
        
    def testErrorsRmsd(self):
        rigid1 = Rigidbody()
        rigid2 = Rigidbody()
        #cannot calculate an rmsd on an empty object
        self.assertRaises(ValueError, Rmsd, rigid1, rigid2)
        
        #check input paramter types:
        self.assertRaises(RuntimeError, Rmsd, self.rigid1, "hello")
        self.assertRaises(RuntimeError, Rmsd, "hello",  self.rigid1)
        
        
    def testRmsdAtomSelection1(self):
        #tests Rmsd with an AtomSelection object
        atsel = self.rigid1.SelectAllAtoms()
        self.assertEqual(Rmsd(atsel,self.rigid2), 0)    
        

    def testRmsdAtomSelection2(self):
        #tests Rmsd with an AtomSelection object
        atsel = self.rigid1.SelectAllAtoms()
        self.assertEqual(Rmsd(self.rigid2, atsel), 0)
        


    def testTranslation1(self):
        CoM1 = self.rigid1.FindCenter()
        self.rigid1.Translate(Coord3D(3.0, -55.67, 1))
        CoM2 = self.rigid1.FindCenter()
        diff=CoM2-CoM1
        self.assertTrue( norm2(diff + Coord3D(-3.0, 55.67, -1.0)) < 1e-6)
        self.rigid1.Translate(Coord3D(-3.0, 55.67, -1.0))   # translate back
        self.assertTrue(Rmsd(self.rigid1, self.rigid2) < 1e-6)

    def testTranslation2(self):
        vec1 = Coord3D (-123.54, 45.62, -99.003)
        vec2 = Coord3D (36.3125, 2.78, -36.378)
        self.rigid2.Translate(vec1+vec2)
        self.rigid2.Translate(vec1-vec2)
        self.rigid2.Translate(Coord3D() - 2*vec1)  #should be a global null translation + round error
        self.assertTrue(Rmsd(self.rigid2, self.rigid3) < 1e-6)

class TestRotations(unittest.TestCase):
    def setUp(self):
       
        at1 = Atom(Atomproperty(),Coord3D(1,0,0))
        at2 = Atom(Atomproperty(),Coord3D(0,1,0))
        at3 = Atom(Atomproperty(),Coord3D(0,0,1))
        at4 = Atom(Atomproperty(),Coord3D(1,1,1))
        
        rig = Rigidbody()
        rig.AddAtom(at1)
        rig.AddAtom(at2)
        rig.AddAtom(at3)
        rig.AddAtom(at4)
        
        self.rig = rig
        
    def testRotZ(self):
        
        
        self.rig.ABrotate(Coord3D(0,0,0), Coord3D(0,0,1), math.pi/2)
        # i should now be j
        co1 = self.rig.CopyAtom(0).coords
        self.assertAlmostEqual(co1.x, 0)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 1)
        
        # j becomes -i
        co2 = self.rig.CopyAtom(1).coords
        self.assertAlmostEqual(co2.x, -1)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 0)

        #k is still k:
        co3 = self.rig.CopyAtom(2).coords
        self.assertAlmostEqual(co3.x, 0)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 1)
        
    def testRotX(self):
        self.rig.ABrotate(Coord3D(0,0,0), Coord3D(1,0,0), math.pi/2)
        
        #i is still i
        co1 = self.rig.CopyAtom(0).coords
        self.assertAlmostEqual(co1.x, 1)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 0)
        
        # j becomes k
        co2 = self.rig.CopyAtom(1).coords
        self.assertAlmostEqual(co2.x, 0)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 1)

        #k becomes -j
        co3 = self.rig.CopyAtom(2).coords
        self.assertAlmostEqual(co3.x, 0)
        self.assertAlmostEqual(co3.y, -1)
        self.assertAlmostEqual(co3.z, 0)
        

    def testRotY(self):
        self.rig.ABrotate(Coord3D(0,0,0), Coord3D(0,1,0), math.pi/2)
        
        #i becomes -j
        co1 = self.rig.CopyAtom(0).coords
        self.assertAlmostEqual(co1.x, 0)
        self.assertAlmostEqual(co1.z, -1)
        self.assertAlmostEqual(co1.y, 0)
        
        # j is still j
        co2 = self.rig.CopyAtom(1).coords
        self.assertAlmostEqual(co2.x, 0)
        self.assertAlmostEqual(co2.y, 1)
        self.assertAlmostEqual(co2.z, 0)

        #k becomes i
        co3 = self.rig.CopyAtom(2).coords
        self.assertAlmostEqual(co3.x, 1)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 0)
        
        
    def testRotZ_trans(self):
        
        self.rig.ABrotate(Coord3D(1,1,1), Coord3D(1,1,3), math.pi/2)
        
        
        co1 = self.rig.CopyAtom(0).coords
        self.assertAlmostEqual(co1.x, 2)
        self.assertAlmostEqual(co1.z, 0)
        self.assertAlmostEqual(co1.y, 1)
        
        
        co2 = self.rig.CopyAtom(1).coords
        self.assertAlmostEqual(co2.x, 1)
        self.assertAlmostEqual(co2.y, 0)
        self.assertAlmostEqual(co2.z, 0)

        co3 = self.rig.CopyAtom(2).coords
        self.assertAlmostEqual(co3.x, 2)
        self.assertAlmostEqual(co3.y, 0)
        self.assertAlmostEqual(co3.z, 1)

        co4 = self.rig.CopyAtom(3).coords
        self.assertAlmostEqual(co4.x, 1)
        self.assertAlmostEqual(co4.y, 1)
        self.assertAlmostEqual(co4.z, 1)
        
        




class TestPairlist(unittest.TestCase):
    
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
        at.coords = Coord3D(1,0,0)
        r.AddAtom(at)
        at.coords = Coord3D(2,0,0)
        r.AddAtom(at)
        
        l = Rigidbody()
        at.coords = Coord3D(4,0,0)
        l.AddAtom(at)
        at.coords = Coord3D(5,0,0)
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
        #use a small cutoff to only get one pair
        
        pl = AttractPairList(self.ar, self.al, 2.01) #using 2.01 A for the cutoff
        self.assertEqual(len(pl), 1)
        
        count=0
        for p in pl:
            count+=1
            self.assertTrue(count <2)
        self.assertEqual(count, 1)
        
    def test_three_pairs(self):
        #use a slightly bigger cutoff to get 3 pairs:
        # (1,4) (2,4) and (2,5)
        
        pl = AttractPairList(self.ar, self.al, 3.01)
        self.assertEqual(len(pl), 3)

unittest.main()
