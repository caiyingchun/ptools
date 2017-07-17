.. highlight:: shell

============
Installation
============


Latest stable release quick setup
---------------------------------

This is the very minimal set of instructions required to install PTools
in a Python virtual environment.

First, install all system dependencies. 
This requires administrator permissions. 
E.g., for a debian- or ubuntu-like system::

1. Install git and download PTools last release::

    $ sudo apt-get update
    $ sudo apt-get install -y git
    $ git clone https://github.com/ptools/ptools.git
    $ cd ptools

2. Install system requirements::

    $ cat requirements_system.txt | xargs sudo apt-get install -y


The rest can be installed as a normal user::

1. Create and activate the virtual environment::

    $ virtualenv venv-ptools
    $ source venv-ptools/bin/activate

2. Install ptools dependencies::

    (venv-ptools) $ pip install -r requirements_python.txt

3. Build and install ptools::

    (venv-ptools) $ make install

4. Test everything went fine::
   
    (venv-ptools) $ make test
