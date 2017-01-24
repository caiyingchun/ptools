
"""ptools.exceptions - Defines PTools specific exceptions."""


import collections
import string


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
    the residue reduction (transformation from all-atom to coarse grain)."""

    default_message_fmt = 'error reducing residue {resname}:{resid}'

    def __init__(self, resname, resid, message='', **kwargs):
        self.resname = resname
        self.resid = resid
        self._message = message or self.default_message_fmt

        # Set attributes with attributes coming from kwargs.
        for attr, value in kwargs.items():
            if attr not in ('resname', 'resid', 'message'):
                setattr(self, attr, value)

        super(ResidueReductionError, self).__init__(self._format_message())

    def _format_message(self):
        fmt = string.Formatter()
        attrs = [field_name
                 for (text, field_name, format_spec, conversion)
                 in fmt.parse(self._message)]
        values = {attr: getattr(self, attr) for attr in attrs}
        return self._message.format(**values)


class BeadCreationError(ResidueReductionError):
    """Base class raised when an error is encountered when reducing
    an atomtic topology to a coarse grain topology."""

    default_message_fmt = (ResidueReductionError.default_message_fmt +
                           "\n  error creating bead '{bead_name}'")

    def __init__(self, bead, message=''):
        self.bead = bead
        self.expected_atoms = sorted(self.bead.atom_reduction_parameters.keys())
        self.found_atoms = sorted(atom.atomType for atom in self.bead.atoms)
        super(BeadCreationError, self).__init__(bead.residType, bead.residId,
                                                bead_name=self.bead.name)


class IncompleteBeadError(BeadCreationError):
    default_message_fmt = (BeadCreationError.default_message_fmt +
                           '\n    expected atoms: {expected_atoms}' +
                           '\n    found atoms: {found_atoms}'+
                           '\n    missing atoms: {missing_atoms}'
                           )

    @property
    def missing_atoms(self):
        return list(set(self.expected_atoms) - set(self.found_atoms))


class DuplicateAtomInBeadError(BeadCreationError):
    default_message_fmt = (BeadCreationError.default_message_fmt +
                       '\n    expected atoms: {expected_atoms}' +
                       '\n    found atoms: {found_atoms}'+
                       '\n    duplicate atoms: {duplicate_atoms}')

    @property
    def duplicate_atoms(self):
        counter = collections.Counter(self.found_atoms)
        return [name for name, count in counter.items() if count > 1]

