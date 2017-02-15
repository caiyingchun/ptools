
"""test_attract - Functionnal tests for the ptools attract command."""


from __future__ import print_function


import filecmp
import os
import re
import shutil
import StringIO
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
     

def itercontent(fileobj, delim):
    """Iterate over a file content.
    
    Return the lines between two occurences of `delim`.

    Args:
        fileobj (file): iterator that allow to iterate over a file lines.
        delim (str): separator string.

    Returns:
        iterator[str]: lines between 2 occurences of `delim`.
    """
    current_token = ''
    istoken = False
    for line in fileobj:
        if line.startswith(delim):
            istoken = True
            if current_token:
                yield current_token
                current_token = ''
        if istoken:
            current_token += line
    yield current_token


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

    def format_matrix(self):
        """Return a string reprenting the matrix."""
        s = '\n'.join(' '.join('{: 14.7f}'.format(value) for value in row)
                      for row in self.matrix)
        return s

    @classmethod
    def from_string(cls, content):
        """Initialization from string."""
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
        lines = content.splitlines()
        i = int(lines[0].split()[-2])
        for line in lines:
            match = cls.minim_re.match(line)
            if match:
                minimlist.append(parse_rotation_minim_output(match))
            elif line.startswith('=='):
                data = parse_rotation_data_line(line)
            elif line.startswith('MAT'):
                matrix.append(list(float(tok) for tok in line.split()[1:]))
        return cls(i, minimlist, matrix, data)

    def cmp(self, other):
        """Compare two AttractOutputRotation instances.
        
        Return:
            str: empty string if rotations are identical, else
                a description of the differences.
        """
        if self.matrix != other.matrix:
            print('')
        

class AttractOutputTranslation(object):
    def __init__(self, id=0, rotations=[]):
        self.id = id
        self.rotations = rotations

    @classmethod
    def from_string(cls, content):
        """Initialization from string."""
        rotations = []
        fileobj = StringIO.StringIO(content)
        transid = int(next(fileobj).split()[-2])
        for lines in itercontent(fileobj, '----- Rotation nb'):
            rot = AttractOutputRotation.from_string(lines)
            rotations.append(rot)
        return cls(transid, rotations)

    def number_of_rotations(self):
        """Return the number of rotations."""
        return len(self.rotations)

    def cmp(self, other):
        """Compare two AttractOutputTranslation instances.
        
        Return:
            str: empty string if translations are identical, else
                a description of the differences.
        """
        if self.id != other.id:
            msg = 'translation {}: identifiers differ: {} != {}'
            return msg.format(self.id, self.id, other.id)

        if self.number_of_rotations() != other.number_of_rotations():
            msg = 'translation {}: number of rotations differ: {} != {}'
            return msg.format(self.id,
                              self.number_of_translations(),
                              other.number_of_translations())

        for rot1, rot2 in zip(self.rotations, other.rotations):
            result = rot1.cmp(rot2)
            if result:
                return result
        return ''




class AttractOutput(object):
    def __init__(self):
        self.translations = []

    def number_of_translations(self):
        """Return the number of translations."""
        return len(self.translations)

    def number_of_rotations(self):
        """Return the list of the number of rotations for each translation."""
        return [t.number_of_rotations() for t in self.translations]

    @classmethod
    def from_file(cls, path):
        """Initialization from file."""
        with open(path, 'rt') as stream:
            return cls.from_stream(stream)

    @classmethod
    def from_string(cls, content):
        """Initialization from string."""
        return cls.from_stream(StringIO.StringIO(content))

    @classmethod
    def from_stream(cls, stream):
        """Initialization from stream (typically file object)."""
        output = cls() 
        for trans in itercontent(stream, '@@@@@@@ Translation nb '):
            t = AttractOutputTranslation.from_string(trans)
            output.translations.append(t)
        return output

    def cmp(self, other):
        """Compare two AttractOutput instances.
        
        Return:
            str: empty string if outputs are identical, else
                a description of the differences.
        """
        if self.number_of_translations() != other.number_of_translations():
            msg = 'number of translations differ: {} != {}'
            print(msg.format(self.number_of_translations(),
                             other.number_of_translations()))
            return False

        for trans1, trans2 in zip(self.translations, other.translations):
            if not trans1.cmp(trans2):
                return False

        return True


def main():
    fname1 = '../data/docking/attract_trans3.out'
    fname2 = '/Users/benoist/Desktop/foo.attract.out'
    
    output1 = AttractOutput.from_file(fname1)
    output2 = AttractOutput.from_file(fname2)
    
    output1.cmp(output2)

if __name__ == '__main__':
    main()





















