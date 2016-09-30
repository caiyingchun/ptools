# -*- coding: utf-8 -*-
import math
import random
import unittest

# ptools and Heligeom are now python modules
# a) the directory (ptools or Heligeom) is the module name
# b) the directory contains a file __init__.py
# c) The commands in __init__.py import scripts if desired
from ptools import *
from ptools.Heligeom import heliAnalyze, heliConstruct
 
class Test_heliAnalyze(unittest.TestCase):

	def setUp(self):
		self.mono1 = Rigidbody("Heligeom_ref/2GLS_A.pdb")
		self.mono2 = Rigidbody("Heligeom_ref/2GLS_B.pdb")
		self.PDB_CRITERIA = 1e-3
		self.CRITERIA = 1e-15

	def test_end_to_end(self):
		""" Monomers 1 + 2 should be identical to heligeom-constructed dimer."""
		initial = self.mono1 + self.mono2
		hp = heliAnalyze(self.mono1, self.mono2, False)
		final = heliConstruct(self.mono1, hp, 2)
		rmsd = Rmsd(initial, final)
		print "test_end_to_end: rmsd mono1+mono2 vs constructed hexamer:", rmsd
		self.assertTrue(rmsd < self.PDB_CRITERIA)

	def test_end_to_end2(self):
		""" Mono 7 in heligeom-constructed ring with pitch 0 and N=6 should overlap mono 1."""
		hp = heliAnalyze(self.mono1, self.mono2, False)
		final = heliConstruct(self.mono1, hp, 7)
		# Monomers chains are automatically labelled A - G
		mono7 = final.SelectChainId('G').CreateRigid()
		rmsd = Rmsd(self.mono1, mono7)
		print "test_end_to_end2: rmsd mono1 mono7 of hexamer:", rmsd
		self.assertTrue(rmsd < self.PDB_CRITERIA)

	def test_ABrotate_old_behavior(self):
		""" Old ptools behavior: theta should refer to angle of axis rotation."""
		thing = Rigidbody()
		thing.AddAtom(Atom(Atomproperty(), Coord3D(1,0,0)))
		ABrotate( Coord3D(0,0,0), Coord3D(0,0,1), thing, math.pi/2)
		newcoords = thing.GetCoords(0)
		self.assertTrue(abs(newcoords.x - 0.0) < self.CRITERIA)
		self.assertTrue(abs(newcoords.y + 1.0) < self.CRITERIA)
		self.assertTrue(abs(newcoords.z - 0.0) < self.CRITERIA)

	#def test_ABrotate_desired_behavior(self):
	#	""" New ptools behavior: theta should refer to angle of point rotation."""
	#	thing = Rigidbody()
	#	thing.AddAtom(Atom(Atomproperty(), Coord3D(1,0,0)))
	#	ABrotate( Coord3D(0,0,0), Coord3D(0,0,1), thing, math.pi/2)
	#	newcoords = thing.GetCoords(0)
	#	self.assertTrue(abs(newcoords.x - 0.0) < self.CRITERIA)
	#	self.assertTrue(abs(newcoords.y - 1.0) < self.CRITERIA)
	#	self.assertTrue(abs(newcoords.z - 0.0) < self.CRITERIA)


unittest.main()
