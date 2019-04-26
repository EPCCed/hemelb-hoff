def add_verb(parent):
    parser = parent.add_parser('ls', help='list jobs')
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'plain'],
        default='table',
        help='How to print data')
    default_cols = ['id', 'template', 'arguments', 'state']
    parser.add_argument('cols', nargs='*', default=default_cols, help='List of columns to print')
    parser.set_defaults(module='.job.ls.operation', function='run')
    return parser
