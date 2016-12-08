.. highlight:: shell

============
Installation
============


Latest stable release quick setup
---------------------------------

This is the very minimal set of instructions required to install PTools
in a Python virtual environment.

First, install all PTools dependencies. This requires administrator permissions. 
E.g., for a debian- or ubuntu-like system::

    $ sudo apt-get update
    $ sudo apt-get install g++ libboost-dev libf2c2-dev python-dev python-pip
    $ sudo pip install virtualenv

The rest can be installed as a normal user::

    $ virtualenv ptools-env
    $ source ptools-env/bin/activate
    (ptools-env) $ pip install cython pytest
    (ptools-env) $ git clone https://github.com/ptools/ptools.git    
    (ptools-env) $ cd ptools
    (ptools-env) $ python setup.py install


From sources
------------

The sources for ptools can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/benoistlaurent/ptools

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/benoistlaurent/ptools/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install

The documentation is provided in the 'docs' directory. Simply run 'make' in this directory 
to get a pdf documentation.

Source code may be parsed by an automatic documentation generator called 'Doxygen'.
This documentation may only help for the C++ part of the library. After installing Doxygen, simply type 'doxygen' in the directory which contains the 'Doxyfile'. Then look into the html/ directory and find the index.html file generated...


.. _Github repo: https://github.com/ptools/ptools
.. _tarball: https://github.com/ptools/ptools/tarball/master
