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
def mocked_aws():
    """Mock all AWS interactions using moto.

    Use this fixture if your tests interact with multiple AWS services.
    The mock_aws() context manager intercepts all boto3 calls.
    """
    with mock_aws():
        yield


@pytest.fixture(scope="function")
def s3_client():
    """Return a mocked S3 client.

    Example usage in tests:
        def test_s3_operation(s3_client):
            s3_client.create_bucket(Bucket="test-bucket")
            # ... test code
    """
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")
