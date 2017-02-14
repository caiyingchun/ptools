
"""test_attract - Functionnal tests for the ptools attract command."""

import filecmp
import os
import unittest


from ptools.scripts import ptools_cli

from .. import (TEST_SINGLEMINIM_LIGAND,
                TEST_SINGLEMINIM_RECEPTOR,
                TEST_SINGLEMINIM_ATTRACT_INP,
                TEST_SINGLEMINIM_FF_PARAM,
                TEST_SINGLEMINIM_MINIMIZATION_OUT)


class TestAttract(unittest.TestCase):
    def setUp(self):
        self.output_name = 'minimization.trj'  # hard-code in attract_cmd.py

    def tearDown(self):
        try:
            os.remove(self.output_name)
        except:
            pass

    def test_single_minimization(self):
        args = ['attract',
                '-r', TEST_SINGLEMINIM_RECEPTOR,
                '-l', TEST_SINGLEMINIM_LIGAND,
                '--ref', TEST_SINGLEMINIM_LIGAND,
                '-c', TEST_SINGLEMINIM_ATTRACT_INP,
                '-p', TEST_SINGLEMINIM_FF_PARAM,
                '-s']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_SINGLEMINIM_MINIMIZATION_OUT, self.output_name))

