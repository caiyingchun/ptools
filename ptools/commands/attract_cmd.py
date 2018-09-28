
"""PTools attract command."""


from __future__ import print_function

import datetime

import ptools
import ptools.docking as docking


def create_subparser(parent):
    parser = parent.add_parser('attract', help=__doc__)
    parser.set_defaults(func=run)
    parser.add_argument('-r', '--receptor', dest='receptor_name', required=True,
                        help="name of the receptor file")
    parser.add_argument('-l', '--ligand', dest='ligand_name', required=True,
                        help="name of the ligand file")
    parser.add_argument('--ref', dest='reffile',
                        help="reference ligand for rmsd")
    parser.add_argument('-c', '--conf', default='attract.inp',
                        help="attract configuration file "
                             "(default=attract.inp)")
    parser.add_argument('-p', '--param',
                        help="attract force field parameter file "
                             "(default=default force field file)")
    parser.add_argument("--ngroups", action="store", type=int,
                        default=1,
                        help="Desired number of divisions of translations file")
    parser.add_argument("--ngroup", action="store", type=int,
                        default=1,
                        help="Which translation group (1 <= ngroup <= ngroups) "
                             "to run (requires --ngroups)")
    parser.add_argument('-s', '--start-config-only', dest='startconfig', action='store_true',
                        help="minimize starting configuration only")
    parser.add_argument('--translation', type=int, dest='transnb',
                        default=None,
                        help="minimize for the provided translation number")
    parser.add_argument('--rotation', type=int, dest='rotnb',
                        default=None,
                        help="minimize for the given rotation number")


def run(args):
    print("""
**********************************************************************
**                                                                  **
**                ATTRACT  (Python edition)                         **
**                based on the PTools library                       **
**                                                                  **
**********************************************************************
PTools revision {}

""".format(ptools.__version__))

    time_start = datetime.datetime.now()
    print("Start time:", time_start)

    print("Reading parameters file: {}".format(args.conf))
    nbminim, lignames, minimlist, rstk = ptools.io.read_attract_parameters(args.conf)
    print("{} series of minimizations".format(nbminim))
    print("rstk = ", rstk)

    ff_name = ptools.io.check_ff_version_match(args.receptor_name, args.ligand_name)
    ff_specs = ptools.forcefield.PTOOLS_FORCEFIELDS[ff_name]
    if args.param:
        ff_specs['ff_file'] = args.param

    # Load receptor and ligand.
    rec = ptools.Rigidbody(args.receptor_name)
    rec = ptools.AttractRigidbody(rec)
    lig = ptools.Rigidbody(args.ligand_name)
    lig = ptools.AttractRigidbody(lig)
    print("Read receptor (fixed): {} with {} particules".format(args.receptor_name, len(rec)))
    print("Read ligand (mobile): {} with {} particules".format(args.ligand_name, len(lig)))

    if args.reffile:
        ref = ptools.Rigidbody(args.reffile)
        print("Read reference file: {} with {} particules".format(args.reffile, len(ref)))
    else:
        ref = None

    if args.startconfig:
        print("Minimize from starting configuration")
        # Use transnb, rotnb = 0, 0 to indicate this
        translations = {0: lig.find_center()}
        rotations = {0: (0, 0, 0)}
    else:
        ptools.io.check_file_exists('rotation.dat', "rotation file 'rotation.dat' is required.")
        ptools.io.check_file_exists('translation.dat', "translation file 'translation.dat' is required.")
        translations = docking.read_translations()
        rotations = docking.read_rotations()

    # CHR some logic re-worked. "single" now used to indicate any minimization
    # run from a single configuration-- either the start config or a specified
    # transnb and rotnb.

    single = args.startconfig or (args.transnb is not None and args.rotnb is not None)

    if single:
        # Save detailed data to files
        print("Single minimization run")
        ftraj = open('minimization.trj', 'wt')
    else:
        ftraj = None

    printFiles = True
    if args.transnb is not None:
        # Limit to desired translation (translations dictionary is keyed by translation number)
        ntrans = len(translations)
        translations = {args.transnb: translations[args.transnb]}
        # CHR Keep the following, but I don't know what s for
        if args.transnb != ntrans - 1:
            # don't append (print?) ligand, receptor, etc.
            # unless this is the last translation point of the simulation
            printFiles = False

    if args.rotnb is not None:
        # Limit to desired rotation (rotation dictionary is keyed by rotation number)
        rotations = {args.rotnb: rotations[args.rotnb]}

    # CHR Add translation list splitting
    if args.ngroups > 1:
        print("Working on translations group {:d} of {:d}".format(args.ngroup, args.ngroups))
        translations = docking.get_group(translations, args.ngroups, args.ngroup)

    # core attract algorithm
    docking.run_attract(lig, rec, translations, rotations, minimlist, ff_specs, args, ref, ftraj)

    # output compressed ligand and receptor:
    if not single and printFiles:
        print(docking.compress_file(args.receptor_name))
        print(docking.compress_file(args.ligand_name))
        print(docking.compress_file(ff_specs['ff_file']))
        print(docking.compress_file('translation.dat'))
        print(docking.compress_file('rotation.dat'))
        print(docking.compress_file('attract.inp'))

    # close trajectory file for single minimization
    if single:
        ftraj.close()
        print("Saved all minimization variables (translations/rotations) in {:s}".format(ftraj.name))

    # print end and elapsed time
    time_end = datetime.datetime.now()
    # print "Finished at: ",now.strftime("%A %B %d %Y, %H:%M")
    print("End time:", time_end)
    print("Elapsed time:", time_end - time_start)
