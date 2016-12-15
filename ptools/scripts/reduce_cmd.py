
"""PTools reduce command."""

from __future__ import print_function

import os
import sys

import ptools


DEFAULT_PROT_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.prot.dat')
DEFAULT_DNA_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.dna.dat')


def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)
    subparsers = parser.add_subparsers()

    parser_attract1 = subparsers.add_parser('attract1',
                                            help='reduce using the attract1 force field')

    parser_attract1.add_argument('--prot', action='store_true', dest='molProt',
                                 help='reduce protein')
    parser_attract1.add_argument('--dna', action='store_true', dest='molDNA',
                                 help='reduce DNA')
    parser_attract1.add_argument('--red', dest='redName',
                                 help="correspondance file between atoms and beads")
    parser_attract1.add_argument('--conv', dest='convName',
                                 help="type conversion file")
    parser_attract1.add_argument('--allow_missing', action='store_true',
                                 dest='warning',
                                 help="don't stop program if atoms are missing, "
                                      "only display a warning on stderr")



def run(args):
    print("This is reduce")
    print(DEFAULT_DNA_REDUCTION_DATA)
    print(os.path.exists(DEFAULT_DNA_REDUCTION_DATA))    

