from __future__ import absolute_import
from . import ls
from . import cp


def add_subcommand(parent):
    parser = parent.add_parser("output", help="output related commands")
    parser.add_argument("job_id", help="Hoff job ID")
    verbs = parser.add_subparsers(help="output action help")
    ls.add_verb(verbs)
    cp.add_verb(verbs)
