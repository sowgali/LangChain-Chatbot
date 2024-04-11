from typing import Tuple
from typing import Any
import boto3
import logging
logger = logging.getLogger()
logger.setLevel("INFO")



_S3_CLIENT = None
S3_PREFIX = "s3://"
S3_REGION = "us-east-1"
_S3_RESOURCE = None


def get_client() -> Any:
    global _S3_CLIENT
    if _S3_CLIENT is None:
        _S3_CLIENT = boto3.client('s3')
    return _S3_CLIENT


def get_resource() -> Any:
    global _S3_RESOURCE
    if _S3_RESOURCE is None:
        _S3_RESOURCE = boto3.resource('s3')
    return _S3_RESOURCE


def is_valid_s3_path(path: str) -> bool:
    return path.startswith(S3_PREFIX)


def _parse_s3_path(path: str) -> Tuple[str, str]:
    assert is_valid_s3_path(path)

    pruned = path[len(S3_PREFIX):]
    if '/' not in pruned:
        return pruned, ''
    index_first_slash = pruned.index('/')
    bucket = pruned[0:index_first_slash]
    suffix = pruned[index_first_slash + 1:]
    return bucket, suffix


def copy_file_to_s3(local_full_path: str, remote_full_path: str) -> bool:
    bucket_name, s3_file_name = _parse_s3_path(remote_full_path)
    logger.debug("Uploading {} to {}:{}".format(local_full_path, bucket_name, s3_file_name))
    get_client().upload_file(local_full_path, bucket_name, s3_file_name)
    logger.debug("Done")
    return True


def write_to_s3(remote_full_path: str, content: str) -> bool:
    bucket_name, s3_file_name = _parse_s3_path(remote_full_path)
    s3 = get_resource().Bucket(bucket_name)
    logger.debug("Uploading content to {}:{}".format(bucket_name, s3_file_name))
    logger.verbose("Content = {}".format(content))
    s3.Object(key=s3_file_name).put(Body=content)
    logger.debug("Done")
    return True


def read_from_s3(remote_full_path: str) -> str:
    bucket_name, s3_file_name = _parse_s3_path(remote_full_path)
    s3 = get_resource().Bucket(bucket_name)
    logger.debug("Downloading content from {}:{}".format(bucket_name, s3_file_name))
    output = s3.Object(key=s3_file_name).get()['Body'].read()
    logger.debug("Done")
    return output.decode("utf-8")