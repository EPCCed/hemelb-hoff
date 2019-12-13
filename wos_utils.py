import boto3
import os
from botocore.exceptions import ClientError

from config import CIRRUS_WOS_ACCESS_KEY
from config import CIRRUS_WOS_SECRET_KEY
from config import CIRRUS_WOS_HOFF_BUCKET
from config import CIRRUS_S3_ENDPOINT
from config import CIRRUS_S3_DEFAULT_REGION


def get_s3_client():
    s3_client = boto3.client('s3', endpoint_url=CIRRUS_S3_ENDPOINT, aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
                             aws_secret_access_key=CIRRUS_WOS_SECRET_KEY, region_name=CIRRUS_S3_DEFAULT_REGION,
                             verify=False)
    return s3_client


def get_bucket():
    s3 = boto3.resource('s3', endpoint_url=CIRRUS_S3_ENDPOINT, aws_access_key_id=CIRRUS_WOS_ACCESS_KEY,
                             aws_secret_access_key=CIRRUS_WOS_SECRET_KEY, region_name=CIRRUS_S3_DEFAULT_REGION,
                             verify=False)
    bucket = s3.Bucket(CIRRUS_WOS_HOFF_BUCKET)
    return bucket


def get_presigned_url(path):
    bucket_name = CIRRUS_WOS_HOFF_BUCKET
    s3_client = get_s3_client()

    return s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': path,
        }
    )

def s3_upload(local_path, remote_path):
    bucket = get_bucket()
    with open(local_path, 'rb') as data:
        bucket.upload_fileobj(data, remote_path)


def s3_list_files_for_job(job_id):
    s3_client = get_s3_client()
    prefix = job_id + "/"
    result = s3_client.list_objects(Bucket=CIRRUS_WOS_HOFF_BUCKET, Prefix=prefix)

    # note that s3 paginates after 1000 objects
    # we assumes that Hoff / Hemelb jobs only produce a small number of files, so we can get away with this
    # otherwise we will have to paginate

    if 'Contents' not in result:
        return []

    keys = []
    for key in result['Contents']:
        keys.append(key['Key'].replace(prefix,""))
    return keys


def s3_delete_files_for_job(job_id):
    if job_id is None:
        return
    if len(job_id) == 0:
        return

    bucket = get_bucket()
    filter = job_id + '/'

    # warning - the next line may only work if there are less than 1000 objects present,
    # otherwise a paginating solution is needed
    # for Hoff / Hemelb jobs we should get away with this ok

    for obj in bucket.objects.filter(Prefix=filter):
        obj.delete()





