import pytest

from gewv_timeseries_client import TimeseriesClient


@pytest.fixture
def client() -> TimeseriesClient:
    return TimeseriesClient(
        host="localhost",
        port=8086,
        token="mySuP3rS3cr3tT0keN",
        organization="test-org",
        verify_ssl=False,
    )


def test_init(client: TimeseriesClient):
    assert type(client) == TimeseriesClient


def test_exist_bucket(client: TimeseriesClient):
    bucket_name = "test-bucket"

    assert client.exist_bucket(bucket=bucket_name)


def test_create_bucket(client: TimeseriesClient):
    bucket_name = "test-create-bucket"
    client.create_bucket(bucket_name)

    assert client.exist_bucket(bucket_name)


def test_delete_bucket(client: TimeseriesClient):
    bucket_name = "test-delete-bucket"
    client.create_bucket(bucket_name)

    assert client.exist_bucket(bucket_name)

    client.delete_bucket(bucket_name)

    assert not client.exist_bucket(bucket_name)
