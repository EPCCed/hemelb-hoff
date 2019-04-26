from __future__ import absolute_import
from . import ls
from . import rm

def add_subcommand(parent):
    parser = parent.add_parser('job', help='job related commands')
    verbs = parser.add_subparsers(help='job action help')
    ls.add_verb(verbs)
    rm.add_verb(verbs)
    
