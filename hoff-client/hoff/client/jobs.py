from contextlib import contextmanager
import os
from .client import SubClient
from .coding import JsonCodable


class JobCreateParams(JsonCodable):
    JSON_ATTRS = ["template_name", "arguments"]
    JSON_RENAME_C2S = {}
    pass


class Job(JsonCodable):
    JSON_ATTRS = [
        "project",
        "executable",
        "id",
        "queue",
        "template",
        "input_set_id",
        "num_total_cpus",
        "total_physical_memory",
        "filter",
        "remote_job_id",
        "arguments",
        "wallclock_limit",
        "service_id",
        # Note these two have to be fetched separately...
        "state",
        "retrieved",
    ]
    JSON_RENAME_C2S = {"id": "local_job_id", "template": "name"}
    pass


@contextmanager
def cd(path):
    old_wd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_wd)


class JobClient(SubClient):
    """A service client for dealing with Hoff jobs.
    """

    def create(self, job_create_params):
        """Create a job from the parameters - returns the created job ID."""
        if not isinstance(job_create_params, JobCreateParams):
            raise TypeError("must pass JobCreateParams object to JobClient.create")

        resp = self.session.post(self.url, json=job_create_params.json())

        if resp.status_code != 200:
            raise HoffError("Could not create job", reposnse=resp)

        job_id = resp.content
        return job_id

    def list(self, include_deleted=False):
        """List all the job IDs you can see"""
        resp = self.session.get(self.url)
        if resp.status_code != 200:
            raise HoffError("Could not list visible jobs", response=resp)
        return [js["local_job_id"] for js in resp.json() if js["state"] != "DELETED"]

    def get(self, job_id):
        """Get full job info for a job ID"""
        resp = self.session.get(self.urlbuild(str(job_id)))
        if resp.status_code != 200:
            raise HoffError(
                'Could get info for job ID "{}"'.format(job_id), response=resp
            )
        data = resp.json()
        data["state"] = self.get_state(job_id)
        data["retrieved"] = self.get_retrieved(job_id)
        return Job(**data)

    def add_input(self, job_id, **files):
        """Add input files to a job"""
        file_url = self.urlbuild(str(job_id), "files")

        @contextmanager
        def filemgr(files):
            open_files = {name: open(files[name], "rb") for name in files}
            try:
                yield open_files
            finally:
                for name in files:
                    open_files[name].close()

        with filemgr(files) as input_files:
            resp = self.session.post(file_url, files=input_files)

        if resp.status_code != 200:
            raise HoffError(
                'Could not upload files for job ID "{}"'.format(job_id), response=resp
            )

    def submit(self, job_id):
        """Submit a created job for execution"""
        resp = self.session.post(self.urlbuild(str(job_id), "submit"))
        if resp.status_code != 200:
            raise HoffError(
                'Could not submit job ID "{}"'.format(job_id), response=resp
            )

    def get_state(self, job_id):
        """Given a job ID get the state"""
        state_url = self.urlbuild(str(job_id), "state")
        resp = self.session.get(state_url)
        if resp.status_code != 200:
            raise HoffError(
                'Could not get state for job ID "{}"'.format(job_id), response=resp
            )
        return resp.text

    def get_retrieved(self, job_id):
        """Given a job ID get whether it's results have been fetched to
        the hoff-server.
        """
        get_retrieved_state_url = self.urlbuild(str(job_id), "retrieved")
        resp = self.session.get(get_retrieved_state_url)
        if resp.status_code != 200:
            raise HoffError(
                'Could not get retrieved flag for job ID "{}"'.format(job_id),
                response=resp,
            )
        return int(resp.content)

    def list_output(self, job_id):
        file_list_url = self.urlbuild(str(job_id), "files")
        resp = self.session.get(file_list_url)
        if resp.status_code != 200:
            raise HoffError(
                'Could not list output files for job ID "{}"'.format(job_id),
                response=resp,
            )
        return resp.json()

    def _get_file_impl(self, base_url, filename):
        # Assumes that you have cd'ed into the local output dir
        file_url = base_url + filename
        outdir = os.path.dirname(filename)
        if outdir != "" and not os.path.exists(outdir):
            os.makedirs(outdir)
        resp = self.session.get(file_url, stream=True)
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

    def fetch_output_file(self, job_id, output_dir, file_name):
        """Get a single output file"""
        with cd(output_dir):
            self._get_file_impl(self.urlbuild(job_id, "files/"))

    def fetch_output_files(self, job_id, output_dir, file_names):
        """Get a list of output files"""
        url = self.urlbuild(job_id, "files/")
        with cd(output_dir):
            for file_name in file_names:
                self._get_file_impl(url, file_name)

    def fetch_output(self, job_id, output_dir):
        """Get all of a job's output files"""
        self.fetch_output_files(job_id, output_dir, self.list_output(job_id))

    def delete(self, job_id):
        """Delete a job"""
        delete_url = self.urlbuild(str(job_id))
        resp = self.session.delete(delete_url)
        if resp.status_code != 200:
            raise HoffError(
                'Could not delete job ID "{}"'.format(job_id), response=resp
            )

    pass
