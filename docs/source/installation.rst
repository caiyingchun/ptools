.. highlight:: shell

============
Installation
============


This is the very minimal set of instructions required to install PTools
in a Python virtual environment.


Install dependencies
--------------------

First, install all system dependencies. 
This requires administrator permissions. 

Here are examples of installing system-level dependencies for one or two systems:


Debian-like system
~~~~~~~~~~~~~~~~~~

1. Install git and download PTools last release::

    $ sudo apt-get update
    $ sudo apt-get install -y git
    $ git clone https://github.com/ptools/ptools.git
    $ cd ptools

2.  Install system requirements::

    $ cat requirements_system.txt | xargs sudo apt-get install -y


MacOS system (with MacPorts installed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Download PTools last release::

    $ git clone https://github.com/ptools/ptools.git
    $ cd ptools

2. Install system requirements::

    $ cat requirements_macports.txt | xargs sudo port install -N

3. Select the gcc compiler::

    $ sudo port select gcc mp-gcc6

You then need to open a new shell for this compiler to be the default.

*Note: after installation is complete* return to the macos default compiler::

    $ sudo port select gcc none


Install PTools
--------------

The rest should be installed as a normal (non-root) user.

1. Create and activate the virtual environment (can be anywhere)::

    $ virtualenv ../venv-ptools
    $ source venv-ptools/bin/activate

An alias to the second command is recommended, as the virtual environment must be activated when installing or using PTools.

2. Install ptools dependencies::

    (venv-ptools) $ pip install -r requirements_python.txt

3. Build and install ptools::

    (venv-ptools) $ make install

4. Test to see that everything went fine::
   
    (venv-ptools) $ make test
