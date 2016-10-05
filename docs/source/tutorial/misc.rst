
Miscellaneous, tips and tricks
==============================

Troubleshooting
---------------

Bus error
^^^^^^^^^

On Mac OS, the command ``import ptools`` can lead to a "bus error" 
error message. This happens with MacPorts or fink versions of Python. 
A solution is to use the Python provided with the system instead 
(``/usr/bin/python``).


Accurate bead representation
----------------------------

Adjustment of van der Waals radii is recommended for a more accurate 
representation of the occupied volume. In this purpose, we provide a Pymol 
script called ``update_pymol_cg_vdw_radii.pml`` in the 
``$HOME/ptools-XX/PyAttract`` directory. Within Pymol, call this 
script with the command::

    run update_pymol_cg_vdw_radii.pml

or from the menu ``File -> Run -> select the file``.

With some representations (dots, spheres, mesh and surface), you also need 
to tell Pymol to refresh its view with the command ``rebuild``.
Coarse grain van der Waals radii have now their real values and 
reduced molecules their real volume, as shown in
:numref:`fig_real_vdw_receptor` and :numref:`fig_real_vdw_ligand`.


.. _fig_real_vdw_receptor:
.. figure:: figures/1K79_receptor.png
   :align: center

   All-atom (green mesh) and reduced (red mesh) representations of both 
   partners in the 1K79 protein--DNA complex. With the correct values of coarse grain
   van der Waals radii, both representations are equivalent. DNA.


.. _fig_real_vdw_ligand:
.. figure:: figures/1K79_ligand.png
   :align: center

   Same as above. Protein.


Minimization movie
------------------

Here is the procedure to visualize all conformations taken by the ligand during
minimizations.


1. Place the ligand at the wanted translation and rotation::

    startligand.py ligand.red translation_number rotation_number

   This will generate the file `ligand_X_Y.red` where ``X`` and ``Y`` 
   are the translation and rotation numbers, respectively.

2. Launch a docking simulation in single mode::

    attract.py receptor.red ligand_X_Y.red --ref=ligand.red -s > single.att

   The file ``minimization.trj`` is created and contains the 6 variables of
   translation and rotation for all steps of all minimizations.

3. Convert translation/rotation variables into ligand conformations::

    applytraj.py minimization.trj ligand_X_Y.red > ligand_moves.red

   The file ``ligand_moves.red`` is a multi-pdb files containing all
   conformations of the ligand at each step of the minimizations.

4. Visualize ``ligand_moves.red`` with PyMoL or VMD. For instance with Pymol::

    pymol ligand_moves.red


You could also represent the receptor::

    pymol receptor.red ligand_moves.red

