# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tarfile
import textwrap
import urllib2
import StringIO

from setuptools import setup, find_packages
from distutils import log
from distutils.extension import Extension
from distutils.errors import DistutilsOptionError



try:
    from Cython.Distutils import build_ext as _build_ext
except ImportError:
    print("Cannot find cython. Please install it using `pip install cython`.",
          file=sys.stderr)
    exit(1)


# Display info messages sent to logger.
log.set_verbosity(log.INFO)


# URL for downloading a tarball containing ptools dependencies.
PTOOLS_DEP_URL = 'https://codeload.github.com/ptools/ptools_dep/legacy.tar.gz'\
                 '/master'


# For compatibility with Python 2.6.
if sys.version_info >= (2, 7):
    check_output = subprocess.check_output
else:
    def _check_output(args):
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
    check_output = _check_output


# OS X specific linking options.
if sys.platform == 'darwin':
    from distutils import sysconfig
    vars = sysconfig.get_config_vars()
    vars['LDSHARED'] = vars['LDSHARED'].replace('-bundle', '-dynamiclib')


class build_ext(_build_ext):

    user_options = _build_ext.user_options
    boolean_options = _build_ext.boolean_options

    user_options.extend([
        ('use-legacy-boost', None, "download an old version "
                                   "of boost headers"),
        ('with-boost-include-dir=', None, 'location of boost headers'),
    ])

    boolean_options.extend(['use_legacy_boost'])

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.use_legacy_boost = False
        self.with_boost_include_dir = ''

    def finalize_options(self):
        _build_ext.finalize_options(self)

        # Cannot use '--use-legacy-boost' with '--with-boost-include-dir'
        if self.use_legacy_boost and self.with_boost_include_dir:
            msg = "must supply either --use-legacy-boost either "\
                  "--with-boost-include-dir -- not both"
            raise DistutilsOptionError(msg)

        boost_include_dir = ''

        if self.with_boost_include_dir:
            boost_include_dir = self.with_boost_include_dir
        if self.use_legacy_boost:
            raise NotImplementedError('not implemented yet')

        # Use the automatic find functions to find dependencies if
        # they have not been provided by the user.
        if not boost_include_dir:
            boost_include_dir = find_boost()

        if boost_include_dir:
            self.include_dirs.append(boost_include_dir)


def git_version():
    """Return the git revision as a string."""
    cmd = ['git', 'show', '-s', '--format=%h %ci', 'HEAD']
    try:
        git_revision = check_output(cmd).strip()
    except OSError:
        git_revision = 'Unknown version. Please use git to download PTools '\
                       'and get reliable versioning informations'
    return git_revision


def write_version_h(filename):
    """Write a header file with the current git revision hash."""
    git_revision = git_version()
    if git_revision.startswith('Unknown'):
        s = "it seems that you don't have a git directory. "\
            "While the library will compile correcly, informations about "\
            "the current ptools version will be missing. Please use git to "\
            "download PTools and get reliable versioning informations."
        warn(s)

    content = textwrap.dedent("""
        /*
         * This file was generated automatically.
         * You should not modify it manually, as it may be re-generated.
         */

        #ifndef GITREV_H
        #define GITREV_H
        #define GIT_REVID   "%(git_revision)s"
        #endif /* GITREV_H */
        """)
    with open(filename, 'w') as f:
        f.write(content % {'git_revision': git_revision})


def get_environ(s):
    """Return the value of environment variable `s` if present, else
    an empty string."""
    return os.environ[s] if s in os.environ else ''


def find_file(filename, paths):
    """Try to locate a file in a given set of directories.

    Args:
        filename(str): file to look for.
        paths(list[str]): directories to scan.

    Return:
        str: the absolute path to the file in which directory is the first
            directory where the file has been found.
            An empty string if no file has been found.
    """
    for dirname in paths:
        abspath = os.path.abspath(os.path.join(dirname, filename))
        if os.path.exists(abspath):
            return abspath
    return ''


def find_directory(filename, paths):
    """Try to locate a file in a given set of directories.

    Args:
        filename(str): file to look for.
        paths(list[str]): directories to scan.

    Returns:
        str: the absolute path to the directory in which the file
            has been found. An empty string if no file has been found.
    """
    for dirname in paths:
        abspath = os.path.join(dirname, filename)
        if os.path.exists(abspath):
            return os.path.abspath(dirname)
    return ''


def find_executable(filename):
    """Try to locate a program in the PATH environment variable.

    Args:
        filename(str): program to look for.

    Returns:
        str: absolute path to `filename` if in the path, else
            an empty string.
    """
    return find_file(filename, os.environ['PATH'].split(':'))

