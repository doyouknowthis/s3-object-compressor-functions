import os
from pathlib import Path

import boto3
import pytest
from moto import mock_aws


@pytest.fixture()
def get_file():
    def _(file_path: str):
        return (Path(__file__).parent / file_path).read_bytes()

    return _


@pytest.fixture(scope="function")
def aws_credentials():
    """Set up mocked AWS credentials for pytest.

    This fixture sets fake credentials in environment variables.
    Required to be run BEFORE any boto3 clients/resources are created.
    """
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    yield


@pytest.fixture(scope="function")
def mocked_aws(aws_credentials):
    """Mock all AWS interactions using moto.

    Use this fixture if your tests interact with multiple AWS services.
    The mock_aws() context manager intercepts all boto3 calls.
    """
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def s3_client(aws_credentials):
    """Return a mocked S3 client.

    Example usage in tests:
        def test_s3_operation(s3_client):
            s3_client.create_bucket(Bucket="test-bucket")
            # ... test code
    """
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")
