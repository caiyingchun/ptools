
import filecmp
import unittest

from ptools.commands import ptools_cli

from ..utils import mk_tmp_file
from .. import (TEST_LIGAND_RED_ATTRACT1,
                TEST_TRANSLATE_OUTPUT)


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.output_file = mk_tmp_file()
        self.output_name = self.output_file.name

    def tearDown(self):
        self.output_file.close()

    def test_translate_attract1(self):
        args = ['translate', TEST_LIGAND_RED_ATTRACT1, TEST_LIGAND_RED_ATTRACT1,
                '-o', self.output_name]
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_TRANSLATE_OUTPUT, self.output_name))
