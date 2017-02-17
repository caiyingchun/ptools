
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


class AttractOutputComparisonError(Exception):
    pass


class AttractOutputRotation(object):
    """Class that help storing a rotation data from Attract output string."""

    # Parse a minimization result line.
    minim_re = re.compile(r'{{ minimization nb (?P<id>\d+) of (?P<total>\d+) ; '
                          r'cutoff= (?P<cutoff>\d+\.\d+) \(A\) ; '
                          r'maxiter= (?P<maxiter>\d+)')

    def __init__(self, i=0, minimlist=[], matrix=[], energie=0.0, rmsd=0.0):
        self.id = i
        self.minimlist = minimlist
        self.matrix = matrix
        self.energie = energie
        self.rmsd = rmsd

    def number_of_minimizations(self):
        """Return the number of minimizations ran."""
        return len(self.minimlist)

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
        return cls(i, minimlist, matrix, data['ener'], data['rmsd'])

    def cmp(self, other):
        """Compare two AttractOutputRotation instances.
        
        Raises:
            AttractOutputComparisonError: if two rotations are different.
        """
        def isnan(num):
            return num != num
        
        # Compare identifiers.
        if self.id != other.id:
            err = 'identifiers differ: {} != {}'.format(self.id, other.id)
            raise AttractOutputComparisonError(err)
        
        # Compare matrices.
        if self.matrix != other.matrix: 
            err = 'matrices differ:\n{}\n-----\n{}'.format(self.format_matrix(),
                                                           other.format_matrix())
            raise AttractOutputComparisonError(err)
        
        # Compare minimizations.
        if self.number_of_minimizations() != other.number_of_minimizations():
            err = 'different number of minimizations: {} != {}'
            err = err.format(self.number_of_minimizations(),
                             other.number_of_minimizations())
            raise AttractOutputComparisonError(err)

        for minim1, minim2 in zip(self.minimlist, other.minimlist):
            if minim1['cutoff'] != minim2['cutoff']:
                err = 'minimization {}: cutoffs differ: {} != {}'
                err = err.format(minim1['id'], minim1['cutoff'], minim2['cutoff'])
                raise AttractOutputComparisonError(err)
            if minim1['maxiter'] != minim2['maxiter']:
                err = 'minimization {}: maxiters differ: {} != {}'
                err = err.format(minim1['id'], minim1['maxiter'], minim2['maxiter'])
                raise AttractOutputComparisonError(err)

        # Compare energies.
        if self.energie != other.energie:
            err = 'energies differ: {} != {}'.format(self.energie, other.energie)
            raise AttractOutputComparisonError(err)

        # Compare RMSDs.
        if self.rmsd != other.rmsd and not isnan(self.rmsd) and isnan(other.rmsd):
            err = 'RMSDs differ: {} != {}'.format(self.rmsd, other.rmsd)
            raise AttractOutputComparisonError(err)


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
        
        Raises:
            AttractOutputComparisonError: if two translations are different.
        """
        if self.id != other.id:
            err = 'translation {}: identifiers differ: {} != {}'
            err = err.format(self.id, self.id, other.id)
            raise AttractOutputComparisonError(err)

        if self.number_of_rotations() != other.number_of_rotations():
            err = 'translation {}: number of rotations differ: {} != {}'
            err = err.format(self.id,
                             self.number_of_translations(),
                             other.number_of_translations())
            raise AttractOutputComparisonError(err)

        for rot1, rot2 in zip(self.rotations, other.rotations):
            try:
                rot1.cmp(rot2)
            except Exception as e:
                err = 'translation {}: rotation {}: {}'.format(self.id, rot1.id, e)
                raise AttractOutputComparisonError(err)


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

        Raises:
            AttractOutputComparisonError: if two outputs are different.
        """
        if self.number_of_translations() != other.number_of_translations():
            err = 'number of translations differ: {} != {}'
            err = err.format(self.number_of_translations(),
                             other.number_of_translations())
            raise AttractOutputComparisonError(err)

        errors = []
        for trans1, trans2 in zip(self.translations, other.translations):
            try:
                trans1.cmp(trans2)
            except Exception as e:
                errors.append(e)
        return errors


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
    cmd_args = ptools_cli.parse_command_line(args)
    cmd_args.func(cmd_args)

    out, err = capfd.readouterr()
    output_ref = AttractOutput.from_string(out)
    output_test = AttractOutput.from_file(TEST_SINGLEMINIM_ATTRACT_OUT)

    errors = output_ref.cmp(output_test)
    if errors:
        for e in errors:
            print(e.message)
    assert len(errors) == 0
    assert filecmp.cmp(TEST_SINGLEMINIM_MINIMIZATION_OUT, output_name) == True


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
            # '--ref', TEST_DOCKING_LIGAND,
            '-c', TEST_DOCKING_ATTRACT_INP,
            '-p', TEST_DOCKING_FF_PARAM,
            '-t', '3']
    cmd_args = ptools_cli.parse_command_line(args)
    cmd_args.func(cmd_args)

    out, err = capfd.readouterr()
    output_ref = AttractOutput.from_string(out)
    output_test = AttractOutput.from_file(TEST_DOCKING_ATTRACT_OUT)

    errors = output_ref.cmp(output_test)
    if errors:
        for e in errors:
            print(e.message)
    assert len(errors) == 0

 
