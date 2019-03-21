import unittest

from ptools import AttractRigidbody, AttractForceField1, Lbfgs, Coord3D
from ptools.docking import get_group_splitting, get_groups,  get_group

from . import TEST_TOYMINIM_LIGAND, TEST_TOYMINIM_RECEPTOR, TEST_TOYMINIM_FF_PARAM


class SubsetTests(unittest.TestCase):

    def test_grouping_too_many_requested_groups(self):
        data = xrange(7)
        ngroups_desired = 8
        ngroups, n = get_group_splitting(data, ngroups_desired)
        self.assertEqual(n, 1)
        self.assertEqual(ngroups, 7)

    def test_grouping_ndata_divides_evenly(self):
        data = xrange(144)
        ngroups_desired = 12
        ngroups, n = get_group_splitting(data, ngroups_desired)
        self.assertEqual(n, 12)
        self.assertEqual(ngroups, 12)

    def test_grouping_ndata_divides_with_remainder(self):
        data = xrange(255)
        ngroups_desired = 16
        ngroups, n = get_group_splitting(data, ngroups_desired)
        self.assertEqual(n, 16)
        self.assertEqual(ngroups, 16)

    def test_concatenated_group_lists_should_match_original_data(self):
        ndata = 10
        data = xrange(ndata)
		# [item for sublist in l for item in sublist]
		# Flattening thanks to https://stackoverflow.com/a/952952
        groupdata = [ item for sublist in get_groups(data, 4) for item in sublist ]
        self.assertEqual(set(groupdata), set(data))

    def test_concatenated_dictionary_groups_match_original_data(self):
        # data here resembles a use case using a dictionary of translations, e.g.
        #data = dict([ (i, 'abcdefghijklmnopqrstuvwxyz'[i]) for i in xrange(15) ])
        data = dict([ (i, object()) for i in xrange(15) ])
        ndata = len(data)
        for e in data.iteritems():
            print e
        groupdata = dict([ item for sublist in get_groups(data, 4) for item in sublist.iteritems() ])
        self.assertEqual(set(groupdata), set(data))

    def test_groups_should_match_expectations(self):
        ndata = 11
        data = xrange(ndata)
        groups = get_groups(data, 4)
        self.assertEqual(len(groups), 4)
        for g in groups[:-1]:
            self.assertEqual(len(g), 3)
        self.assertEqual(len(groups[-1]), 2)
        

class MinimizationTests(unittest.TestCase):
    """CHR April 2017 Add simple geometric minimization tests.

    Test 1: ligand L in test1 starts +5A along Y above the optimum,
    which is equidistant from the two CA atoms 1 and 2 forming the receptor.

        Ligand:                  L
                                 .
                                 .
                                 .
        Receptor:  ----1-------------------2---


    Optimum position:

        Receptor:  ----1---------L---------2---


    Test 2: same as Test 1, but here L starts 5 A further along X and Z
    """

    def setUp(self):
        self.cutoff = 100.0
        self.niter = 100
        self.forcefield = AttractForceField1(TEST_TOYMINIM_FF_PARAM, self.cutoff)

    def test_find_analytical_solution_when_displaced_along_Y(self):
        """Minimization should displace ligand by -5A along Y-axis to minimum-energy position."""
        receptor = AttractRigidbody(TEST_TOYMINIM_RECEPTOR)
        receptor.set_translation(False)
        receptor.set_rotation(False)
        ligand = AttractRigidbody(TEST_TOYMINIM_LIGAND)
        atom = ligand.copy_atom(0)
        # Ligand position in file            5.0, 5.0, 0.0
        # Minimum-energy ligand position is  5.0, 0.0, 0.0
        print "Ligand starting position: %s" % atom.to_pdb_string()

        self.forcefield.add_ligand(receptor)
        self.forcefield.add_ligand(ligand)
        lbfgs_minimizer = Lbfgs(self.forcefield)
        lbfgs_minimizer.minimize(self.niter)

        X = lbfgs_minimizer.get_minimized_vars()  # variables after minimization
        euler_angles = X[0:3]
        dx, dy, dz = X[3:]
        for angle in euler_angles:
            self.assertAlmostEqual(angle, 0.0)
        self.assertAlmostEqual(dx, 0.0)
        self.assertAlmostEqual(dy, -5.0)
        self.assertAlmostEqual(dz, 0.0)

    def test_find_analytical_solution_when_displaced_along_X_Y_Z(self):
        """Minimization should displace ligand by -5A along each axis to minimum-energy position."""
        # PGTOL not easily changeable through ptools, needs to be set tighter to get closer to optimum
        tolerance = 5e-5
        receptor = AttractRigidbody(TEST_TOYMINIM_RECEPTOR)
        receptor.set_translation(False)
        receptor.set_rotation(False)
        ligand = AttractRigidbody(TEST_TOYMINIM_LIGAND)
        # New starting ligand position      10.0, 5.0, 5.0
        # Minimum-energy ligand position is  5.0, 0.0, 0.0
        ligand.translate(Coord3D(5.0, 0.0, 5.0))
        atom = ligand.copy_atom(0)
        print "Ligand starting position: %s" % atom.to_pdb_string()

        self.forcefield.add_ligand(receptor)
        self.forcefield.add_ligand(ligand)
        lbfgs_minimizer = Lbfgs(self.forcefield)
        lbfgs_minimizer.minimize(self.niter)

        X = lbfgs_minimizer.get_minimized_vars()  # variables after minimization
        euler_angles = X[0:3]
        dx, dy, dz = X[3:]
        for angle in euler_angles:
            self.assertAlmostEqual(angle, 0.0)
        self.assertLess(abs(dx + 5.0), tolerance)
        self.assertLess(abs(dy + 5.0), tolerance)
        self.assertLess(abs(dz + 5.0), tolerance)
