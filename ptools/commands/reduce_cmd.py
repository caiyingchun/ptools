
"""reduce_cmd - PTools reduce command."""

from __future__ import print_function

import sys

import ptools


def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)

    # Global arguments.
    parser.add_argument('pdb',
                        help="path to input PDB file (atomistic resolution)")
    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms "
                             "and beads file")
    parser.add_argument('--conv', dest='convName',
                        default=ptools.reduce.DEFAULT_NAME_CONVERSION_YML,
                        help="path type conversion file")
    parser.add_argument('-o', '--output',
                        help="path to output file (default=stdout)")
    parser.add_argument('--ignore-error', nargs='?', default=[],
                        action='append',
                        choices=ptools.exceptions.residue_reduction_errors() + ['all'],
                        help="skip residue when error occurs "
                             "(by default the program crashes by raising the "
                             "appropriate exception)")

    parser.add_argument('--ff', choices=['attract1', 'attract2', 'scorpion'],
                        default='attract1', dest='forcefield',
                        help="reduction model (force field; default='attract1')")

    # Attract1 options.
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prot', action='store_true', dest='molProt',
                       help='reduce protein')
    group.add_argument('--dna', action='store_true', dest='molDNA',
                       help="reduce DNA")

    # Scorpion options.
    parser.add_argument('--cgopt', dest='optimizedcharges', action='store_true',
                        help="if present, optimize bead charges")
    parser.add_argument('--delgrid', type=float, default=1.5,
                        help="grid spacing (A) for charge optimization"
                             "(default is 1.5), works only with --cgopt "
                             "option")


def parse_args(args):
    """Check that command-line arguments are valid.

    Check that the options uses are compatible with the force field used.
    Also makes '--prot' option default if attract1 force field was required.

    Args:
        args (argparse.Namespace): input arguments
    """
    # Attract1-specific options.
    if (args.molProt or args.molDNA) and args.forcefield != 'attract1':
        ptools.io.critical("option --prot and --dna are valid only with "
                           "--ff=attract1",
                           exitstatus=2)

    if args.forcefield == 'attract1' and not (args.molProt or args.molDNA):
        ptools.io.critical("one of the arguments --prot --dna is required "
                           "when not using --red option",
                           exitstatus=2)

    # Scorpion-specific options.
    if '--cgopt' in sys.argv and args.forcefield != 'scorpion':
        ptools.io.critical("option --cgopt requires --ff=scorpion",
                           exitstatus=2)

    if '--delgrid' in sys.argv and args.forcefield != 'scorpion':
        ptools.io.critical("option --delgrid requires --ff=scorpion",
                           exitstatus=2)


def get_reduction_data_path(args):
    """Return path to reduction data file.

    Reduction data file can be provided from the '--red' option.

    Returns:
        str: path to reduction parameter file.
    """
    if not args.redName:
        if args.forcefield == 'attract1':
            if args.molProt:
                return ptools.reduce.DEFAULT_ATTRACT1_PROT_REDUCTION_YML
            elif args.molDNA:
                return ptools.reduce.DEFAULT_ATTRACT1_DNA_REDUCTION_YML
        elif args.forcefield == 'attract2':
            return ptools.reduce.DEFAULT_ATTRACT2_REDUCTION_YML
        elif args.forcefield == 'scorpion':
            return ptools.reduce.DEFAULT_SCORPION_REDUCTION_YML
    return args.redName


def run(args):
    parse_args(args)

    redname = get_reduction_data_path(args)
    convname = args.convName
    atomicname = args.pdb

    ptools.io.check_file_exists(redname)
    ptools.io.check_file_exists(convname)
    ptools.io.check_file_exists(atomicname)

    reducer = ptools.reduce.Reducer(atomicname, redname)
    reducer.name_conversion_file = convname

    # Convert exception list of names as list of classes.
    if 'all' in args.ignore_error:
        args.ignore_error = ptools.exceptions.residue_reduction_errors()
    ignore_exceptions = ptools.exceptions.exception_names_to_exception_list(args.ignore_error)
    reducer.reduce(ignore_exceptions=ignore_exceptions)

    if args.forcefield == 'scorpion':
        # If force field is scorpion, first CA bead's charge is +1 and
        # last CA bead's charge is -1.
        ca_beads = [bead for bead in reducer.beads if bead.name == 'CA']
        ca_beads[0].charge = 1.0
        ca_beads[-1].charge = -1.0

        # If force field is scorption, bead charges can be optimized thanks
        # to cgopt.
        if args.optimizedcharges:
            reducer.optimize_charges(args.delgrid)

    reducer.print_output_model(args.output)
