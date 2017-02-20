from __future__ import print_function

import os
import re
import StringIO
import sys

from _ptools import Matrix

from .forcefield import PTOOLS_FORCEFIELDS
from .exceptions import FileParsingError


class AttractOutputRotation(object):
    """Class that help storing a rotation data from Attract output string."""

    # Parse a minimization result line.
    minim_re = re.compile(r'{{ minimization nb (?P<id>\d+) of (?P<total>\d+) ; '
                          r'cutoff= (?P<cutoff>\d+\.\d+) \(A\) ; '
                          r'maxiter= (?P<maxiter>\d+)')

    def __init__(self, i=0, minimlist=[], matrix=[], energie=0.0, rmsd=0.0):
        self.id = i
        self.minimlist = minimlist
        self._matrix = Matrix(4, 4)
        self.energie = energie
        self.rmsd = rmsd
        self.matrix = matrix

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, m):
        """Set matrix from list of list."""
        assert len(m) == 4
        assert len(m[0]) == 4
        for i in xrange(4):
            for j in xrange(4):
                self._matrix[i, j] = m[i][j]

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

    def assert_equal(self, other):
        """Compare two AttractOutputRotation instances.

        Raises:
            AssertionError: if two rotations are different.
        """
        def isnan(num):
            return num != num

        # Compare identifiers.
        if self.id != other.id:
            err = 'identifiers differ: {} != {}'.format(self.id, other.id)
            raise AssertionError(err)

        # Compare matrices.
        if self.matrix != other.matrix:
            err = 'matrices differ:\n{}\n-----\n{}'.format(self.format_matrix(),
                                                           other.format_matrix())
            raise AssertionError(err)

        # Compare minimizations.
        if self.number_of_minimizations() != other.number_of_minimizations():
            err = 'different number of minimizations: {} != {}'
            err = err.format(self.number_of_minimizations(),
                             other.number_of_minimizations())
            raise AssertionError(err)

        for minim1, minim2 in zip(self.minimlist, other.minimlist):
            if minim1['cutoff'] != minim2['cutoff']:
                err = 'minimization {}: cutoffs differ: {} != {}'
                err = err.format(minim1['id'], minim1['cutoff'], minim2['cutoff'])
                raise AssertionError(err)
            if minim1['maxiter'] != minim2['maxiter']:
                err = 'minimization {}: maxiters differ: {} != {}'
                err = err.format(minim1['id'], minim1['maxiter'], minim2['maxiter'])
                raise AssertionError(err)

        # Compare energies.
        if self.energie != other.energie:
            err = 'energies differ: {} != {}'.format(self.energie, other.energie)
            raise AssertionError(err)

        # Compare RMSDs.
        if self.rmsd != other.rmsd and not isnan(self.rmsd) and isnan(other.rmsd):
            err = 'RMSDs differ: {} != {}'.format(self.rmsd, other.rmsd)
            raise AssertionError(err)


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

    def assert_equal(self, other):
        """Compare two AttractOutputTranslation instances.

        Raises:
            AssertionError: if two translations are different.
        """
        if self.id != other.id:
            err = 'translation {}: identifiers differ: {} != {}'
            err = err.format(self.id, self.id, other.id)
            raise AssertionError(err)

        if self.number_of_rotations() != other.number_of_rotations():
            err = 'translation {}: number of rotations differ: {} != {}'
            err = err.format(self.id,
                             self.number_of_translations(),
                             other.number_of_translations())
            raise AssertionError(err)

        for rot1, rot2 in zip(self.rotations, other.rotations):
            try:
                rot1.assert_equal(rot2)
            except Exception as e:
                err = 'translation {}: rotation {}: {}'.format(self.id, rot1.id, e)
                raise AssertionError(err)

    def get_rotation(self, id):
        """Return the rotation with id `id`.

        Args:
            id (int): id of the rotation to find in the list of rotations.

        Returns:
            AttractOutputRotation: rotation with id `id`.

        Raises:
            IndexError: if rotation id cannot be found in
               docking ouputs.

            ValueError: if multiple entries with the same id have been found.
        """
        rlist = [r for r in self.rotations if r.id == id]
        if not rlist:
            err = 'rotation identifier {} not found'.format(id)
            raise IndexError(err)
        if len(rlist) > 1:
            err = 'multiple rotations found with id {}'.format(id)
            raise ValueError(err)
        return rlist[0]


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

    def assert_equal(self, other):
        """Compare two AttractOutput instances.

        Raises:
            AssertionError: if two outputs are different.
        """
        if self.number_of_translations() != other.number_of_translations():
            err = 'number of translations differ: {} != {}'
            err = err.format(self.number_of_translations(),
                             other.number_of_translations())
            raise AssertionError(err)

        errors = []
        for trans1, trans2 in zip(self.translations, other.translations):
            try:
                trans1.assert_equal(trans2)
            except Exception as e:
                errors.append(e)
        return errors

    def get_translation(self, id):
        """Return the translation with id `id`.

        Args:
            id (int): id of the translation to find in the list of translations.

        Returns:
            AttractOutputTranslation: translation with id `id`.

        Raises:
            IndexError: if translation id cannot be found in
               docking ouputs.

            ValueError: if multiple entries with the same id have been found.
        """
        tlist = [t for t in self.translations if t.id == id]
        if not tlist:
            err = 'translation identifier {} not found'.format(id)
            raise IndexError(err)
        if len(tlist) > 1:
            err = 'multiple translations found with id {}'.format(id)
            raise ValueError(err)
        return tlist[0]

    def get_matrix(self, transid, rotid):
        """Return rotation matrix for docking with translation id `transid`
        and rotation id `rotid`.

        Args:
            transid (int): docking translation identifier.
            rotid (int): docking rotation identifier.

        Return:
            list: 4x4 transformation matrix.

        Raises:
            IndexError: if `transid` or `rotid` cannot be found in
               docking ouputs.

            ValueError: if multiple entries with the same id have been found.
        """
        t = self.get_translation(transid)
        r = t.get_rotation(rotid)
        return r.matrix


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


