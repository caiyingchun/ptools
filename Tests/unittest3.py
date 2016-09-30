# -*- coding: utf-8 -*-
import os
import math
import random
import unittest

from ptools import *

# CHR, BB, CP unittests of PTools DNA functionality. Here "unit" in "unittest" means
# high-level functions that call the lower-level ones with a vague intention
# that all the functions are called.
#
# These tests verify the re-creation of the DNA examples that Benjamin
# added to the new tutorial, which were then put in the original Heligom paper,
# and which are now placed in the SI for the manuscript for the PTools2 release.

# The functions "stepN" defined here are meant to simplify the tests, as these steps
# must be performed sequentially for each test.

def step0():
	d = DNA("DNA_ref/bp.ato.pdb","DNA_ref/1QN4_DNA.pdb")
	return d

def step1(d):
	d1 = d.SubDNA(2,9)
	return d1

def step2(d1):
	d0 = DNA("DNA_ref/bp.ato.pdb","GCGAAC",BDNA())
	d2 = DNA("DNA_ref/bp.ato.pdb","GGCGGCGGCGGCGGCGG",ADNA())
	d3 = DNA(d0)
	d3.Add(d1)
	d4 = DNA(d3)
	d4.Add(d2)
	return d3, d4

def step3(d4):
	d6 = DNA(d4)
	d6.ApplyLocal(Roll(45.),14)
	return d6

def step4(d4):
	d7 = DNA(d4)
	d7.ApplyGlobal(Twist(20.), 7)
	return d7

# The tests themselves are here:

class TestDNA(unittest.TestCase):

	def setUp(self):
		self.PDB_CRITERIA = 1e-3
		self.CRITERIA = 1e-15

	def test_write(self):
		""" Calculated DNA PDB file should match reference file."""
		#d=DNA("DNA_ref/bp.ato.pdb","1QN4_DNA.pdb")
		d = step0()
		d.WritePDB("D_tmp.pdb")
		s0 = open("DNA_ref/D.pdb", 'r').read()
		s1 = open("D_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D_tmp.pdb")

	def test_SubDNA(self):
		""" Calculated DNA PDB file should match reference file."""
		d = step0()
		d1 = step1(d)
		d1.WritePDB("D1_tmp.pdb")
		s0 = open("DNA_ref/D1.pdb", 'r').read()
		s1 = open("D1_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D1_tmp.pdb")

	def test_add(self):
		""" Calculated DNA PDB file should match reference file."""
		d = step0()
		d1 = step1(d)
		d3, d4 = step2(d1)

		d3.WritePDB("D3_tmp.pdb")
		s0 = open("DNA_ref/D3.pdb", 'r').read()
		s1 = open("D3_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D3_tmp.pdb")

		d4.WritePDB("D4_tmp.pdb")
		s0 = open("DNA_ref/D4.pdb", 'r').read()
		s1 = open("D4_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D4_tmp.pdb")

	def test_ApplyLocal(self):
		""" Calculated DNA PDB file should match reference file."""
		d = step0()
		d1 = step1(d)
		d3, d4 = step2(d1)
		d6 = step3(d4)

		d6.WritePDB("D6_tmp.pdb")
		s0 = open("DNA_ref/D6.pdb", 'r').read()
		s1 = open("D6_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D6_tmp.pdb")

	def test_ApplyGlobal(self):
		""" Calculated DNA PDB file should match reference file."""
		d = step0()
		d1 = step1(d)
		d3, d4 = step2(d1)
		d7 = step4(d4)

		d7.WritePDB("D7_tmp.pdb")
		s0 = open("DNA_ref/D7.pdb", 'r').read()
		s1 = open("D7_tmp.pdb", 'r').read()
		self.assertTrue(s0 == s1)
		os.system("rm D7_tmp.pdb")


unittest.main()
