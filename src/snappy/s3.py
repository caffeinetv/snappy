import boto3
from botocore.exceptions import ClientError
import logging
import unittest
import os
import ntpath
import tempfile
from snappy.settings import AWS_REGION

LOG = logging.getLogger(__name__)

def get_aws_resource(aws_resource):
    return boto3.resource(aws_resource, AWS_REGION)


def download_s3_obj(bucket, key):
    """
    Download the file from s3 given `bucket` and `key`.
    Returns
    -------
    str
        the filename of the downloaded file or None if the file was not found
    """
    f_info = bucket + ':' + key
    basename = ntpath.basename(key)
    name, ext = os.path.splitext(basename)
    LOG.info('Downloading file from s3 at {}'.format(f_info))
    s3_res = get_aws_resource('s3')
    code, tmp_file = tempfile.mkstemp()
    tmp_file = tmp_file + '.' + ext
    try:
        s3_res.Bucket(bucket).download_file(key, tmp_file)
    except ClientError:
        LOG.exception('File not found: {}'.format(f_info))
        return None
    return tmp_file


def get_s3_obj(bucket, key):
    """
    Get resource representing an s3 object given `bucket` and `key`.
    Returns
    -------
    S3.Object
        the s3 object or None if the object does not exist
    """
    f_info = bucket + ':' + key
    LOG.info('Getting s3 obj. at {}'.format(f_info))
    s3_res = get_aws_resource('s3')
    obj = s3_res.Object(bucket, key)
    try:
        obj.load()
    except ClientError:
        LOG.exception('File not found: {}'.format(f_info))
        return None
    return obj
    