def _print(*args, **kwargs):
    """Print a message to a file.

    Args:
        args (str): elements of a message
        kwargs (dict[str]): keyword arguments among:
            prefix (str): string added before the message itself
            end (str): string to be added after the message
            file (file): file pointer
            flush (bool): should the file pointer be flushed
            sep (str): separator between the elements of a message
    """
    valid_kwargs = ('prefix', 'end', 'file', 'flush', 'sep')
    for kw in kwargs:
        if kw not in valid_kwargs:
            raise KeyError("invalid keyword argument '{}'".format(kw))

    if not isinstance(args, list):
        args = [args]

    prefix = kwargs.pop('prefix', '')
    end = kwargs.pop('end', '\n')
    file = kwargs.pop('file', sys.stderr)
    flush = kwargs.pop('flush', False)
    sep = kwargs.pop('sep', ' ')

    message = prefix + sep.join(*args)
    print(message, file=file, end=end)

    if flush:
        file.flush()


def info(*args, **kwargs):
    """Display a log message."""
    prefix = kwargs.get('prefix', 'INFO: ')
    kwargs['prefix'] = prefix
    _print(*args, **kwargs)


def warning(*args, **kwargs):
    """Display a warning message."""
    prefix = kwargs.get('prefix', 'WARNING: ')
    kwargs['prefix'] = prefix
    _print(*args, **kwargs)


def error(*args, **kwargs):
    """Display a warning message."""
    prefix = kwargs.get('prefix', 'ERROR: ')
    kwargs['prefix'] = prefix
    _print(*args, **kwargs)


def critical(*args, **kwargs):
    """Display a warning message."""
    exitstatus = kwargs.pop('exitstatus', 1)
    prefix = kwargs.get('prefix', 'CRITICAL ERROR: ')
    kwargs['prefix'] = prefix
    _print(*args, **kwargs)
    sys.exit(exitstatus)


def is_comment(s, commentchar='#'):
    """Return True is `s` starts with `commentchar` or is empty."""
    return s.startswith(commentchar) or not len(s.strip())


def check_file_exists(path, msg="file not found: '%(path)s'", exitstatus=128,
                      prefix='ERROR: '):
    """Check that a file exists.

    Print an error message and exit if it does not.

    Args:
        path (str): path to file
        msg (str): message to print if file does not exist
        exitstatus (int): exit status
        prefix (str): message prefix
    """
    if not os.path.exists(path):
        msg = prefix + msg % vars()
        print(msg)
        sys.exit(exitstatus)


def read_attract_output(path):
    """Read an Attract output file, which contains the informations that are
    printed on stdout during a run.

    Args:
        path (str): path to file.

    Returns:
        AttractOutput: instance of class that stores attract output data.
    """
    return AttractOutput.from_file(path)


def parse_attract_output(content):
    """Parse Attract ouptut data, which contains the informations that are
    printed on stdout during a run.

    Args:
        content (str): attract output data.

    Returns:
        AttractOutput: instance of class that stores attract output data.
    """
    return AttractOutput.from_string(content)


