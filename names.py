import sys
import os
import subprocess
import time
import re

# Set CONTEXT True to print latest context line for each match found
CONTEXT = True

def find_names_in_file(filename, names={}, context=CONTEXT):
    """Find all class.method and module.class names in one file, return as keys in names dict."""
    #e = re.compile('\.[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*')
    #e = re.compile('\.[a-zA-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*\(')
    e = re.compile('\.[a-zA-Z]+[a-zA-Z0-9_]*\(')
    with open(filename) as fin:
        for linee in fin.readlines():
            line = linee.strip()
            match = e.search(line)
            try:
                # group includes leading "." and trailing "("
                name = match.group()[1:-1]
                if context:
                    names[name] = line
                else:
                    names[name] = None
            except AttributeError:
                # Failure to match returns an object without a group() method
                pass
            pass
    return names


def find_names(searchdirs='./', suffix=".py"):
    """Find all class.method and module.class names in all files in searchdirs, return as keys in names dict."""
    names = {}
    
    for searchdir in searchdirs:

        # From the os.walk example at https://stackoverflow.com/a/120701
        for dirname, dirnames, filenames in os.walk(searchdir):
        
            for filename in filenames:
                if filename.endswith(suffix):
                    fullname = os.path.join(dirname, filename)
                    find_names_in_file(fullname, names=names)
        
            # Advanced usage:
            # editing the 'dirnames' list will stop os.walk() from recursing into there.
            if '.git' in dirnames:
                # don't go into any .git directories.
                dirnames.remove('.git')

    return names


def print_names(names, key=lambda x: x.upper(), print_values=CONTEXT):
    """Print in sorted order. Must re-order as necessary to avoid renaming problems."""
    for name in sorted(names.keys(), key=key):
        if print_values:
            print name, "  :  ", names[name]
        else:
            print name


def print_translations(tlist, print_values=CONTEXT):
    for entry in tlist:
        if print_values:
            old, new = entry
            print old, "  :  ", new
        else:
            print entry[0]


def read_translations(filename):
    """Read data from file to create translations list."""
    translations = []
    with open(filename) as fin:
        for line in fin.readlines():
            #print filename, line.strip()
            entry = line.strip().split()
            if len(entry) == 2:
                translations.append(entry)
            else:
                print entry
    return translations


def rename_all(translations):
    """Use unix sed command to rename identifiers in all relevant files."""
    # find . -name \*.h -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.cpp -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.pyx -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.py -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.rst -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # make clean
    # make install
    # make test

    ## TEST: Use .T suffix and a file named "test.T" for testing
    #suffixes = [".T"]
    suffixes = [".h", ".cpp", ".py", ".pyx"]
    #suffixes = [".rst"]

    name_arg_template = "*%s"
    sed_command_template = "s/%s/%s/g"

    for entry in translations:
        if len(entry) != 2:
            continue
        old, new = entry
        print "Renaming %s  -->  %s" % (old, new)
        for suffix in suffixes:
            name_arg = name_arg_template % (suffix)
            sed_command = sed_command_template % (old, new)
            args = ('find', '.', '-name', name_arg, '-exec', 'sed', '-i', sed_command, '{}', ';')
            print args
            subprocess.Popen(args)
        time.sleep(1)
    return


if __name__ == "__main__":

    task = sys.argv[1]

    if task.startswith('find'):
        searchdirs = sys.argv[2:]
        names = find_names(searchdirs)
        print_names(names)

    elif task.startswith('rename'):
        namesfile = sys.argv[2]
        translations = read_translations(namesfile)
        rename_all(translations)

