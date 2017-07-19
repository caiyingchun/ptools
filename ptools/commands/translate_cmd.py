
"""PTools translate command."""

from __future__ import print_function

import os
import sys

import ptools

# Path to default solvation parameter file.
SOLVATION_PARAMETER_FILE = os.path.join(ptools.DATA_DIR, 'aminon.par')

# PDB format.
PDB_FMT = "ATOM %(atomid)6d %(atomname)5s %(resname)3s %(resid)4d    "\
          "%(x)8.3f%(y)8.3f%(z)8.3f"


def create_subparser(parent):
    """Create translate command argument parser."""
    parser = parent.add_parser('translate', help=__doc__)
    parser.set_defaults(func=run)

    parser.add_argument('receptor',
                        help="path to receptor topology file")
    parser.add_argument('ligand',
                        help="path to ligand topology file")
    parser.add_argument('-d', '--density', type=float, default=10.0,
                        help="distance (in Angstrom) between starting points. "
                             "The value must be > 1.0 (default is 10.0).")

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--distance-to-receptor', type=float,
                       help="minimum distance (in Angstrom) between starting "
                            "points and the receptor surface. "
                            "Default is the ligand radius.")
    group.add_argument('--distance-to-receptor-factor', type=float, default=1.0,
                       help="minimum distance (in Angstrom) between starting "
                            "points and the receptor surface. "
                            "Multiply the ligand radius by this factor.")
    parser.add_argument('-o', '--output',
                        help='path to output file (default=stdout)')


def write_grid_to_pdb(grid, fp):
    """Write grid to PDB file.

    Args:
        grid (ptools.Rigidbody): grid
        fp (file): file pointer to output file
    """
    for i in xrange(len(grid)):
        coords = grid.getCoords(i)
        print(PDB_FMT % {'atomid': i + 1,
                         'atomname': 'POSI',
                         'resname': 'PRO',
                         'resid': i + 1,
                         'x': coords.x,
                         'y': coords.y,
                         'z': coords.z},
              file=fp)


def run(args):
    # Check input files exist.
    ptools.io.check_file_exists(SOLVATION_PARAMETER_FILE)
    ptools.io.check_file_exists(args.receptor)
    ptools.io.check_file_exists(args.ligand)

    # Read input topologies.
    rec = ptools.Rigidbody(args.receptor)
    lig = ptools.Rigidbody(args.ligand)

    # Distance to receptor.
    distance_to_receptor = args.distance_to_receptor or lig.Radius()
    distance_to_receptor *= args.distance_to_receptor_factor

    # Initialize surface.
    surf = ptools.Surface(30, 30, SOLVATION_PARAMETER_FILE)
    surf.surfpointParams(5000, distance_to_receptor)

    # Generate grid points.
    grid = surf.surfpoint(rec, 1.4)

    # Remove points too clore from the receptor.
    outergrid = surf.outergrid(grid, rec, distance_to_receptor)
    outergrid = surf.removeclosest(outergrid, args.density)

    # Generate output PDB.
    if args.output:
        with open(args.output, 'wt') as f:
            write_grid_to_pdb(outergrid, f)
    else:
        write_grid_to_pdb(outergrid, sys.stdout)
