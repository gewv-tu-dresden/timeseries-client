from dotenv import load_dotenv
import pandas as pd
from gewv_timeseries_client import TimeseriesClient
from influxdb_client import Point
from datetime import datetime, timedelta
from pytz import UTC
from loguru import logger

load_dotenv()

# Use .env-file for the credentials and the address
# INFLUXDB_V2_URL=<db_host>
# INFLUXDB_V2_ORG=<org_id>
# INFLUXDB_V2_TOKEN=<token>

PROJECT = "EXPERIMENTAL"


def read_and_write_data():
    client = TimeseriesClient.from_env_properties()

    # write single points
    _start_points = datetime.now(UTC)
    _point1 = (
        Point("test_single_point")
        .tag("location", "Prague")
        .field("temperature", 25.3)
        .time(_start_points)
    )
    _point2 = (
        Point("test_single_point")
        .tag("location", "New York")
        .field("temperature", 24.3)
        .time(_start_points)
    )
    client.write_points(project=PROJECT, points=[_point1, _point2])

    # write a dataframe
    _start_dataframe = datetime.now(UTC)
    _dataframe = pd.DataFrame(
        data=[["coyote_creek", 1.0], ["coyote_creek", 2.0]],
        index=[_start_dataframe, _start_dataframe + timedelta(hours=1)],
        columns=["location", "water_level"],
    )
    client.write_a_dataframe(
        project=PROJECT,
        measurement_name="test_dataframe",
        dataframe=_dataframe,
        tag_columns=["location"],
    )

    # read single points
    points = client.get_points(
        project=PROJECT,
        fields={"_measurement": "test_single_point"},
        start_time=_start_points,
    )
    logger.info("Request Points:")
    results = []
    for table in points:
        for record in table.records:
            results.append((record.get_value(), record.get_field()))

    print(results)

    # read a dataframe
    dataframe = client.get_dataframe(
        project=PROJECT,
        fields={"_measurement": "test_dataframe", "_field": "water_level"},
        start_time=_start_dataframe,
    )
    logger.info("Requested Dataframe:")
    logger.info(dataframe)


if __name__ == "__main__":
    read_and_write_data()
