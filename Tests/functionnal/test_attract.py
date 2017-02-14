
"""test_attract - Functionnal tests for the ptools attract command."""


from __future__ import print_function


import filecmp
import os
import re
import shutil
import sys
import unittest

import pytest

from ptools.scripts import ptools_cli

# from .. import (TEST_SINGLEMINIM_LIGAND,
#                 TEST_SINGLEMINIM_RECEPTOR,
#                 TEST_SINGLEMINIM_ATTRACT_INP,
#                 TEST_SINGLEMINIM_FF_PARAM,
#                 TEST_SINGLEMINIM_MINIMIZATION_OUT,

#                 TEST_DOCKING_LIGAND,
#                 TEST_DOCKING_RECEPTOR,
#                 TEST_DOCKING_ATTRACT_INP,
#                 TEST_DOCKING_ROTATION,
#                 TEST_DOCKING_TRANSLATION,
#                 TEST_DOCKING_ATTRACT_OUT)


class TestAttract(unittest.TestCase):

    @pytest.mark.skipif(sys.platform == 'darwin',
                reason="currently not working on OS X")
    def test_single_minimization(self):
        output_name = 'minimization.trj'  # hard-coded in attract_cmd.py
        args = ['attract',
                '-r', TEST_SINGLEMINIM_RECEPTOR,
                '-l', TEST_SINGLEMINIM_LIGAND,
                '--ref', TEST_SINGLEMINIM_LIGAND,
                '-c', TEST_SINGLEMINIM_ATTRACT_INP,
                '-p', TEST_SINGLEMINIM_FF_PARAM,
                '-s']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        self.assertTrue(filecmp.cmp(TEST_SINGLEMINIM_MINIMIZATION_OUT, output_name))
        os.remove(output_name)

    @pytest.mark.skipif(sys.platform == 'darwin',
                reason="currently not working on OS X")
    def test_docking(self):
        # Copy rotation.dat and translation.dat to current directory (to be removed).
        shutil.copyfile(TEST_DOCKING_ROTATION, 'rotation.dat')
        shutil.copyfile(TEST_DOCKING_TRANSLATION, 'translation.dat')

        # Run attract.
        args = ['attract',
                '-r', TEST_DOCKING_RECEPTOR,
                '-l', TEST_DOCKING_LIGAND,
                '--ref', TEST_DOCKING_LIGAND,
                '-c', TEST_DOCKING_ATTRACT_INP,
                '-t', '3']
        cmd_args = ptools_cli.parse_command_line(args)
        cmd_args.func(cmd_args)
        # self.assertTrue(filecmp.cmp(TEST_SINGLEMINIM_MINIMIZATION_OUT, self.output_name))

        # Remove files created during the run.
        os.remove('rotation.dat')
        os.remove('translation.dat')


    def test_coucou(self):
        read_attract_output(TEST_DOCKING_ATTRACT_OUT)



class AttractOutput(object):
    """Class that help storing and parsing Attract output data."""
    def __init__(self):
        self.translations = [[]]


    @classmethod
    def from_string(cls, content):
        def iterrotations():
            lines = content.splitlines()
            isrotation = False
            current_rotation = []
            for line in lines:
                if line.startswith('----- Rotation nb'):
                    isrotation = True
                    if current_rotation:
                        yield AttractOutputRotation.from_lines(current_rotation)
                        current_rotation = []
                if isrotation and line.strip():
                    current_rotation.append(line)

        for r in iterrotations():
            print(r.id)
            print(r.data)
            print(r.matrix)
            print("----------------------------")
        

class AttractOutputTranslation(object):
    """Class that help storing a translation data from Attract output string."""
    pass

class AttractOutputRotation(object):
    """Class that help storing a rotation data from Attract output string."""

    # Parse a minimization result line.
    minim_re = re.compile(r'{{ minimization nb (?P<id>\d+) of (?P<total>\d+) ; '
                      r'cutoff= (?P<cutoff>\d+\.\d+) \(A\) ; '
                      r'maxiter= (?P<maxiter>\d+)')

    def __init__(self, i=0, minimlist=[], matrix=[], data={}):
        self.id = i
        self.minimlist = minimlist
        self.matrix = matrix
        self.data = data

    @classmethod
    def from_lines(cls, rotation_lines):
        def parse_rotation_minim_output(match):
            typemap = {'id': int, 'total': int, 'cutoff': float, 'maxiter': int}
            minim = match.groupdict()
            for key, value in minim.iteritems():
                minim[key] = typemap[key](value)
            return minim

        def parse_rotation_data_line(line):
            tokens = line.split()[1:]
            rmsd = float('nan') if tokens[3] == 'XXXX' else float(tokens[3])
            d = dict(trans=int(tokens[0]), rot=int(tokens[1]),
                     ener=float(tokens[2]), rmsd=rmsd)
            return d

        minimlist = []
        matrix = []
        i = int(rotation_lines[0].split()[-2])
        for line in rotation_lines:
            match = cls.minim_re.match(line)
            if match:
                minimlist.append(parse_rotation_minim_output(match))
            elif line.startswith('=='):
                data = parse_rotation_data_line(line)
            elif line.startswith('MAT'):
                matrix.append(list(float(tok) for tok in line.split()[1:]))
        return cls(i, minimlist, matrix, data)

    

def read_attract_output(path):
    """Read attract result string saved to a file."""
    with open(path, 'rt') as f:
        content = f.read()
    return AttractOutput.from_string(content)



def main():
    read_attract_output('../data/docking/attract_trans3.out')

if __name__ == '__main__':
    main()





















