
import filecmp
import sys
import unittest

import pytest

from ptools.scripts import ptools_cli

from ..utils import mk_tmp_file
from .. import (TEST_LIGAND_PDB,
                TEST_LIGAND_RED_ATTRACT1,
                TEST_LIGAND_RED_ATTRACT2,
                TEST_LIGAND_RED_SCORPION,
                TEST_LIGAND_RED_SCORPION_CGOPT)


class TestReduceAttract1(unittest.TestCase):

    def setUp(self):
        self.output_file = mk_tmp_file()
        self.output_name = self.output_file.name

    def tearDown(self):
        self.output_file.close()

    def test_reduce_attract1(self):
        args = ['reduce', TEST_LIGAND_PDB, '-o', self.output_name, 'attract1', '--prot']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_LIGAND_RED_ATTRACT1, self.output_name))


class TestReduceAttract2(unittest.TestCase):

    def setUp(self):
        self.output_file = mk_tmp_file()
        self.output_name = self.output_file.name

    def tearDown(self):
        self.output_file.close()

    def test_reduce_attract2(self):
        args = ['reduce', TEST_LIGAND_PDB, '-o', self.output_name, 'attract2']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_LIGAND_RED_ATTRACT2, self.output_name))


class TestReduceScorpion(unittest.TestCase):

    def setUp(self):
        self.output_file = mk_tmp_file()
        self.output_name = self.output_file.name

    def tearDown(self):
        self.output_file.close()

    def test_reduce_scorpion(self):
        args = ['reduce', TEST_LIGAND_PDB, '-o', self.output_name, 'scorpion']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_LIGAND_RED_SCORPION, self.output_name))

    # @pytest.mark.skipif(sys.platform == 'darwin',
    #                     reason="currently not working on OS X")
    # def test_reduce_scorpion_cgopt(self):
    #     args = ['reduce', TEST_LIGAND_PDB, '-o', self.output_name, 'scorpion', '--cgopt']
    #     cmd_args = ptools_cli.parse_command_line(args)
    #     cmd_args.func(cmd_args)
    #     self.assertTrue(filecmp.cmp(TEST_LIGAND_RED_SCORPION_CGOPT, self.output_name))

    def test_import_cgopt(self):
        import ptools.cgopt as cgopt
        self.assertTrue(hasattr(cgopt, 'optimize'))

    def test_import_cgopt2(self):
        from ptools import cgopt
        self.assertTrue(hasattr(cgopt, 'optimize'))


if __name__ == '__main__':
    unittest.main()
