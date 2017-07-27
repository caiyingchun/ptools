import sys
import os
import subprocess
import time
import re

# Set CONTEXT True to print latest context line for each match found
CONTEXT = True
DRY_RUN = False
STRIP_TERMINALS = False

def find_names_in_file(filename, names={}, context=CONTEXT):
    """Use regex to find all class.method and module.class names in one file, return as keys in names dict."""
    #e = re.compile('\.[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*')
    #e = re.compile('\.[a-zA-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*\(')
    e = re.compile('\.[a-zA-Z]+[a-zA-Z0-9_]*\(')
    with open(filename) as fin:
        for linee in fin.readlines():
            line = linee.strip()
            match = e.search(line)
            try:
                # Note: matching group includes leading "." and trailing "("
                name = match.group()
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


def print_names(namesdict, key=lambda x: x.upper(), print_values=CONTEXT):
    """Print names dictionary in sorted order. May need to re-order some entries to avoid renaming problems."""
    for name in sorted(namesdict.keys(), key=key):
        if print_values:
            print name, "  :  ", namesdict[name]
        else:
            print name


def print_substitutions(subslist, print_values=CONTEXT):
    """Print substitutions list in order."""
    for entry in subslist:
        if print_values:
            old, new = entry
            print old, "  :  ", new
        else:
            print entry[0]


def read_substitutions(filename):
    """Read data from file to create substitutions list."""
    substitutions = []
    with open(filename) as fin:
        for line in fin.readlines():
            #print filename, line.strip()
            entry = line.strip().split()
            if len(entry) == 2:
                substitutions.append(entry)
            else:
                print entry
    return substitutions


def  parse_entry(entry, strip_terminals=False):
    """Return target and new value for substitution entry with or without terminal "." and "(" characters."""
    target = entry[0] if not strip_terminals else entry[0][1:-1]
    newvalue = entry[1] if not strip_terminals else entry[1][1:-1]
    return target, newvalue


def rename_all(substitutions, dry_run=DRY_RUN, strip_terminals=STRIP_TERMINALS):
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

    for entry in substitutions:
        if len(entry) != 2:
            continue
        old, new = parse_entry(entry, strip_terminals=strip_terminals)
        print "Renaming %s  -->  %s" % (old, new)
        for suffix in suffixes:
            name_arg = name_arg_template % (suffix)
            sed_command = sed_command_template % (old, new)
            print "sed command is: ", sed_command
            if dry_run:
                if strip_terminals:
                    target = old
                else:
                    # Escape the metacharacters
                    olde = "\\%s\\%s" % (old[:-1], old[-1])
                    print "Escaping ", old, olde
                args = ('find', '.', '-name', name_arg, '-exec', 'egrep', '-Hs', olde, '{}', ';')
            else:
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
        substitutions = read_substitutions(namesfile)
        rename_all(substitutions)