def read_aminon(path):
    """Read Attract force field parameter file.

    This file is supposed to have 3 values per line:

        - index (int)
        - atom radius (float)
        - amplitude (float)
        - inull (0)

    Args:
        path (str): path to file.

    Returns:
        list[(float, float)]: radius and amplitude values for each line.
    """
    params = []
    with open(path, 'rt') as f:
        for line in f:
            # Ignore empty lines and lines starting with '#'.
            if line.strip() and not line.startswith('#'):
                tokens = line.split()
                radius = float(tokens[1])
                amplitude = float(tokens[2])
                params.append((radius, amplitude))
    return params


def check_ff_version_match(receptor, ligand):
    """Read force field name from receptor and ligand files and check that
    they match.

    Args:
        receptor (str): path to receptor file.
        ligand (str): path to ligand file.

    Returns:
        str: force field name.

    Raises:
        ValueError: if force field name from receptor and ligand differ.
    """
    ff_rec = read_forcefield_from_reduced(receptor)
    ff_lig = read_forcefield_from_reduced(ligand)
    if ff_rec != ff_lig:
        err = "receptor and ligand force field names do not match: '{}' != '{}'"
        err = err.format(ff_rec, ff_lig)
        raise ValueError(err)
    return ff_rec


def read_forcefield_from_reduced(path):
    """Read force field name from reduced PDB.

    Force field is read from the first line which should be formatted as
    HEADER <FORCE_FIELD_NAME>.

    Args:
        path (str): path to reduced PDB.

    Raises:
        IOError: if header cannot be extracted from first line.

    Returns:
        str: force field name in upper case.
    """
    def get_header_line():
        with open(path, 'rt') as f:
            line = f.readline()
        if not line.startswith('HEADER'):
            err = '{}: reduced PDB file first line must be a HEADER line '\
                  'specifying the chosen force field ({})'
            err = err.format(path, list(PTOOLS_FORCEFIELDS.keys()))
            raise IOError(err)
        return line

    def get_header_tokens():
        line = get_header_line()
        tokens = line.split()
        if len(tokens) < 2:
            err = "{}: cannot read force field name from first line '{}'"
            err = err.format(path, line)
            raise IOError(err)
        return tokens

    def get_ffname():
        ff = get_header_tokens()[1].upper()
        if ff not in PTOOLS_FORCEFIELDS:
            err = "{}: invalid force field name '{}': must choose between {}"
            err = err.format(path, ff, PTOOLS_FORCEFIELDS)
            raise ValueError(err)
        return ff

    return get_ffname()


def read_attract_parameters(path):
    """Read attract parameter file.

    Args:
        path (str): path to attract parameter file.

    Returns:
        nbminim (int): number of minimizations to perform.
        lignames (list[str])
        minimlist (list[dict[str, (int or float)]])
        rstk (float)
    """

    def read_number_of_minimizations():
        try:
            nbminim = int(lines.pop(0).split()[0])
        except:
            error = 'Cannot read number of minimizations from attract parameter file'
            raise ValueError(error)
        return nbminim

    def read_lignames():
        def get_tokens():
            try:
                tokens = lines.pop(0).split()
            except:
                error = 'Unexpectedly reached end of attract parameter file'
                raise ValueError(error)
            return tokens
        lignames = []
        tokens = get_tokens()
        while tokens and tokens[0] == 'Lig':
            lignames.append(tokens[2])
            tokens = get_tokens()
        return lignames, tokens

    def read_rstk():
        try:
            rstk = float(tokens[3])
        except:
            error = 'Cannot read rstk from attract parameter file'
            raise ValueError(error)
        return rstk

    def read_minimization():
        try:
            tokens = lines.pop(0).split()
        except:
            error = 'Cannot read minimizations from attract parameter file: '\
                    'expected {}, found {}'.format(nbminim, i)
            raise ValueError(error)
        if len(tokens) < 3:
            error = 'Cannot read minimization line from attract parameter file: '\
                    'expected at least 3 values, found {}'.format(len(tokens))
            raise ValueError(error)
        minim = {'maxiter': int(tokens[0]),
                 'squarecutoff': float(tokens[-1]),
                 'rstk': rstk if tokens[-2] == '1' else 0.0}
        return minim

    # Read file ignoring comments.
    with open(path, 'rt') as f:
        lines = [line for line in f if not line[0] in ('#', '!')]

    # First number is the number of minimizations to perform.
    nbminim = read_number_of_minimizations()

    # Read ligand list which are all lines starting with 'Lig'.
    lignames, tokens = read_lignames()

    # Read rstk.
    rstk = read_rstk()

    # Read minimization list.
    minimlist = []
    for i in range(nbminim):
        minimlist.append(read_minimization())

    return nbminim, lignames, minimlist, rstk
