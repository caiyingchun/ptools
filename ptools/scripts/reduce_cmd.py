
"""PTools reduce command."""

from __future__ import print_function

import argparse
import os
import sys

import ptools


DEFAULT_PROT_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.prot.dat')
DEFAULT_DNA_REDUCTION_DATA = os.path.join(ptools.DATA_DIR, 'at2cg.dna.dat')
DEFAULT_FF_PARAM_DATA = os.path.join(ptools.DATA_DIR, 'ff_param.dat')
DEFAULT_CONVERSION_DATA = os.path.join(ptools.DATA_DIR, 'type_conversion.dat')


def create_attract1_subparser(parent):
    parser = parent.add_parser('attract1',
                               help='reduce using the attract1 force field')
    parser.set_defaults(forcefield='attract1')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prot', action='store_true', dest='molProt',
                       help='reduce protein')
    group.add_argument('--dna', action='store_true', dest='molDNA',
                       help='reduce DNA')

    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms and beads file")
    parser.add_argument('--ff', dest='ffName',
                        default=DEFAULT_FF_PARAM_DATA,
                        help="path to force field parameter file")
    parser.add_argument('--conv', dest='convName',
                        default=DEFAULT_CONVERSION_DATA,
                        help="path type conversion file")
    parser.add_argument('--allow_missing', action='store_true',
                        dest='warning',
                        help="don't stop program if atoms are missing, "
                             "only display a warning on stderr")



def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('pdb',
                        help="path to input PDB file (atomistic resolution)")

    subparsers = parser.add_subparsers()
    create_attract1_subparser(subparsers)

    
def get_reduction_data_path(args):
    """Return path to reduction data file.

    Reduction data file can be provided from the '--red' option.
    If it is not, 
     which depends on whether the input
    file is protein or DNA and the path to a custom parameter file was
    provided or not."""
    if not args.redName:
        if args.molProt:
            return DEFAULT_PROT_REDUCTION_DATA
        elif args.molDNA:
            return DEFAULT_DNA_REDUCTION_DATA
        else:
            err = "error: one of the arguments --prot --dna is required when "\
                  "not using --red option"
            print(err, file=sys.stderr)
            sys.exit(2)
    return args.redName


def run(args):
    print("This is reduce")
    
    redname = get_reduction_data_path(args)
    ffname = args.ffName
    convname = args.convName
    atomicname = args.pdb

    ptools.io.check_file_exists(redname)
    ptools.io.check_file_exists(ffname)
    ptools.io.check_file_exists(convname)
    ptools.io.check_file_exists(atomicname)


    
    
