
"""ptools.exceptions - Defines PTools specific exceptions."""

from __future__ import print_function

import collections
import inspect
import sys


class FileParsingError(Exception):
    """Exception raised when the parsing of a file fails.

    Args:
        filename (str): path to file being parsed.
        message (str): error message.
        line (str): line where error has been found.
        lineid (int): line number where the error has been found.
    """
    def __init__(self, filename, message, line='', lineid=None):
        fmt = '%(filename)s:'
        if lineid is not None:
            fmt += '%(lineid)d:'
        fmt += ' error: %(message)s'
        if line:
            fmt += "\n%(line)r"
        super(FileParsingError, self).__init__(fmt % vars())


class ResidueReductionError(Exception):
    """Base class for an exception raised when an error occured during
    the residue reduction (transformation from all-atom to coarse grain).

    Attrs:
        default_message_fmt (str): default message format.

    Args:
        resname (str): residue name.
        resid (int): residue identifier.
        kwargs dict[str]->value: any argument that will be used to format
            message.
    """
    default_message_fmt = 'in residue {self.resname}:{self.resid}'

    def __init__(self, resname, resid, message='', **kwargs):
        self.resname = resname
        self.resid = resid

        # Set attributes with attributes coming from kwargs.
        for attr, value in kwargs.items():
            if attr not in ('resname', 'resid', 'message'):
                setattr(self, attr, value)

        message = message or self.default_message_fmt
        super(ResidueReductionError, self).__init__(message.format(self=self))

    def report(self):
        return "{}: {}".format(type(self).__name__, self.message)


class NoResidueReductionRulesFoundError(ResidueReductionError):
    default_message_fmt = (ResidueReductionError.default_message_fmt +
                           ": no rule found for this residue reduction")


class BeadCreationError(ResidueReductionError):
    """Base class raised when an error is encountered when reducing
    an atomtic topology to a coarse grain topology.

    Attrs:
        bead (ptools.commands.reduce_cmd.Bead): bead where error occured.
        expected_atoms (list[str]): list of expected atom names.
        found_atoms (list[str]): list of actually found atom names.
    """
    default_message_fmt = (ResidueReductionError.default_message_fmt +
                           " in bead '{self.bead.name}'")

    def __init__(self, bead, message=''):
        self.bead = bead
        self.expected_atoms = sorted(self.bead.atom_reduction_parameters.keys())
        self.found_atoms = sorted(atom.atom_type for atom in self.bead.atoms)
        super(BeadCreationError, self).__init__(bead.resid_type, bead.resid_id,
                                                bead_name=self.bead.name)


class IncompleteBeadError(BeadCreationError):
    """Exception raised when an atom has not been found when constructing
    a bead."""
    default_message_fmt = (BeadCreationError.default_message_fmt +
                           '\n    expected atoms: {self.expected_atoms}' +
                           '\n    found atoms: {self.found_atoms}' +
                           '\n    missing atoms: {self.missing_atoms}'
                           )

    @property
    def missing_atoms(self):
        """Return the list of missing atom names."""
        return list(set(self.expected_atoms) - set(self.found_atoms))


class DuplicateAtomInBeadError(BeadCreationError):
    """Exception raised when an atom is found several times when constructing
    a bead."""
    default_message_fmt = (BeadCreationError.default_message_fmt +
                           '\n    expected atoms: {self.expected_atoms}' +
                           '\n    found atoms: {self.found_atoms}' +
                           '\n    duplicate atoms: {self.duplicate_atoms}')

    @property
    def duplicate_atoms(self):
        """Return the list of duplicate atom names."""
        counter = collections.Counter(self.found_atoms)
        return [name for name, count in counter.items() if count > 1]


class IgnoredAtomsInReducedResidueError(ResidueReductionError):
    """Exception raised when an atom from all-atom model has not been used
    in the coarse grain model.

    Attrs:
        atom_names (list[str]): names of atoms read in the topology file for
            the current residue.
        bead_atom_names (list[str]): names of atoms used for bead construction.
    """
    default_message_fmt = (ResidueReductionError.default_message_fmt +
                           ' some atoms were unused during coarse grain '
                           'modeling: {self.unused_atoms}')

    def __init__(self, residue):
        # Names of atoms sent to coarse grain residue constructor.
        self.atom_names = [atom.atom_type for atom in residue.all_atoms]

        # Names of atoms actually used in the beads.
        self.bead_atom_names = [atom.atom_type for bead in residue.beads
                                for atom in bead.atoms]

        super(IgnoredAtomsInReducedResidueError, self).__init__(residue.resname, residue.resid)

    @property
    def unused_atoms(self):
        """Return the list of unused atom names."""
        diff = set(self.atom_names) ^ set(self.bead_atom_names)
        return list(diff)


def residue_reduction_errors():
    """Return the list of ResidueReductionError subclass names."""
    return [name for name, obj in inspect.getmembers(sys.modules[__name__])
            if inspect.isclass(obj) and issubclass(obj, ResidueReductionError)]


def exception_names_to_exception_list(exception_names):
    """Return a list of exception class from the list of exception names."""
    exception_list = [eval(name) for name in exception_names]
    return exception_list
