import logging
import os

from PIL import Image
from aws_lambda_typing import context as context_, events

from functions.common import s3_event_record_to_bucket_and_key, s3_download_object_to_file, s3_upload_file_to_bucket

logger = logging.getLogger(__name__)

IMAGE_JPG_COMPRESS_QUALITY = os.environ.get("IMAGE_JPG_COMPRESS_QUALITY", 75)


def lambda_handler(event: events.S3Event, context: context_.Context) -> None:
    """
    Lambda function to process image uploads.
    """
    for record in event["Records"]:
        bucket, key = s3_event_record_to_bucket_and_key(record)

        logger.info(f"Processing {key} from bucket {bucket}.")

        file_name, file_ext = os.path.splitext(os.path.basename(key))
        tmp_file_in = f"/tmp/{os.path.basename(key)}"
        tmp_file_out = f"/tmp/compressed_{os.path.basename(key)}"

        logger.info(f"Downloading {key} from bucket {bucket} into {tmp_file_in}.")

        s3_download_object_to_file(bucket, key, tmp_file_in)

        logger.info(f"Compressing {key}.")

        compress_image(tmp_file_in, tmp_file_out, IMAGE_JPG_COMPRESS_QUALITY)

        new_key = f"{file_name}_compressed{file_ext}"
        logger.info(f"Uploading compressed object {tmp_file_out} to bucket {bucket} with key {new_key}.")

        s3_upload_file_to_bucket(bucket, new_key, tmp_file_out)


def compress_image(tmp_file_in: str, tmp_file_out: str, jpg_compress_quality: int) -> None:
    file_name, file_ext = os.path.splitext(os.path.basename(tmp_file_in))

    with Image.open(tmp_file_in) as img:
        if file_ext.lower() == ".png":
            logger.info("Compressing PNG image.")
            img.save(tmp_file_out, 'PNG', optimize=True)
        elif file_ext.lower() == ".jpg" or file_ext.lower() == ".jpeg":
            logger.info("Compressing JPEG image.")
            img.save(tmp_file_out, 'JPEG', optimize=True, quality=jpg_compress_quality)
        else:
            logger.error(f"Unsupported file extension: {file_ext}")
            raise Exception(f"Unsupported file extension: {file_ext}")
