
"""PTools command-line script."""


from __future__ import print_function

import argparse

import ptools

from . import attract_cmd
from . import hello_cmd
from . import reduce_cmd


def parse_command_line():
    parser = argparse.ArgumentParser(description=__doc__,
                                     version=ptools.__version__)
    subparsers = parser.add_subparsers()
    hello_cmd.create_subparser(subparsers)
    attract_cmd.create_subparser(subparsers)
    reduce_cmd.create_subparser(subparsers)
    return parser.parse_args()


def main():
    args = parse_command_line()
    args.func(args)


if __name__ == "__main__":
    main()
