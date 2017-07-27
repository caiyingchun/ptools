import unittest

from ptools import AttractRigidbody, AttractForceField1, Lbfgs, Coord3D
from ptools.docking import get_group

from . import TEST_TOYMINIM_LIGAND, TEST_TOYMINIM_RECEPTOR, TEST_TOYMINIM_FF_PARAM


class SubsetTests(unittest.TestCase):

    def test_concatenated_group_lists_should_match_original_data(self):
        """Concatenated group lists should match original data list."""
        ndata = 10
        data = xrange(ndata)
        ngroups = 5
        gdata = []
        for ng in xrange(ngroups):
            gdata += get_group(data, ngroups, 1 + ng)
        self.assertEqual(len(gdata), len(data))
        for d, e in zip(data, gdata):
            self.assertEqual(d, e)

    def test_for_exact_division_last_group_should_have_expected_length(self):
        """When division is exact last group should have length n"""
        ndata = 10
        data = xrange(ndata)
        ngroups = 5
        n = ndata / ngroups
        ngroup = ngroups
        group = get_group(data, ngroups, ngroup)
        self.assertEqual(len(group), n + ndata % ngroups)

    def test_for_nonexact_division_last_group_should_have_expected_length(self):
        """When division is not exact last group should have n + ndata % ngroups"""
        ndata = 11
        data = xrange(ndata)
        ngroups = 5
        n = ndata / ngroups
        ngroup = ngroups
        group = get_group(data, ngroups, ngroup)
        self.assertEqual(len(group), n + ndata % ngroups)

    def test_for_different_nonexact_division_last_group_should_have_expected_length(self):
        """When division is not exact the last group should have length ndata % ngroups"""
        ndata = 49
        data = xrange(ndata)
        print list(data)
        ngroups = 9
        n = ndata / ngroups
        ngroup = ngroups
        group = get_group(data, ngroups, 1)
        print 1, group
        group = get_group(data, ngroups, ngroup - 1)
        print ngroup - 1, group
        group = get_group(data, ngroups, ngroup)
        print ngroup, group
        self.assertEqual(len(group), n + ndata % ngroups)


class MinimizationTests(unittest.TestCase):
    """CHR April 2017 add simple geometric minimization tests.

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
        receptor.setTranslation(False)
        receptor.setRotation(False)
        ligand = AttractRigidbody(TEST_TOYMINIM_LIGAND)
        atom = ligand.CopyAtom(0)
        # Ligand position in file            5.0, 5.0, 0.0
        # Minimum-energy ligand position is  5.0, 0.0, 0.0
        print "Ligand starting position: %s" % atom.ToPdbString()

        self.forcefield.addLigand(receptor)
        self.forcefield.addLigand(ligand)
        lbfgs_minimizer = Lbfgs(self.forcefield)
        lbfgs_minimizer.minimize(self.niter)

        X = lbfgs_minimizer.GetMinimizedVars()  # variables after minimization
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
        receptor.setTranslation(False)
        receptor.setRotation(False)
        ligand = AttractRigidbody(TEST_TOYMINIM_LIGAND)
        # New starting ligand position      10.0, 5.0, 5.0
        # Minimum-energy ligand position is  5.0, 0.0, 0.0
        ligand.Translate(Coord3D(5.0, 0.0, 5.0))
        atom = ligand.CopyAtom(0)
        print "Ligand starting position: %s" % atom.ToPdbString()

        self.forcefield.addLigand(receptor)
        self.forcefield.addLigand(ligand)
        lbfgs_minimizer = Lbfgs(self.forcefield)
        lbfgs_minimizer.minimize(self.niter)

        X = lbfgs_minimizer.GetMinimizedVars()  # variables after minimization
        euler_angles = X[0:3]
        dx, dy, dz = X[3:]
        for angle in euler_angles:
            self.assertAlmostEqual(angle, 0.0)
        self.assertLess(abs(dx + 5.0), tolerance)
        self.assertLess(abs(dy + 5.0), tolerance)
        self.assertLess(abs(dz + 5.0), tolerance)
