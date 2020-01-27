import boto3
from botocore.exceptions import ClientError

from wos_utils import s3_list_files_for_job, s3_upload, s3_delete_files_for_job, get_presigned_url

import os
import uuid
from tests.test_params import TEST_UPLOAD_FILE
import requests


def test_wos_access():
    try:
        job_uuid = str(uuid.uuid4())
        path = job_uuid + "/" + os.path.basename(TEST_UPLOAD_FILE)
        s3_upload(TEST_UPLOAD_FILE, path)
        files = s3_list_files_for_job(job_uuid)
        assert(files[0] == os.path.basename(TEST_UPLOAD_FILE))
        presigned_url = get_presigned_url(path)
        response = requests.get(presigned_url)
        assert(response.status_code==200)

        # compare the contents to make sure we got the right file
        with open(TEST_UPLOAD_FILE, mode='rb') as file:
            fileContent = file.read()
            assert(fileContent == response.content)

        s3_delete_files_for_job(job_uuid)
        response = requests.get(presigned_url)
        assert(response.status_code==404)

    except Exception as e:
        raise e


if __name__ == '__main__':
    test_wos_access()

