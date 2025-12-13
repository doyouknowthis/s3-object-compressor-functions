import os

import boto3
from aws_lambda_typing import events
from moto import mock_aws

from functions.pdf.lambda_function import lambda_handler


@mock_aws
def test_handler(mocker, get_file):
    test_bucket = "test-bucket"
    test_key = "test-pdf.pdf"

    """
    Upload a file from resources/ so boto3.client can download it.
    """
    client = boto3.client("s3", region_name="us-east-1")
    client.create_bucket(Bucket=test_bucket)
    client.put_object(Bucket=test_bucket, Key=test_key, Body=get_file("./resources/gsw-short-paper-guidelines.pdf"))

    """
    Call the handler with a mock event.
    """
    event: events.S3Event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": test_bucket}, "object": {"key": test_key}
                }
            }
        ]
    }
    lambda_handler(event, None)

    """
    Assertions
    """
    assert os.path.exists(f"/tmp/compressed_{test_key}")
    objects_in_bucket = client.list_objects_v2(Bucket=test_bucket)
    assert len(objects_in_bucket["Contents"]) == 2

    file_name, file_ext = os.path.splitext(os.path.basename(test_key))
    assert objects_in_bucket["Contents"][1]["Key"] == f"{file_name}_compressed{file_ext}"
