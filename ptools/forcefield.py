
from _ptools import (AttractForceField1, Lbfgs,
                     AttractForceField2,
                     ScorpionForceField, ScorpionLbfgs)


# Map the force field name with parameter file, force field class and 
# minimizer.
PTOOLS_FORCEFIELDS = {
    'SCORPION': {'ff_file': 'scorpion.par',
                 'ff_class': ScorpionForceField,
                 'minimizer_class': ScorpionLbfgs},

    'ATTRACT1': {'ff_file': 'aminon.par',
                 'ff_class': AttractForceField1,
                 'minimizer_class': Lbfgs},

    'ATTRACT2': {'ff_file': 'mbest1u.par',
                 'ff_class': AttractForceField2,
                 'minimizer_class': Lbfgs},
}

