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


# Directory where legacy f2c library will be downloaded and compiled if
# required.
LEGACY_F2C_DIR = 'f2c_legacy'


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
        ('use-legacy-f2c', None, "download and compile an old version "
                                 "of libf2c"),
        ('with-boost-include-dir=', None, 'location of boost headers'),
        ('with-f2c-include-dir=', None, 'location of libf2c headers'),
        ('with-f2c-library=', None, 'location of libf2c.a'),
    ])

    boolean_options.extend(['use-legacy-f2c', 'use_legacy_boost'])

    def initialize_options(self):
        _build_ext.initialize_options(self)
        self.use_legacy_f2c = False
        self.use_legacy_boost = False
        self.with_boost_include_dir = ''
        self.with_f2c_include_dir = ''
        self.with_f2c_library = ''

    def finalize_options(self):
        _build_ext.finalize_options(self)

        # Cannot use '--use-legacy-f2c' with '--with-f2c-include-dir'
        if self.use_legacy_f2c and self.with_f2c_include_dir:
            msg = "must supply either --use-legacy-f2c either "\
                  "--with-f2c-include-dir -- not both"
            raise DistutilsOptionError(msg)

        # Cannot use '--use-legacy-f2c' with '--with-f2c-library'
        if self.use_legacy_f2c and self.with_f2c_library:
            msg = "must supply either --use-legacy-f2c either "\
                  "--with-f2c-library -- not both"
            raise DistutilsOptionError(msg)

        # Cannot use '--use-legacy-boost' with '--with-boost-include-dir'
        if self.use_legacy_boost and self.with_boost_include_dir:
            msg = "must supply either --use-legacy-boost either "\
                  "--with-boost-include-dir -- not both"
            raise DistutilsOptionError(msg)

        # '--with-f2c-include-dir' and 'with-f2c-library' need to be both
        # empty or filled.
        if any((self.with_f2c_library, self.with_f2c_include_dir)) and not\
           all((self.with_f2c_library, self.with_f2c_include_dir)):
            msg = '--with-f2c-include-dir and --with-f2c-library need to be '\
                  'both empty or both informed'
            raise DistutilsOptionError(msg)

        boost_include_dir = ''
        f2c_include_dir = ''
        f2c_library = ''

        if self.with_boost_include_dir:
            boost_include_dir = self.with_boost_include_dir
        if self.with_f2c_include_dir:
            f2c_include_dir = self.with_f2c_include_dir
            f2c_library = self.with_f2c_library
        if self.use_legacy_f2c:
            f2c_include_dir, f2c_library = install_legacy_f2c()
        if self.use_legacy_boost:
            raise NotImplementedError('not implemented yet')

        # Use the automatic find functions to find dependencies if
        # they have not been provided by the user.
        if not boost_include_dir:
            boost_include_dir = find_boost()
        if not f2c_include_dir:
            f2c_include_dir, f2c_library = find_f2c()

        if boost_include_dir:
            self.include_dirs.append(boost_include_dir)
        if f2c_include_dir:
            self.include_dirs.append(f2c_include_dir)
        if f2c_library:
            for ext in self.extensions:
                ext.extra_objects.append(f2c_library)


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


