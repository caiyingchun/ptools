
"""reduce_cmd - PTools reduce command."""

from __future__ import print_function

import ptools


def create_attract1_subparser(parent):
    parser = parent.add_parser('attract1',
                               help='reduce using the attract1 force field')
    parser.set_defaults(forcefield='attract1')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--prot', action='store_true', dest='molProt',
                       help='reduce protein')
    group.add_argument('--dna', action='store_true', dest='molDNA',
                       help='reduce DNA')


def create_attract2_subparser(parent):
    parser = parent.add_parser('attract2',
                               help='reduce using the attract2 force field')
    parser.set_defaults(forcefield='attract2')


def create_scorpion_subparser(parent):
    parser = parent.add_parser('scorpion',
                               help='reduce using the scorpion force field')
    parser.set_defaults(forcefield='scorpion')
    parser.add_argument('--cgopt', dest='optimizedcharges', action='store_true',
                        help='if present, optimize bead charges')
    parser.add_argument('--delgrid', type=float, default=1.5,
                        help='grid spacing (A) for charge optimization'
                             '(default is 1.5), works only with --cgopt '
                             'option')


def create_subparser(parent):
    parser = parent.add_parser('reduce', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('pdb',
                        help="path to input PDB file (atomistic resolution)")
    parser.add_argument('--red', dest='redName',
                        help="path to correspondance file between atoms "
                             "and beads file")
    parser.add_argument('--conv', dest='convName',
                        default=ptools.reduce.DEFAULT_NAME_CONVERSION_YML,
                        help="path type conversion file")
    parser.add_argument('-o', '--output',
                        help='path to output file (default=stdout)')
    parser.add_argument('--ignore-error', nargs='?', default=[],
                        action='append',
                        choices=ptools.exceptions.residue_reduction_errors() + ['all'],
                        help="skip residue when error occurs "
                             "(by default the program crashes by raising the "
                             "appropriate exception)")

    subparsers = parser.add_subparsers()
    create_attract1_subparser(subparsers)
    create_attract2_subparser(subparsers)
    create_scorpion_subparser(subparsers)


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
            else:
                err = "one of the arguments --prot --dna is required "\
                      "when not using --red option"
                ptools.io.critical(err, exitstatus=2)
        elif args.forcefield == 'attract2':
            return ptools.reduce.DEFAULT_ATTRACT2_REDUCTION_YML
        elif args.forcefield == 'scorpion':
            return ptools.reduce.DEFAULT_SCORPION_REDUCTION_YML
    return args.redName


def run(args):
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
