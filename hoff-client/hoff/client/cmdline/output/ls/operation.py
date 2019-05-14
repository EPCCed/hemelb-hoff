from __future__ import print_function, absolute_import
from hoff.client import Config, Session


def run(args):
    conf = Config(args.config)

    if args.outdir is None:
        args.outdir = os.getcwd()

    with Session(conf) as s:
        jclient = s.jobs
        output = jclient.list_output(args.job_id)

    for item in output:
        print(output)
