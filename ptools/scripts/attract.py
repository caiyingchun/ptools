
"""PTools attract command."""


from __future__ import print_function

import datetime

import ptools


def rmsdca(l1, l2):
    """Return the RMSD between the alpha-carbone atom of two RigidBody
    instances."""
    return ptools.Rmsd(l1.CA().CreateRigid(), l2.CA().CreateRigid())


def create_subparser(parent):
    parser = parent.add_parser('attract', help=__doc__)
    parser.set_defaults(func=run)
    parser.add_argument('-r', '--receptor', dest='receptor_name', required=True,
                        help="name of the receptor file")
    parser.add_argument('-l', '--ligand', dest='ligand_name', required=True,
                        help="name of the ligand file")
    parser.add_argument('--ref', dest='reffile',
                        help="reference ligand for rmsd")
    parser.add_argument('--start1', action='store_true',
                        help="(only useful with -t), use 1 for the first "
                             "translation point")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--single', action='store_true',
                        help="single minimization mode")
    group.add_argument('-t', '--translation', type=int, dest='transnb',
                        help="translation number (distributed mode) starting "
                              "from 0 for the first one!")


def run(args):
#     print("""
# **********************************************************************
# **                                                                  **
# **                ATTRACT  (Python edition)                         **
# **                based on the PTools library                       **
# **                                                                  **
# **********************************************************************
# PTools revision {}

# """.format(ptools.__version__))

    # time_start = datetime.datetime.now()
    # print("Start time:", time_start)

    # print("Reading parameters file: attract.inp")
    # nbminim, lignames, minimlist, rstk = ptools.io.read_attract_parameters("attract.inp")
    # print("rstk = ", rstk)

    ff_name = ptools.io.check_ff_version_match(args.receptor_name, args.ligand_name)
    ff_specs = ptools.forcefield.PTOOLS_FORCEFIELDS[ff_name]

    # Load receptor and ligand.
    rec = ptools.AttractRigidbody(args.receptor_name)
    lig = ptools.AttractRigidbody(args.ligand_name)
    # print("Read receptor (fixed): {} with {} particules".format(args.receptor_name, len(rec)))
    # print("Read ligand (mobile): {} with {} particules".format(args.ligand_name, len(lig)))

    # Save all minimization variables to trajectory file.
    trjname = 'minimization.trj'
    if args.single:
        ftraj = open(trjname, 'wt')

    if args.reffile:
        ref = ptools.Rigidbody(args.reffile)
        print("Read reference file: {} with {} particules".format(args.reffile, len(ref)))
        refca = ref.CA()
        if len(refca) == 0:  # No C alpha atom, ligand is probably a dna
            Rmsd_alias = ptools.Rmsd
            print("No Calpha atom found for ligand (DNA?). RMSD will be "
                  "calculated on all grains")
        else:
            Rmsd_alias = rmsdca


    print(ptools.Rmsd)


