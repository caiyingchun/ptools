
"""extract_cmd - PTools extract command."""

from __future__ import print_function

import sys

import ptools


def create_subparser(parent):
    parser = parent.add_parser('extract', help=__doc__)
    parser.set_defaults(func=run)
    parser.add_argument('attract_output',
                        help='attract ouptut file')
    parser.add_argument('ligand',
                        help='ligand reduced topology')
    parser.add_argument('transid', type=int,
                        help='id of the translation to extract')
    parser.add_argument('rotid', type=int,
                        help='id of the rotation to extract')
    parser.add_argument('-o', '--output',
                        help='output topology file name (by default print '
                             'on stout)')


def run(args):
    ptools.io.check_file_exists(args.attract_output)
    ptools.io.check_file_exists(args.ligand)

    # Get transformation matrix from attract output file.
    docking_result = ptools.io.read_attract_output(args.attract_output)
    m = docking_result.get_matrix(args.transid, args.rotid)

    # Read ligand topology and apply transformation.
    ligand = ptools.Rigidbody(args.ligand)
    ligand.apply_matrix(m)

    # Print output topology.
    header = 'REMARK 999 TRANSLATION ROTATION  {} {}'.format(args.transid,
                                                             args.rotid)
    if args.output:
        with open(args.output, 'wt') as f:
            print(header, ligand, sep='\n', file=f)
    else:
        print(header, ligand, sep='\n', file=sys.stdout)
