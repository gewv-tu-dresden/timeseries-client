from influxdb_client import InfluxDBClient
from influxdb_client.client.write.point import Point
from influxdb_client.domain.organization import Organization
from influxdb_client.rest import ApiException
from influxdb_client.client.flux_table import FluxTable
from datetime import datetime
from typing import List, Union, Optional, Dict
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd


class TimeseriesClient:
    host: Union[str, None]
    port: int
    token: Union[str, None]
    organization: str

    def __init__(
        self,
        host: str = None,
        port: int = None,
        organization: str = "GEWV",
        token: str = None,
        client: InfluxDBClient = None,
        verify_ssl: bool = True,
    ):
        if client is None:
            if host is None:
                raise Exception("Missing Host Address for Timeseries DB Client.")

            if port is None:
                raise Exception("Missing Port for Timeseries DB Client.")

            if token is None:
                raise Exception("Missing Token for Timeseries DB Client.")

            protocol = "https" if verify_ssl else "http"

            self._client = InfluxDBClient(
                url=f"{protocol}://{host}:{port}",
                token=token,
                verify_ssl=verify_ssl,
            )
        else:
            self._client = client

        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
        self._query_api = self._client.query_api()
        self._bucket_api = self._client.buckets_api()
        self._org_api = self._client.organizations_api()

        self._org_id = self.get_org_id_by_name(org_name=organization)

        if self._org_id is None:
            raise Exception(
                f"The organization {organization} dont exists in InfluxDB. Break execution."
            )

        self._client.org = self._org_id

    @staticmethod
    def from_env_properties():
        client = InfluxDBClient.from_env_properties()
        return TimeseriesClient(client=client)

    def health(self):
        return self._client.health()

    def get_org_id_by_name(self, org_name: str) -> Union[str, None]:
        orgs: List[Organization] = self._org_api.find_organizations()
        for org in orgs:
            if org.name == org_name:
                return org.id

        return None

    def create_bucket(self, bucket: str):
        try:
            self._bucket_api.create_bucket(bucket_name=bucket)
        except ApiException as err:
            if err.status != 422:
                raise

    def exist_bucket(self, bucket: str):
        return self._bucket_api.find_bucket_by_name(bucket_name=bucket)

    def create_project(self, project_name: str):
        # Steps
        # 1. create new bucket
        # 2. create token for bucket
        # 3. create new org in grafana
        # 4. create new source in grafana
        pass

    def get_points(
        self,
        **kwargs,
    ) -> List[FluxTable]:
        if not self.health:
            raise Exception("Influx DB is not reachable or unhealthy.")

        tables = self._query_api.query(query=self.build_query(**kwargs))

        return tables

    def get_dataframe(self, **kwargs):
        if not self.health:
            raise Exception("Influx DB is not reachable or unhealthy.")

        df = self._query_api.query_data_frame(query=self.build_query(**kwargs))

        return df

    def write_points(self, project: str, points: List[Point]):
        self._write_api.write(bucket=project, record=points)

    def write_a_dataframe(
        self,
        project: str,
        measurement_name: str,
        dataframe: pd.DataFrame,
        tag_columns: List[str] = [],
        additional_tags: Dict[str, str] = None,
    ):
        """
        Write a pandas dataframe to the influx db. You can define some
        tags, that are appended to every entry.
        """

        if additional_tags is None:
            self._write_api.write(
                bucket=project,
                record=dataframe,
                data_frame_measurement_name=measurement_name,
                data_frame_tag_columns=tag_columns,
            )
            return

        tags_dataframe = pd.DataFrame(index=dataframe.index)

        # create the dataframe with the tags
        for tag_name, tag in additional_tags.items():
            tag_columns.append(tag_name)
            tags_dataframe[tag_name] = [tag] * len(dataframe)

        combined_frames = pd.concat([dataframe, tags_dataframe], axis=1)

        self._write_api.write(
            bucket=project,
            record=combined_frames,
            data_frame_measurement_name=measurement_name,
            data_frame_tag_columns=tag_columns,
        )

    def build_query(
        self,
        project: str,
        fields: Dict[str, str] = {},
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        precision: str = "5m",
    ) -> str:

        query = f"""
            from(bucket: "{project}")
        """

        if start_time is not None and end_time is not None:
            self.test_datetime(start_time)
            self.test_datetime(end_time)

            query += f"""
                |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
            """
        elif start_time is not None:
            self.test_datetime(start_time)

            query += f"""
                |> range(start: {start_time.isoformat()})
            """

        elif end_time is not None:
            self.test_datetime(end_time)

            query += f"""
                |> range(stop: {end_time.isoformat()})
            """

        for f, v in fields.items():
            query += f"""
                |> filter(fn: (r) => r["{f}"] == "{v}")
            """

        query += f"""
            |> aggregateWindow(every: {precision}, fn: mean, createEmpty: true)
            |> yield(name: "mean")
        """

        return query

    @staticmethod
    def test_datetime(dt: datetime):
        if not isinstance(dt, datetime):
            raise Exception(f"The delivered datetime {dt} is not from type datetime.")

        if dt.tzinfo is None:
            raise Exception(
                f"The time {dt.isoformat()} has no timezone info. That is necassary."
            )
