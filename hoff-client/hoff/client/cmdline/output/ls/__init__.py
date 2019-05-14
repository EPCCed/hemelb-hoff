from __future__ import absolute_import


def add_verb(parent):
    parser = parent.add_parser("ls", help="list output of a job")
    parser.add_argument(
        "--invert", "-v", action="store_true", help="invert the meaning of the pattern"
    )
    parser.add_argument("pattern", help="pattern to match against file names to list")

    parser.set_defaults(module=".output.ls.operation", function="run")
    return parser
