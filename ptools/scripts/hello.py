
"""PTools hello command."""


from __future__ import print_function


def create_subparser(parent):
    parser = parent.add_parser('hello', help=__doc__)
    parser.set_defaults(func=run)


def run(args):
    print("HEYYYYYY: welcome to Ptools !!!")
    
    
