
"""test_attract - Functional tests for the ptools attract command."""


from __future__ import print_function


import filecmp
import os
import shutil

import pytest

import ptools
from ptools.scripts import ptools_cli

from .. import skip_on_osx

from .. import (TEST_SINGLEMINIM_LIGAND,
                TEST_SINGLEMINIM_RECEPTOR,
                TEST_SINGLEMINIM_ATTRACT_INP,
                TEST_SINGLEMINIM_FF_PARAM,
                TEST_SINGLEMINIM_ATTRACT_OUT,
                TEST_SINGLEMINIM_MINIMIZATION_OUT,

                TEST_DOCKING_LIGAND,
                TEST_DOCKING_RECEPTOR,
                TEST_DOCKING_ATTRACT_INP,
                TEST_DOCKING_FF_PARAM,
                TEST_DOCKING_ROTATION,
                TEST_DOCKING_TRANSLATION,
                TEST_DOCKING_ATTRACT_OUT)


def run_attract_test(args, capfd, ref_output_file):
    """Run attract with `args`, read the standard output using `capfd` and
    compare it with the reference output stored in `ref_output_file`."""
    cmd_args = ptools_cli.parse_command_line(args)
    cmd_args.func(cmd_args)

    out, err = capfd.readouterr()
    output_test = ptools.io.parse_attract_output(out)
    output_ref = ptools.io.read_attract_output(ref_output_file)

    errors = output_ref.assert_equal(output_test)
    if errors:
        print("{} errors occured:".format(len(errors)))
        for e in errors:
            print(e.message, end='\n\n')
    assert len(errors) == 0


@pytest.fixture
def minim_traj(request):
    def teardown():
        os.remove(traj)
    traj = 'minimization.trj'  # hard-coded in attract_cmd.py
    request.addfinalizer(teardown)
    return traj


@skip_on_osx
def test_single_minimization(capfd, minim_traj):
    # output_name = 'minimization.trj'  # hard-coded in attract_cmd.py
    output_name = minim_traj
    args = ['attract',
            '-r', TEST_SINGLEMINIM_RECEPTOR,
            '-l', TEST_SINGLEMINIM_LIGAND,
            '--ref', TEST_SINGLEMINIM_LIGAND,
            '-c', TEST_SINGLEMINIM_ATTRACT_INP,
            '-p', TEST_SINGLEMINIM_FF_PARAM,
            '-s']
    run_attract_test(args, capfd, TEST_SINGLEMINIM_ATTRACT_OUT)
    assert filecmp.cmp(TEST_SINGLEMINIM_MINIMIZATION_OUT, output_name) is True


@pytest.fixture
def docking_trans_rot(request):
    def teardown():
        os.remove('rotation.dat')
        os.remove('translation.dat')
    request.addfinalizer(teardown)
    # Copy rotation.dat and translation.dat to current directory
    # (those names are hard-coded in attract).
    shutil.copyfile(TEST_DOCKING_ROTATION, 'rotation.dat')
    shutil.copyfile(TEST_DOCKING_TRANSLATION, 'translation.dat')


@skip_on_osx
def test_docking(capfd, docking_trans_rot):
    # Run attract.
    args = ['attract',
            '-r', TEST_DOCKING_RECEPTOR,
            '-l', TEST_DOCKING_LIGAND,
            '-c', TEST_DOCKING_ATTRACT_INP,
            '-p', TEST_DOCKING_FF_PARAM,
            '-t', '4']
    run_attract_test(args, capfd, TEST_DOCKING_ATTRACT_OUT)
