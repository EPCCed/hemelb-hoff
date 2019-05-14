from __future__ import absolute_import

def add_verb(parent):
    parser = parent.add_parser('cp', help='copy output of a job to localhost')
    parser.add_argument('--outdir', '-o', default=None, help='Name of directory to fetch results to')
    parser.set_defaults(module='.output.cp.operation', function='run')
    return parser
