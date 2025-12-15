import logging
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client("s3")
logger = logging.getLogger(__name__)


def s3_event_record_to_bucket_and_key(record) -> tuple[str, str]:
    """
    Take the S3 event record and return the bucket name and key.
    """
    return record["s3"]["bucket"]["name"], unquote_plus(record["s3"]["object"]["key"])


def s3_download_object_to_file(bucket, key, file_path):
    """
    Download an object from S3 to a local file.
    """
    logger.debug(f"Downloading {key} from bucket {bucket} into {file_path}.")
    with open(file_path, "wb") as file:
        s3.download_fileobj(Bucket=bucket, Key=key, Fileobj=file)
    logger.debug(f"Downloaded {key} from bucket {bucket} into {file_path}.")


def s3_upload_file_to_bucket(bucket, key, file_path):
    """
    Upload a local file to S3.
    """
    logger.debug(f"Uploading {file_path} to bucket {bucket} as {key}.")
    with open(file_path, "rb") as file:
        s3.upload_fileobj(file, Bucket=bucket, Key=key)
    logger.debug(f"Uploaded {file_path} to bucket {bucket} as {key}.")