def install_legacy_f2c():
    """Download and build legacy libf2c from ptools_dep repository.

    Returns:
        tuple(str, str): libf2c include directory and the absolute
            path to libf2c.a.
    """
    def f2c_files(members):
        for tarinfo in members:
            if 'libf2c2-20090411' in tarinfo.name:
                yield tarinfo

    def download_legacy_f2c():
        url = PTOOLS_DEP_URL
        tarball_f2c_dir = 'ptools-ptools_dep-66b145b/libf2c2-20090411'
        log.info("Downloading f2c")
        response = urllib2.urlopen(url)
        compressed = StringIO.StringIO(response.read())
        tar = tarfile.open(fileobj=compressed, mode='r:gz')
        tar.extractall(members=f2c_files(tar))
        tar.close()
        shutil.move(tarball_f2c_dir, LEGACY_F2C_DIR)
        shutil.rmtree(tarball_f2c_dir.split('/')[0])
        log.info("Downloading f2c done")

    if not os.path.exists(LEGACY_F2C_DIR):
        download_legacy_f2c()

    log.info("Compiling f2c")
    cflags = 'CFLAGS=-ansi -g -O2 -fomit-frame-pointer -D_GNU_SOURCE '\
             '-fPIC -DNON_UNIX_STDIO -Df2c'

    # First compilation.
    args = ['make', '-C', LEGACY_F2C_DIR, '-f', 'makefile.u', cflags]
    subprocess.call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Library compilation (write log).
    args = ['make', '-C', LEGACY_F2C_DIR, '-f', 'makefile.u', cflags,
            'libf2c.a']
    logfilename = os.path.join(LEGACY_F2C_DIR, 'compile.log')
    with open(logfilename, 'wt') as logfile:
        subprocess.call(args, stdout=logfile, stderr=subprocess.STDOUT)

    tmpf2clib = os.path.join(LEGACY_F2C_DIR, 'libf2c.a')
    if not os.path.exists(tmpf2clib):
        log.fatal("error occured during f2c compilation. "
                  "Please check {0}.".format(log))
    log.info("Compiling f2c done")

    # Move header and library to pseudo install directory.
    f2cdir = os.path.join(os.path.join(LEGACY_F2C_DIR, 'install', 'include'))
    if not os.path.exists(f2cdir):
        os.makedirs(f2cdir)
    shutil.copyfile(os.path.join(LEGACY_F2C_DIR, 'f2c.h'),
                    os.path.join(f2cdir, 'f2c.h'))

    f2clibdir = os.path.join(os.path.join(LEGACY_F2C_DIR, 'install', 'lib'))
    f2clib = os.path.join(f2clibdir, 'libf2c.a')
    if not os.path.exists(f2clibdir):
        os.makedirs(f2clibdir)
    shutil.copyfile(tmpf2clib, f2clib)

    return f2cdir, f2clib


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


def find_f2c():
    """Try to locate the libf2c include directory and libf2c.a library.

    Returns:
        tuple(str, str): libf2c include directory and the absolute
            path to libf2c.a.
    """
    # Search f2c.h.
    f2cdir = find_directory('f2c.h',
                            [get_environ('F2C_INCLUDE_DIR'),
                             '/usr/include', '/usr/local/include',
                             '/opt/local/include'])
    if not f2cdir:
        warn("f2c.h not found. Specify headers location by using the "
             "F2C_INCLUDE_DIR environment variable. If it is not "
             "installed, you can either install a recent version "
             "or use the --use-legacy-f2c option.")
        raise OSError('f2c.h not found')
    else:
        log.info("f2c.h found at {0}".format(f2cdir))

    # Search libf2c.a.
    f2clib = get_environ('F2C_LIBRARY') or\
        find_file('libf2c.a',
                  ['/usr/lib', '/usr/local/lib', '/opt/local/lib',
                   '/usr/lib64', '/usr/local/lib64',
                   '/usr/lib/x86_64-linux-gnu'])
    if not f2clib:
        warn("libf2c.a not found. Specify its location by using the "
             "F2C_LIBRARY environment variable. If it is not "
             "installed, you can either install a recent version "
             "or use the --use-legacy-f2c option.")
        raise OSError('libf2c.a not found')
    else:
        log.info("libf2c.a found at {0}".format(f2clib))
    return f2cdir, f2clib


def warn(message, prefix='WARNING: '):
    """Print a warning message preceded by `prefix` using docutils.log.warn."""
    log.warn(prefix + message)


def setup_package():
    # Update version header.
    write_version_h('headers/gitrev.h')

    # Install data files in <prefix>/share/ptools.
    data_dir = os.path.join(sys.prefix, "share/ptools/data")

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
               'src/minimizers/lbfgs_interface.cpp',
               'src/minimizers/lbfgs_wrapper/lbfgsb.c',
               'src/minimizers/lbfgs_wrapper/lbfgsb_wrapper.cpp',
               ]

    sources.append("bindings/_ptools.pyx")

    ptools = Extension('_ptools',
                       sources=sources,
                       language='c++',
                       include_dirs=['headers'])

    cgopt = Extension('_cgopt',
                      sources=['bindings/_cgopt.pyx',
                               'src/cgopt/chrg_scorpion.c'],
                      language='c',
                      include_dirs=['src/cgopt'])

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
