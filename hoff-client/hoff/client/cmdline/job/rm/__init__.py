def add_verb(parent):
    parser = parent.add_parser('rm', help='delete one or more jobs')
    parser.add_argument('job_ids', help='List of Hoff job ids (one or more)', nargs='+')
    parser.set_defaults(module='.job.rm.operation', function='run')
    return parser
