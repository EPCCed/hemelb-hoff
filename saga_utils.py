"""
   Copyright 2018-2019 EPCC, University Of Edinburgh

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


from __future__ import print_function
import saga
import os
import re

import boto3
from botocore.exceptions import ClientError

from config import CIRRUS_WOS_ACCESS_KEY
from config import CIRRUS_WOS_SECRET_KEY
from config import CIRRUS_WOS_HOFF_BUCKET
from config import CIRRUS_S3_ENDPOINT
from config import CIRRUS_S3_DEFAULT_REGION

def generate_presigned_url(bucket_name, path, expiration):

    s3_client = boto3.client(
        's3',
        aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
        aws_secret_access_key=CIRRUS_WOS_SECRET_KEY,
        region_name=CIRRUS_S3_DEFAULT_REGION
    )
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': path},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return None

        # The response contains the presigned URL
    return response





# name for the job's stdout file
JOB_STDOUT = "job.stdout"

# name for the job's stderr file
JOB_STDERR = "job.stderr"


def get_presigned_url(local_job_id, path):
    bucket_name = CIRRUS_WOS_HOFF_BUCKET + "-" + local_job_id
    s3 = boto3.client('s3', endpoint_url=CIRRUS_S3_ENDPOINT, aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
          aws_secret_access_key=CIRRUS_WOS_SECRET_KEY, verify=False)

    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': path,
        }
    )

def get_s3_bucket(local_job_id):
    bucket_name = CIRRUS_WOS_HOFF_BUCKET + "-" + local_job_id
    s3 = boto3.resource('s3', endpoint_url=CIRRUS_S3_ENDPOINT, aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
          aws_secret_access_key=CIRRUS_WOS_SECRET_KEY, verify=False)
    return s3.Bucket(bucket_name)


def copy_local_files_to_s3(local_job_dir):
    bucket = get_s3_bucket(os.path.basename(local_job_dir))
    response = bucket.create()
    for root, dir, files in os.walk(local_job_dir):
        for f in files:
            filename = os.path.join(root, f)
            keyname = os.path.relpath(filename, local_job_dir)
            response = bucket.upload_file(filename, keyname)


def list_s3_file_for_job(job_id):
    bucket = get_s3_bucket(os.path.basename(job_id))
    keys = []
    # note that s3 paginates after 1000 objects
    # we assumes that Hoff / Hemelb jobs only produce a small number of files, so we can get away with this
    # otherwise we will have to paginate
    for file in bucket.objects.all():
        keys.append(file.key)
    return keys


def s3_delete_files_for_job(job_id):
    bucket_name = CIRRUS_WOS_HOFF_BUCKET + "-" + job_id
    s3 = boto3.resource('s3', endpoint_url=CIRRUS_S3_ENDPOINT, aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
                        aws_secret_access_key=CIRRUS_WOS_SECRET_KEY, verify=False)
    bucket = s3.Bucket(CIRRUS_WOS_HOFF_BUCKET)
    filer = job_id + '/'
    # warning - the next line may only work if there are less than 1000 objects present,
    # otherwise a paginating solution is needed
    # for Hoff / Hemelb jobs we should get away with this ok
    bucket.objects.filter(Prefix=filter).delete()



def get_remote_job_state(remote_job_id, service):

    try:

        session = create_session_for_service(service)

        js = saga.job.Service(service['scheduler_url'], session)
        job = js.get_job(remote_job_id)
        state = job.state
        js.close()
        return state
    except saga.SagaException as ex:
        # Catch all saga exceptions
        print('An exception occured: {0} {1}'.format(ex.type, ex))
        # Trace back the exception. That can be helpful for debugging.
        print('Backtrace: {}'.format(ex.traceback))
        return None




def stage_input_files(job_id, local_input_file_dir, service):
    try:

        # create an SSH context and populate it with our SSH details.

        session = create_session_for_service(service)

        # specify a new working directory for the job
        # we use a UID here, but any unique identifer would work

        REMOTE_WORKING_DIR = service['working_directory']

        # create the job's working directory and copy over the contents of our input directory

        dir = saga.filesystem.Directory(service['file_url'] + REMOTE_WORKING_DIR, session=session)
        dir.make_dir(str(job_id))


        for f in os.listdir(local_input_file_dir):
            transfertarget = service['file_url'] + REMOTE_WORKING_DIR + "/" + str(job_id) + "/" + f
            transfersource = os.path.join(local_input_file_dir, f)
            out = saga.filesystem.File(transfersource, session=session)
            out.copy(transfertarget)

        dir.close()
        return 0

    except saga.SagaException as ex:
        # Catch all saga exceptions
        print('An exception occured: {0} {1}'.format(ex.type, ex))
        # Trace back the exception. That can be helpful for debugging.
        print('Backtrace: {}'.format(ex.traceback))
        return -1



def submit_saga_job(job_description, service):
    try:

        # create an SSH context and populate it with our SSH details.

        session = create_session_for_service(service)
        # specify a new working directory for the job
        # we use a UID here, but any unique identifer would work

        REMOTE_WORKING_DIR = os.path.join(service['working_directory'], str(job_description['local_job_id']))


        # Create a job service object pointing at our host
        js = saga.job.Service(service['scheduler_url'], session)

        # define our job by building a job description and populating it
        jd = saga.job.Description()

        # set the executable to be run
        jd.executable = job_description['executable']

        # set all the information we have been passed

        # set the budget to be charged against
        project = job_description.get('project')
        if project is not None:
            jd.project = project

        num_total_cpus = job_description.get('num_total_cpus')
        if num_total_cpus is not None:
            jd.total_cpu_count = num_total_cpus

        name = job_description.get('name')
        if name is not None:
            jd.name = name

        wallclock_limit = job_description.get('wallclock_limit')
        if wallclock_limit is not None:
            jd.wall_time_limit = wallclock_limit

        env = job_description.get('environment')
        if env is not None:
            jd.environment = env

        arguments = job_description.get('arguments')
        if arguments is not None:
            jd.arguments = arguments

        # here we abuse the SAGA spec to pass through any scheduler-specific directives.
        # eg exclusive reservation of a node, or anything that SAGA does not directly support
        #print(job_description)
        extended = job_description.get('extended')
        if extended is not None:
            print("setting {}".format(extended))
            jd.spmd_variation = extended

        # specify where the job's stdout and stderr will go
        jd.output = JOB_STDOUT
        jd.error = JOB_STDERR

        # specify the working directory for the job
        jd.working_directory = REMOTE_WORKING_DIR


        # Some applications may require exclusive use of nodes
        # SAGA does not support this;
        # as a workaround we can pass the following in the spmd_variation property,
        # which is otherwise unused by the underlying SAGA adapter code
        # jd.spmd_variation = "#PBS -l place=excl"

        # Create a new job from the job description. The initial state of
        # the job is 'New'.

        myjob = js.create_job(jd)
        myjob.run()
        js.close()
        return myjob.id

    except saga.SagaException as ex:
        # Catch all saga exceptions
        print('An exception occured: {0} {1}'.format(ex.type, ex))
        # Trace back the exception. That can be helpful for debugging.
        print('Backtrace: {}'.format(ex.traceback))
        return -1


def cancel_job(job_id, service):

    try:
        session = create_session_for_service(service)

        js = saga.job.Service(service['scheduler_url'], session)
        job = js.get_job(job_id)
        job.cancel()
        js.close()
    except Exception as e:
        raise e


def copy_remote_directory_to_local(remote_dir, local_job_dir, base_dir, filter, logger):

    if not os.path.exists(local_job_dir):
        os.makedirs(local_job_dir)

    for f in remote_dir.list():
        if remote_dir.is_file(f):
            outfiletarget = 'file://localhost/' + local_job_dir
            if filter is not None:
                try:
                    # get the url of our current directory
                    dir_url = str(remote_dir.get_url())

                    # get the relative directory path by referencing relative to base directory
                    relative_path = dir_url.replace(base_dir,"")

                    # get the relative file path
                    relative_file_path = os.path.join(relative_path, str(f))
                    if re.match(filter, relative_file_path) is not None:
                        logger.info("Copying output file " + f)
                        remote_dir.copy(f, outfiletarget)

                except Exception as e:
                    # filter failed, fallback to copy everything
                    remote_dir.copy(f, outfiletarget)
            else:
                outfiletarget = 'file://localhost/' + local_job_dir
                remote_dir.copy(f, outfiletarget)
        else:
            path = str(f)
            local_copy_dir = os.path.join(local_job_dir, path)
            copy_remote_directory_to_local(remote_dir.open_dir(f), local_copy_dir, base_dir, filter, logger)



def stage_output_files(remote_working_dir, local_job_dir, service, filter, logger):

    try:

        if not os.path.exists(local_job_dir):
            os.makedirs(local_job_dir)

        session = create_session_for_service(service)

        # create the job's local output directory and copy over the contents of our job's output directory

        remote_dir = saga.filesystem.Directory(service['file_url'] + remote_working_dir, session=session)
        base_url = str(remote_dir.get_url()) + "/"

        # always copy the stdout / stderr files

        for f in [JOB_STDERR, JOB_STDOUT]:
            try:
                outfiletarget = 'file://localhost/' + local_job_dir
                logger.info("Copying output file " + f)
                remote_dir.copy(f, outfiletarget)
                logger.info("Copied output file " + f)
            except Exception as e:
                message = "error copying output file: " + e.message
                logger.error(message)

        for f in remote_dir.list():
            if remote_dir.is_file(f):
                outfiletarget = 'file://localhost/' + local_job_dir
                if filter is not None:
                    try:
                        if re.match(filter, str(f)):
                            logger.info("Copying output file " + f)
                            remote_dir.copy(f, outfiletarget)
                    except Exception as e:
                        logger.error("Error in filter, defaulting to copying output file " + f)
                        # filter failed, fallback to copying the file rather than losing data
                        remote_dir.copy(f, outfiletarget)
                else:
                    outfiletarget = 'file://localhost/' + local_job_dir
                    remote_dir.copy(f, outfiletarget)

            else:
                path = str(f)
                local_copy_dir = os.path.join(local_job_dir, path)
                copy_remote_directory_to_local(remote_dir.open_dir(f), local_copy_dir, base_url, filter, logger)

        return 0

    except saga.SagaException as ex:
        # Catch all saga exceptions
        print('An exception occured: {0} {1}'.format(ex.type, ex))
        # Trace back the exception. That can be helpful for debugging.
        print('Backtrace: {}'.format(ex.traceback))
        return -1
    except Exception as e:
        print("error in staging: {}".format(e.message))
        return -1



def get_saga_job_state(job_id, service):

    session = create_session_for_service(service)

    js = saga.job.Service(service['scheduler_url'], session)
    job = js.get_job(job_id)
    state = job.state
    js.close()
    return state





def cleanup_directory(remote_dir, service):

    try:
        session = create_session_for_service(service)
        remote_dir = saga.filesystem.Directory(service['file_url'] + remote_dir, session=session)

        for f in remote_dir.list():
            if remote_dir.is_file(f):
                try:
                    remote_dir.remove(f)
                except Exception as e:
                    raise e
            else:
                cleanup_subdir(remote_dir.open_dir(f))
    except Exception as e:
        raise e


def cleanup_subdir(dir):
    for f in dir.list():
        if dir.is_file(f):
            try:
                dir.remove(f)
            except Exception as e:
                raise e
        else:
            cleanup_subdir(dir.open_dir(f))


def create_session_for_service(service):

    try:

        #ctx = saga.Context("UserPass")
        #ctx.user_id = service['username']
        #ctx.user_pass = service['user_pass']

        ctx = saga.Context("SSH")
        ctx.user_id = service['username']
        ctx.user_key = service['user_key']
        ctx.user_pass = service['user_pass']

        # create a session and pass our context
        session = saga.Session()
        session.add_context(ctx)
        return session
    except Exception as e:
        raise e



def main():
    cleanup_directory("/lustre/home/z04/millingw/0635fe93-2f02-4c0a-982d-f4bc35d9926f")



if __name__ == "__main__":
    main()