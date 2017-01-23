
"""ptools.exceptions - Defines PTools specific exceptions."""


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


class BeadCreationError(Exception):
    """Base class raised when an error is encountered when reducing
    an atomtic topology to a coarse grain topology."""
    def __init__(self, bead):
        self.bead = bead
        self.resname = bead.atoms[0].residType
        self.resid = bead.atoms[0].residId
        msg = 'error creating bead for residue {}:{}'
        msg = msg.format(self.resname, self.resid)
        super(BeadCreationError, self).__init__(msg)


class IncompleteBeadError(BeadCreationError):
    pass
