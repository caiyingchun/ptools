
"""PTools translate command."""

from __future__ import print_function

import ptools


def create_subparser(parent):
    parser = parent.add_parser('translate', help=__doc__)
    parser.set_defaults(func=run)

    # parser.add_argument('pdb',
    #                     help="path to input PDB file (atomistic resolution)")
    # parser.add_argument('-o', '--output',
    #                     help='path to output file (default=stdout)')


def run(args):
    print("this is translate")
    print(args)
