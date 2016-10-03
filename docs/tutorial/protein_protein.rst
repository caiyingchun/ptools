
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


ATTRACT parameters
------------------

The parameters required for running an ATTRACT calculation are found in the
file ``attract.inp``, which typical content is:


.. code-block:: r
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


.. [#] http://www.rcsb.org/pdb/cgi/explore.cgi?pdbId=1CGI
.. [#] http://pymol.sourceforge.net
.. [#] http://www.ks.uiuc.edu/Research/vmd
.. [#Basdevant2007] Basdevant, N., Borgis, D. & Ha-Duong, T. A coarse-grained protein-protein potential derived from an all-atom force field. *Journal of Physical Chemistry B* **111**, 9390-9399 (2007).
