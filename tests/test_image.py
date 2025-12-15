import os

from aws_lambda_typing import events

from functions.image.lambda_function import lambda_handler


def test_handler_png(get_file, s3_client):
    test_bucket = "test-bucket"
    test_key = "test-image.png"
    test_file = get_file("./resources/hatsune_miku.png")

    """
    Upload a file from resources/ so boto3.client can download it.
    """
    s3_client.create_bucket(Bucket=test_bucket)
    s3_client.put_object(Bucket=test_bucket, Key=test_key, Body=test_file)

    """
    Call the handler with a mock event.
    """
    event: events.S3Event = {
        "Records": [
            {"s3": {"bucket": {"name": test_bucket}, "object": {"key": test_key}}}
        ]
    }
    lambda_handler(event, None)

    """
    Assertions
    """
    assert os.path.exists(f"/tmp/compressed_{test_key}")
    objects_in_bucket = s3_client.list_objects_v2(Bucket=test_bucket)
    assert len(objects_in_bucket["Contents"]) == 2

    file_name, file_ext = os.path.splitext(os.path.basename(test_key))
    assert (
        objects_in_bucket["Contents"][1]["Key"] == f"{file_name}_compressed{file_ext}"
    )


def test_handler_jpg(get_file, s3_client):
    test_bucket = "test-bucket"
    test_key = "test-image.jpg"
    test_file = get_file("./resources/talara_puppy.jpg")

    """
    Upload a file from resources/ so boto3.client can download it.
    """
    s3_client.create_bucket(Bucket=test_bucket)
    s3_client.put_object(Bucket=test_bucket, Key=test_key, Body=test_file)

    """
    Call the handler with a mock event.
    """
    event: events.S3Event = {
        "Records": [
            {"s3": {"bucket": {"name": test_bucket}, "object": {"key": test_key}}}
        ]
    }
    lambda_handler(event, None)

    """
    Assertions
    """
    assert os.path.exists(f"/tmp/compressed_{test_key}")
    objects_in_bucket = s3_client.list_objects_v2(Bucket=test_bucket)
    assert len(objects_in_bucket["Contents"]) == 2

    file_name, file_ext = os.path.splitext(os.path.basename(test_key))
    assert (
        objects_in_bucket["Contents"][1]["Key"] == f"{file_name}_compressed{file_ext}"
    )
