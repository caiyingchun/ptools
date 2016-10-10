===================
The PTools library
===================

.. show travis-ci build status
.. image:: https://img.shields.io/travis/ptools/ptools.svg?branch=develop
        :target: https://travis-ci.org/ptools/ptools


About
-----

The PTools library is a toolbox for macromolecular modeling and docking.

A more detailed introduction can be found here: http://www.biomedcentral.com/1472-6807/9/27.

PTools: an opensource molecular docking library

Adrien Saladin, Sébastien Fiorucci, Pierre Poulain, Chantal Prévost and Martin Zacharias
BMC Structural Biology. 2009;9:27. 

doi: 10.1186/1472-6807-9-27


Documentation
-------------

The documentation is provided in the 'Tutorial/doc' directory. Simply run 'make' in this directory 
to get a pdf documentation.

Source code may be parsed by an automatic documentation generator called 'Doxygen'.
This documentation may only help for the C++ part of the library.
after installing Doxygen, simply type 'doxygen' in the directory which contains the 'Doxyfile'.
Then look into the html/ directory and find the index.html file generated...


Very quick setup guide
-----------------------

This is the very minimal set of instructions required to install Ptools
in a Python virtual environment.
It assumes all Ptools dependencies have been duly installed. This requires
administrator permissions. E.g., for a debian-like system

    $ sudo apt-get update
    $ sudo apt-get install g++ libboost-dev libf2c2-dev python-dev python-pip
    $ sudo pip install virtualenv

The rest can be performed as a normal user

    $ virtualenv ptools-env
    $ source ptools-env/bin/activate
    (ptools-env) $ pip install cython pytest
    (ptools-env) $ git clone https://github.com/ptools/ptools.git    
    (ptools-env) $ cd ptools
    (ptools-env) $ python setup.py install

A more detailed version of the procedure is in the official tutorial. 


About Git branches:
--------------------

This git repository contains few branches. "master" is the latest "stable" version. 
"develop" contains the current development version. Other branches are features branches, 
which are eventually merged into develop.
