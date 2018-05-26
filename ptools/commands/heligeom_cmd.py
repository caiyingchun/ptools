
"""heligeom_cmd - PTools heligeom command."""

from __future__ import print_function

import math
import string
import sys

import ptools

import ptools.heligeom as heligeom


def create_subparser(parent):
    parser = parent.add_parser('heligeom', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('monomer1.pdb',
                        help="first monomer input file")
    parser.add_argument('monomer2.pdb',
                        help="second monomer input file")
    parser.add_argument('-n', '--number-of-new-monomers', type=int, default=0,
                        help="number of new monomer you want to add to make "
                             "a helicoidal structure")
    parser.add_argument('-o', '--output', default='print',
                        help="output file name")
    parser.add_argument('-Z', '--align-on-z', action='store_true',
                        help="align output PDB on the Z-axis")
    parser.add_argument('-s', '--seq', action='store_true',
                        help="the pdb file is written sequentially, which "
                        "enables generating very long helices without "
                        "creating memory issues. "
                        "This option is valid only when printing on "
                        "the standard output")
    parser.add_argument('--groove', action='store_true',
                        help="producess a file groove.out containing groove "
                             "width values at successive points around the "
                             "axis separated by 0.5 degrees")


def check_args(args):
    """Check input files exists and command-line arguments
    self-compatibility."""

    # Check monomer input PDB files exist.
    ptools.io.check_file_exists(getattr(args, 'monomer1.pdb'))
    ptools.io.check_file_exists(getattr(args, 'monomer2.pdb'))

    # Check command-line arguments self-compatibility.
    if args.align_on_z and not args.number_of_new_monomers:
        ptools.io.error("Option '--align-on-z only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.seq and not args.number_of_new_monomers:
        ptools.io.error("Option '--seq only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.output and not args.number_of_new_monomers:
        ptools.io.error("Option '--output only valid in conjunction with "
                        "--number-of-new-monomers")

    if args.seq and args.output != 'print':
        ptools.io.error("Option '--seq only valid when --output is 'print'")


def run(args):
    check_args(args)
    monomer1 = getattr(args, 'monomer1.pdb')
    monomer2 = getattr(args, 'monomer2.pdb')

    N = args.number_of_new_monomers

    mono1 = ptools.Rigidbody(monomer1)
    mono2 = ptools.Rigidbody(monomer2)
    hp = heligeom.heli_analyze(mono1, mono2, True)

    if N > 0:
        # Construct and output PDB to screen
        heligeom.heli_construct(mono1, hp, N, args.align_on_z, args.seq, args.output)

    if args.groove:
        heligeom.groove_width_calculation(hp, mono1)
