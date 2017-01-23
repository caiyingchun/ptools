
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
