from timeseries_client import TimeseriesClient


def test_init():
    client = TimeseriesClient(host="localhost", port=8886, token="test")
    assert type(client) == TimeseriesClient
