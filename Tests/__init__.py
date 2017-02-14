

import os

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


# ---------------------------------------------------------------------------
#
# Single minimization test files
#
# ---------------------------------------------------------------------------
TEST_SINGLEMINIM_DATA_DIR = os.path.join(TEST_DATA_DIR, 'singleminim')
TEST_SINGLEMINIM_FF_PARAM = os.path.join(TEST_SINGLEMINIM_DATA_DIR, 'aminon.par')
TEST_SINGLEMINIM_ATTRACT_INP = os.path.join(TEST_SINGLEMINIM_DATA_DIR, 'attract.inp')
TEST_SINGLEMINIM_LIGAND = os.path.join(TEST_SINGLEMINIM_DATA_DIR, 'ligand.red')
TEST_SINGLEMINIM_RECEPTOR = os.path.join(TEST_SINGLEMINIM_DATA_DIR, 'receptor.red')
TEST_SINGLEMINIM_MINIMIZATION_OUT = os.path.join(TEST_SINGLEMINIM_DATA_DIR, 'minimization.trj')


# ---------------------------------------------------------------------------
#
# Reduce test files
#
# ---------------------------------------------------------------------------
TEST_REDUCE_DATA_DIR = os.path.join(TEST_DATA_DIR, 'reduce')
TEST_LIGAND_PDB = os.path.join(TEST_REDUCE_DATA_DIR, '1FIN_r.pdb')

# Attract1 reduced topology.
# Generated from f46b895 with:
#   python reduce_attract1.py --prot 1FIN_r.pdb > 1FIN_r.attract1.red
TEST_LIGAND_RED_ATTRACT1 = os.path.join(TEST_REDUCE_DATA_DIR, '1FIN_r.attract1.red')


# Attract2 reduced topology.
# Generated from f46b895 with:
#   python reduce_attract2.py 1FIN_r.pdb > 1FIN_r.attract2.red
TEST_LIGAND_RED_ATTRACT2 = os.path.join(TEST_REDUCE_DATA_DIR, '1FIN_r.attract2.red')


# Scorpion reduced topology.
# Generated from f46b895 with:
#   python reduce_scorpion.py 1FIN_r.pdb > 1FIN_r.scorpion.red
# Input topology has been adapted to acomodate the fact that reduce_scorpion.py
# did not handle OT2 atoms: last atom from 1FIN_r.pdb has been renamed OT2 => OT.
TEST_LIGAND_RED_SCORPION = os.path.join(TEST_REDUCE_DATA_DIR, '1FIN_r.scorpion.red')


# Scorpion reduced topology with optimized charges.
# Generated from f46b895 with:
#   python reduce_scorpion.py --cgopt 1FIN_r.pdb > 1FIN_r.scorpion.red
# Input topology has been adapted to acomodate the fact that reduce_scorpion.py
# did not handle OT2 atoms: last atom from 1FIN_r.pdb has been renamed OT2 => OT.
TEST_LIGAND_RED_SCORPION_CGOPT = os.path.join(TEST_REDUCE_DATA_DIR, '1FIN_r.scorpion_cgopt.red')


# ---------------------------------------------------------------------------
#
# Translate test files
#
# ---------------------------------------------------------------------------

# translate.py output.
# Generated from f46b895 with:
#   python translate.py 1FIN_r.attract1.red 1FIN_r.attract1.red > 1FIN_r_attract1_1FIN_r_attract1_translate.out
TEST_TRANSLATE_OUTPUT = os.path.join(TEST_DATA_DIR, '1FIN_r_attract1_1FIN_r_attract1_translate.out')


TEST_ATTRACT_PARAMS = os.path.join(TEST_DATA_DIR, 'attract.inp')
TEST_ATTRACT_PARAMS_WITH_LIGAND = os.path.join(TEST_DATA_DIR, 'attract_ligand.inp')
TEST_AMINON = os.path.join(TEST_DATA_DIR, 'aminon.par')


# Example of a reduced PDB (RED) file content.
TEST_DUM_RED_CONTENT = """\
HEADER    ATTRACT1 REDUCED PDB FILE
ATOM      1 CA   CYS     1      12.025  21.956  13.016    1   0.000 0 0
ATOM      2 CSE  CYS     1      11.702  23.345  13.055    7   0.000 0 0
ATOM      3 CA   GLY     2      12.408  20.728  16.555    1   0.000 0 0
ATOM      4 CA   VAL     3      11.501  17.132  16.643    1   0.000 0 0
ATOM      5 CSE  VAL     3      10.112  16.917  16.247   29   0.000 0 0
ATOM      6 CA   PRO     4      14.215  14.528  17.062    1   0.000 0 0
ATOM      7 CSE  PRO     4      14.229  15.158  18.286   22   0.000 0 0
ATOM      8 CA   ALA     5      13.919  11.330  15.124    1   0.000 0 0
ATOM      9 CSE  ALA     5      14.424  11.148  14.581    2   0.000 0 0
"""


# Equivalent to TEST_DUM_RED_CONTENT in PDB format.
TEST_DUM_PDB_CONTENT = """\
ATOM      1  N   CYS E   1      11.377  21.513  11.770  1.00  7.18           N
ATOM      2  CA  CYS E   1      12.025  21.956  13.016  1.00  5.40           C
ATOM      3  C   CYS E   1      11.406  21.350  14.300  1.00  6.41           C
ATOM      4  O   CYS E   1      10.216  21.020  14.517  1.00  5.73           O
ATOM      5  CB  CYS E   1      12.168  23.454  12.852  1.00  3.26           C
ATOM      6  SG  CYS E   1      10.913  24.625  13.296  1.00  2.00           S
ATOM      7  N   GLY E   2      12.379  21.161  15.213  1.00  6.48           N
ATOM      8  CA  GLY E   2      12.408  20.728  16.555  1.00  5.36           C
ATOM      9  C   GLY E   2      11.698  19.535  17.075  1.00  5.75           C
"""

# Example of an attract force field parameter file content.
TEST_AMINON_CONTENT = """\
    1  2.000  1.000  0
    2  1.900  1.000  0
    3  1.950  2.000  0
    4  1.900  0.600  0
    5  1.900  0.600  0
"""


def assertCoordsAlmostEqual(testcase, source, target, places=6):
    """Assert that two `ptools.Coord3D` instances are almost equal.

    Args:
        testcase (unittest.TestCase): provides regular
            `testcase.assertAlmostEqual` method
        source (ptools.Coord3D): tested coordinates
        target (ptools.Coord3D): reference coordinates
        places (int): equivalent to unittest.TestCase.assertAlmostEqual
            places argument (see original documentation)
    """
    testcase.assertAlmostEqual(source.x, target.x, places=places)
    testcase.assertAlmostEqual(source.y, target.y, places=places)
    testcase.assertAlmostEqual(source.z, target.z, places=places)
