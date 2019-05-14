from hoff.client import Config, Session

def run(args):
    conf = Config(args.config)
    with Session(conf) as s:
        jclient = s.jobs
        for job_id in args.job_ids:
            # delete the job
            jclient.delete(job_id)
