import sys
import os
import re

# Set CONTEXT True to print latest context line for each match found
CONTEXT = False

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
    for name in sorted(names.keys(), key=key):
        if print_values:
            print name, "  :  ", names[name]
        else:
            print name


def read_names_data(filename):
    """Read data from file to create names dict."""
    names = {}
    with open(filename) as fin:
        for line in fin.readlines():
            #print filename, line.strip()
            entries = line.strip().split()
            if len(entries) == 2:
                old, new = line.strip().split()
                names[old] = new
            else:
                print entries
    return names


def rename_all(names):
    """Use unix sed command to rename identifiers in all relevant files."""
    # find . -name \*.h -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.cpp -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.pyx -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.py -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # find . -name \*.rst -exec sed --in-place 's/ABrotate/rotate/g' {} \;
    # make clean
    # make install
    # make test
    for old in sorted(names.keys(), key=lambda x: x.upper()):
        print old, "  -->  ", names[old]
    return


if __name__ == "__main__":

    task = sys.argv[1]

    if task.startswith('find'):
        searchdirs = sys.argv[2:]
        names = find_names(searchdirs)
        print_names(names)

    elif task.startswith('rename'):
        namesfile = sys.argv[2]
        names = read_names_data(namesfile)
        rename_all(names)

