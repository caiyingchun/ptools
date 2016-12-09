
"""PTools attract command."""


from __future__ import print_function


def create_subparser(parent):
    parser = parent.add_parser('attract', help=__doc__)
    parser.set_defaults(func=run)
    parser.add_argument('-r', '--receptor', dest='receptor_name',
                        help="name of the receptor file")
    parser.add_argument('-l', '--ligand', dest='ligand_name',
                        help="name of the ligand file")
    parser.add_argument('-s', '--single', action='store_true',
                        help="single minimization mode")
    parser.add_argument('--ref', dest='reffile',
                        help="reference ligand for rmsd")
    parser.add_argument('-t', '--translation', type=int, dest='transnb',
                        help="translation number (distributed mode) starting "
                              "from 0 for the first one!")
    parser.add_argument('--start1', action='store_true',
                        help="(only useful with -t), use 1 for the first "
                             "translation point")



def run(args):
    print("This is attract - Not implemented yet")
    
