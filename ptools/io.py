from __future__ import print_function

import os
import sys

from .forcefield import PTOOLS_FORCEFIELDS


class FileParsingError(Exception):
    """Exception raised when the parsing of a file fails."""
    def __init__(self, filename, message, line='', lineid=None):
        fmt = '%(filename)s:'
        if lineid is not None:
            fmt += '%(lineid)d:'
        fmt += ' error: %(message)s'
        if line:
            fmt += "\n%(line)r"
        super(FileParsingError, self).__init__(fmt % vars())


# def _log(*args, prefix='', end='\n', file=sys.stderr, flush=False, sep=' '):
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
            err = err.format(path, PTOOLS_FORCEFIELDS)
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
