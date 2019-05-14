from hoff.client import Config, Session

def run(args):
    conf = Config(args.config)

    if args.outdir is None:
        args.outdir = os.getcwd()

    with Session(conf) as s:
        jclient = s.jobs
        jclient.fetch_output(args.job_id, args.outdir)