def find_boost():
    """Try to locate the boost include directory (look for
    the shared_array.hpp header file).

    Returns:
        str: boost include directory
    """
    boostdir = find_directory('boost/shared_array.hpp',
                              [get_environ('BOOST_INCLUDE_DIR'),
                               '/usr/include', '/usr/local/include',
                               '/opt/local/include'])
    if not boostdir:
        warn("Boost not found. Specify headers location by using the "
             "BOOST_INCLUDE_DIR environment variable. If it is not "
             "installed, you can either install a recent version "
             "or use the --use-legacy-boost option.")
        raise OSError('Boost headers not found')
    else:
        log.info("Boost headers found at {0}".format(boostdir))
    return boostdir


def find_fortranlib():
    """Try to locate the gfortran include directory and libgfortran library.

    Returns:
        str: fortran include directory and the absolute
            path to libgfortran.
    """

    # Search libgfortran.
    fortran_library_name = 'libgfortran.3.dylib' if sys.platform == 'darwin' else 'libgfortran.so.3'
    fortlib = find_file(fortran_library_name,
                  ['/usr/lib64', '/usr/local/lib64',
                   '/usr/lib', '/usr/local/lib',
                   '/opt/local/lib', '/opt/local/lib/libgcc',
                   '/usr/lib/x86_64-linux-gnu'])
    if not fortlib:
        warn("{:s} not found. Specify its location by using the "
             "LD_LIBRARY_PATH environment variable.".format(fortran_library_name))
        raise OSError('{:s} not found'.format(fortran_library_name))
    else:
        log.info("{:s} found at {:s}".format(fortran_library_name, fortlib))
    return fortlib


def compile_fortran(sourcefile):
    objfile = sourcefile.replace('.f','.o')
    args = ["gfortran", "-fPIC", "-c", "-o", objfile, sourcefile]
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]


def warn(message, prefix='WARNING: '):
    """Print a warning message preceded by `prefix` using docutils.log.warn."""
    log.warn(prefix + message)


def setup_package():
    # Update version header.
    write_version_h('headers/gitrev.h')

    # Install data files in <prefix>/share/ptools.
    data_dir = os.path.join(sys.prefix, "share/ptools/data")
    #data_dir = "/workdir/simlab_team/robert/.local/share/ptools/data"

    # Install all files in the data directory.
    data_files = [os.path.join('data', path) for path in os.listdir('data')]

    sources = ['src/BasePair.cpp',
               'src/DNA.cpp',
               'src/Movement.cpp',
               'src/Parameter.cpp',
               'src/cython_wrappers.cpp',
               'src/atom.cpp',
               'src/attractrigidbody.cpp',
               'src/coordsarray.cpp',
               'src/mcopff.cpp',
               'src/rigidbody.cpp',
               'src/surface.cpp',
               'src/atomselection.cpp',
               'src/basetypes.cpp',
               'src/forcefield.cpp',
               'src/pairlist.cpp',
               'src/rmsd.cpp',
               'src/version.cpp',
               'src/attractforcefield.cpp',
               'src/coord3d.cpp',
               'src/geometry.cpp',
               'src/pdbio.cpp',
               'src/superpose.cpp',
               'src/scorpionforcefield.cpp',
               'src/cgopt/chrg_scorpion_wrap.cpp',
               'src/minimizers/lbfgs_interface.cpp',
               'src/minimizers/lbfgs_wrapper/lbfgsb_wrapper.cpp',
               ]

    sources.append("bindings/_ptools.pyx")

    compile_fortran('src/minimizers/lbfgs_wrapper/lbfgsb.f')
    compile_fortran('src/cgopt/chrg_scorpion.f')

    ptools = Extension('_ptools',
                       sources=sources,
                       language='c++',
                       include_dirs=['headers'],
                       extra_objects = ['src/minimizers/lbfgs_wrapper/lbfgsb.o',
                           find_fortranlib()])

    cgopt = Extension('_cgopt',
                      sources=['bindings/_cgopt.pyx'],
                      language='c++',
                      include_dirs=['src/cgopt'],
                      extra_objects = ['src/cgopt/chrg_scorpion.o',
                           find_fortranlib()])

    packages = find_packages(exclude=['Heligeom',
                                      'Tests',
                                      'Tests.functionnal'])

    setup(ext_modules=[ptools, cgopt],
          cmdclass={'build_ext': build_ext},
          name='ptools',
          packages=packages,
          version='1.2',
          entry_points={
              'console_scripts': ['ptools = ptools.scripts.ptools_cli:main']
          },
          include_package_data=True,
          data_files=[
              (data_dir, data_files)
          ]
    )


def setup_cpp_tests():
    template_variables = {
        'BOOST_INCLUDE_DIR': find_boost()
    }

    # Read Makefile template and modify it according to the template variable
    # dictionnary.
    with open('Tests/cpp/Makefile.in', 'rt') as f:
        template = f.read()
    for variable, value in template_variables.items():
        variable = '@' + variable + '@'
        template = template.replace(variable, value)

    # Write actual Makefile used to compile and run C++ tests.
    with open('Tests/cpp/Makefile', 'wt') as f:
        f.write(template)


if __name__ == '__main__':
    setup_package()
    setup_cpp_tests()
