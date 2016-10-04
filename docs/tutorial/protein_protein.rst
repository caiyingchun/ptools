
Protein-protein complex: 1CGI
=============================

The 1CGI complex [#]_ has two partners:

- the bovine chymotrypsinogen A: chain E, 245 residues, 1799 atoms,
- a variant of the human pancreatic secretory trypsin inhibitor: chain I, 56 residues, 440 atoms.


Extraction of the docking partners
----------------------------------

Before docking, one has to separate both partners.
This is possible with vizualisation software such as Pymol [#]_ or VMD [#]_, 
and also directly with PTools.

Within the Python interpreter, first load the PTools library::

    from ptools import *


Read the PDB file of the complex::

    pdb = Rigidbody("1CGI.pdb")


The chain selection allows the separation between chain E and I::

    selectE = pdb.SelectChainId("E")
    selectI = pdb.SelectChainId("I")

Create both chains as independant Rigidbody objects and save them in PDB files. 
The largest protein is defined as the receptor (chain E) and the smallest 
as the ligand (chain I)::

    protE = selectE.CreateRigid()
    protI = selectI.CreateRigid()
    WritePDB(protE, "receptor.pdb")
    WritePDB(protI, "ligand.pdb")

Or more quickly::

    WritePDB(selectE.CreateRigid(), "receptor.pdb")
    WritePDB(selectI.CreateRigid(), "ligand.pdb")


.. [#] http://www.rcsb.org/pdb/cgi/explore.cgi?pdbId=1CGI
.. [#] http://pymol.sourceforge.net
.. [#] http://www.ks.uiuc.edu/Research/vmd


Coarse grain reduction
----------------------

This step translates all-atom molecules into coarse grain (reduced) molecules for further docking. 

For the receptor::

    reduce.py --ff force_field [--dna] [--cgopt] [--dgrid 1.5] receptor.pdb > receptor.red

In the present case, ``receptor.red`` contains 522 beads.

For the ligand::

    reduce.py --ff force_field [--dna] [--cgopt] [--dgrid 1.5] ligand.pdb > ligand.red


In this example, ``ligand.red`` contains 126 beads.

The ``reduce.py`` script requires the following parameters:

- The ``force_field``name can be chosen among ``attract1``, ``attract2`` or ``scorpion``.
- The ``--dna`` option must be specified only if the receptor is a DNA molelcule.
  This option only works with the force field attract1.
- The ``--cgopt`` option is required if the user want to optimize the beads charges
  in order to best reproduce the electric potential around the protein [#Basdevant2007]_. 
  This option only works with the force field scorpion.
- The ``--dgrid`` option specifies the grid spacing (in Å) for the charge optimization.
  Default is 1.5 Å. 
  Works only with the \verb@--cgopt@ option.
- an input all-atom PDB file, for instance ``receptor.pdb``
- an output coarse grain file name, for instance ``receptor.red``.


The reduced files generated are PDB-like structure files that can be read by many visualization programs (Rasmol, Pymol, VMD, Chimera...). Always visualize both all-atom and coarse grain structures to check the reduction worked properly (see Fig.~\ref{1CGI_at_cg} for 1CGI).

.. \begin{figure}[htbp]
.. \center
.. {\textbf A}
.. \includegraphics*[width=0.30\textwidth]{img/1CGI_receptor.png}
.. \hspace*{2cm}
.. {\textbf B}
.. \includegraphics*[width=0.25\textwidth]{img/1CGI_ligand.png}
.. \caption{All-atom (green sticks) and reduced (red spheres) representation of 
.. both proteins in the 1CGI complex. Receptor (A) and ligand (B).}
.. \label{1CGI_at_cg}
.. \end{figure}

.. [#Basdevant2007] Basdevant, N., Borgis, D. & Ha-Duong, T. A coarse-grained protein-protein potential derived from an all-atom force field. *Journal of Physical Chemistry B* **111**, 9390-9399 (2007).


ATTRACT parameters
------------------

The parameters required for running an ATTRACT calculation are found in the
file ``attract.inp``, which typical content is:


.. code-block:: bat
   :linenos:

        6    0    0
     -34.32940  38.75490  -3.66956   0.00050
      100  2  1  1  1  0  0  0  1  9900.00
      100  2  1  1  1  0  0  0  1  1500.00
      100  2  1  1  1  0  0  0  1  1000.00
       50  2  1  1  1  0  0  0  0   500.00
       50  2  1  1  1  0  0  0  0   500.00
       50  2  1  1  1  0  0  0  0   500.00

Line 1 indicates the number of minimisations performed by ATTRACT
for each starting position (six in the present case).
The last six lines (3 - 8) are the characteristics of each minimisation.
The first column is the number of steps before the minimisation stops.
The last column is the square of the cutoff distance for the calculation of
the interaction energy between both partners.
In the present case, the simulation starts with a very large cutoff value of
9900 Å\ :sup:`2` (≈ 99 Å), which is gradually dicreased
to end with 500 Å\ :sup:`2` (≈ 22 Å).

.. Note::

    Columns with zeros or ones should not be modified, as
    well as line 2. They are used for internal development purposes.


Simple optimization
-------------------

Before running a systematic docking simulation which could take several hours,
a simple optimization can be performed to check if an experimental
protein-protein complex is associated to an energy minimum of the
force-field used.
Single mode optimizations are also useful if the user want to make a movie
of an minimization process (see section **REF::video**).

A single optimization with ATTRACT requires:

- the ATTRACT Python script (``attract.py``)
- a coarse grain receptor (fixed partner) file (``receptor.red``)
- a coarse grain (mobile partner) file (``ligand.red``)
- docking parameters (``attract.inp``)


ATTRACT can be used with different options.

- The force\_field name has to be chosen among attract1, attract2 or scorpion.
- ``-r`` or ``--receptor`` (mandatory): defines the receptor file.
- ``-l`` or ``--ligand`` (mandatory): defines the ligand file.
- ``-s`` (optional): performs one single serie of minimisations with the
  ligand in its initial position.
- ``--ref``, (optional) provides a ligand PDB file as a reference (reduced).
  After the optimization, the RMSD is calculated between this reference
  structure and the simulated ligand.
- ``--t transnb`` (optional): loads only the translation number ``transnb``
  (and all its associated rotations). This option is very useful for
  dispatching a simulation over a cluster of computers.
- ``-h`` or ``--help`` (optional): reminds possible options.


A single ATTRACT simulation (optimization) may thus be obtained by::

    attract.py -r receptor.red -l ligand.red --ref=ligand.red -s > single.att

The first PDB file provided must be the receptor file (and the second the ligand).
The content of the output file ``single.att`` is the following:

.. code-block:: bat
   :linenos:


    **********************************************************************
    **                                                                  **
    **                ATTRACT  (Python edition)                         **
    **                based on the PTools library                       **
    **                                                                  **
    **********************************************************************

    PTools revision 437
    from branch bug539468
    unique id pierre_poulain-20100603130128-awuyfelj7avtls54
    
    Start time: 2010-06-03 18:50:57.506277
    Reading parameters file: attract.inp
    6 series of minimizations
    rstk =  0.0005
    Reading receptor (fixed): receptor.red with 246 particules
    Reading  ligand (mobile): ligand.red with 162 particules
    Reading reference file: ligand.red with 162 particules
    Single mode simulation
    @@@@@@@ Translation nb 1 @@@@@@@
    ----- Rotation nb 1 -----
    {{ minimization nb 1 of 6 ; cutoff= 99.50 (A) ; maxiter= 100
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  69 iterations
    {{ minimization nb 2 of 6 ; cutoff= 38.73 (A) ; maxiter= 100
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  9 iterations
    {{ minimization nb 3 of 6 ; cutoff= 31.62 (A) ; maxiter= 100
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  13 iterations
    {{ minimization nb 4 of 6 ; cutoff= 22.36 (A) ; maxiter= 50
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  11 iterations
    {{ minimization nb 5 of 6 ; cutoff= 22.36 (A) ; maxiter= 50
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  3 iterations
    {{ minimization nb 6 of 6 ; cutoff= 22.36 (A) ; maxiter= 50
    number of free variables for the minimizer: 6
    CONVERGENCE: REL_REDUCTION_OF_F <= FACTR*EPSMCH             |  1 iterations
          Trans    Rot          Ener    RmsdCA_ref
    ==        1      1   -58.4463779 1.23525236672
    ### MAT BEGIN
    MAT        0.9941915     -0.0969983      0.0466331      0.4410928 
    MAT        0.0984211      0.9947151     -0.0292441     -1.1030090 
    MAT       -0.0435501      0.0336639      0.9984839      0.5793707 
    MAT        0.0000000      0.0000000      0.0000000      1.0000000 
    ### MAT END

    Saved all minimization variables (translations/rotations) in minimization.trj
    End time: 2010-06-03 18:50:58.031199
    Elapsed time: 0:00:00.524922

- **lines 1--6:** header
- **lines 7--9:** PTools library revision, branch and unique id
- **line 11:** starting date and time of the simulation
- **lines 21--23:** minimization 1. Minimization index, cutoff 
  in Å and maximum number of iterations (line 21). 
  Number of variables (line 22). End of minimization (line~23), either 
  convergence is achieved (the number of performed iterations is specified), 
  either maximum number of steps is reached.
- **lines 24--26:** minimization 2.
- **lines 27--29:** minimization 3.
- **lines 30--32:** minimization 4.
- **lines 33--35:** minimization 5.
- **lines 36--38:** minimization 6.
- **lines 39--40:** final result after the 6 minimizations.
  With a single series of minimization, the default translation (``Trans``)
  is 1 and the default rotation (``Rot``) is 1. 
  Energy (``Ener``) is given in RT unit and the C\ :sub:`α`-RMSD 
  (``RmsdCA_ref``) in Å if the ``--ref`` option is specified.
- **lines 41--46:** rotation/translation matrix of the ligand compared to its initial position.
- **line 49:** end date and time of the simulation.
- **line 50:** elapsed time for the simulation

Here, the final energy is -58.4 RT unit and the RMSD is 1.2 Å, which is pretty
close from the initial position (in a *perfect* simulation, RMSD would be
of course, 0.0 Å).


Initial ligand positions for systematic docking
-----------------------------------------------

Rigid body movements in translational and rotational space can be described
with 3 variables or degrees of freedom (`x`, `y` and `z`) in translation 
and 3 variables (φ,  ψ and θ) in rotation. The rigid body 
transformation is illustrated in  Fig. **reference**.

.. .. figure:: ../_images/rigid_body_freedom.png
..    :align: center

..    Rigid body transformation in translational and rotational space.


Translations
^^^^^^^^^^^^

For the purpose of a systematic docking simulation, (translational) 
starting points are placed  all around the receptor.
The Python script ``translate.py`` employs a slightly modified Shrake and Rupley [#Shrake1973]_
method to define starting positions from the receptor surface.
The surface generation functions are implemented in the PTools library.
The script first reads the coarse grain (reduced) receptor and ligand files,
then generates a grid of points at a certain distance from the receptor and outputs
the grid with a given density.

Note: a density option (``-d``) controls the minimum distance between starting 
points (in Å).
The default value is 10.0 Å. 

In the present case::

    translate.py receptor.red ligand.red > translation.dat


Vizualization of the starting points may be obtained with any vizualisation 
software by renaming ``translation.dat`` in ``translation.pdb`` and then
by removing the first line of ``translation.pdb`` (that indicates the total 
number of starting points).
In this example, Fig.~\ref{1CGI_translation} shows the receptor surounded by
the 204 starting points.

.. [#Shrake1973] Shrake, A. & Rupley, J.A. Environment and exposure to solvent of protein atoms. Lysozyme and insulin. Journal of Molecular Biology 79, (1973).

.. \begin{figure}[htbp]
.. \center
.. \includegraphics*[width=0.4\textwidth]{img/1CGI_translation.png}
.. \caption{Coarse grain receptor in green spheres and starting points as orange spheres.}
.. \label{1CGI_translation}
.. \end{figure}


Rotations
^^^^^^^^^


Each position in translation (*i.e.* each ``ATOM`` line of the file ``translation.dat``)
is associated with a certain number of rotations corresponding to the three (φ,  ψ and θ)
rotational degrees of freedom.
The rotation distribution is detailed in the file ``rotation.dat``,
which has the following format:

.. code-block:: bat
   :linenos:
    
          7   6
        0.0   1
       30.0   5
       60.0   9
       90.0  13
      120.0   9
      150.0   5
      180.0   1

First item of line 1 indicates the number of φ angles (7) that are listed underneath 
(0.0, 30.0, 60.0, 90.0, 120.0, 150.0 and 180.0°).
In the second column, the item on line 1 is the number of θ angles (here 6).
Figures underneath are the number of ψ angles associated to each φ angle.

For instance, with φ = 30°, there are 5 ψ angles (equally distributed on a
circle, *i.e.* 72, 144, 216, 288 and 360°) and 6 θ angles.
In total, there are 1 + 5 + 9 + 13 + 9 + 5 + 1) × 6 = 258 rotations per
translation.


Ultimately, there are in this example a total of 204 starting points × 258 rotations 
which gives 52,632 starting geometries for the ligand.

