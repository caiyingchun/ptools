
import os

import ptools
from _ptools import (AttractForceField1, Lbfgs,
                     AttractForceField2,
                     ScorpionForceField, ScorpionLbfgs)

# Force field parameter files are located in PTools data directory
# (/path/to/ptools/installdir/share/data)
ATTRACT1_FF_PARAMETER_FILE = os.path.join(ptools.DATA_DIR, 'aminon.par')
ATTRACT2_FF_PARAMETER_FILE = os.path.join(ptools.DATA_DIR, 'mbest1u.par')
SCORPION_FF_PARAMETER_FILE = os.path.join(ptools.DATA_DIR, 'scorpion.par')


# Map the force field name with parameter file, force field class and
# minimizer.
PTOOLS_FORCEFIELDS = {
    'SCORPION': {'ff_file': SCORPION_FF_PARAMETER_FILE,
                 'ff_class': ScorpionForceField,
                 'minimizer_class': ScorpionLbfgs},

    'ATTRACT1': {'ff_file': ATTRACT1_FF_PARAMETER_FILE,
                 'ff_class': AttractForceField1,
                 'minimizer_class': Lbfgs},

    'ATTRACT2': {'ff_file': ATTRACT2_FF_PARAMETER_FILE,
                 'ff_class': AttractForceField2,
                 'minimizer_class': Lbfgs},
}
