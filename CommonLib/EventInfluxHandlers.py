import json
import time

import pytz
from locust import events
import socket
import datetime
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class EventInfluxHandlers:

    hostname = socket.gethostname()
    # data_base_name = "locustdb"
    table_name = "REST_Table"

    my_bucket = "my-init-bucket"
    token = "secret-token"
    org = "my-init-org"

    # export INFLUX_TOKEN=AD0fi6bp6_COJhWRjxsXxKHeO-w7m9x2myIM5S6OXaAuEcwUtAgxw45QUS2Pzs7MwGCHnqcw-qQyU1pki2EUhA==

    influxDbClient = InfluxDBClient(url="http://localhost:8086", token=token, org=org, bucket=my_bucket)

    def __init__(self, token, org, bucket):
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClient(url="http://localhost:8086", token=token)

    @staticmethod
    def init_influx_client():
        # EventInfluxHandlers.influxDbClient.drop_database(EventInfluxHandlers.data_base_name)
        # EventInfluxHandlers.influxDbClient.create_database(EventInfluxHandlers.data_base_name)
        # EventInfluxHandlers.influxDbClient.switch_database(EventInfluxHandlers.data_base_name)

        # delete_api = EventInfluxHandlers.influxDbClient.delete_api()

        # """
        # Delete Data
        # """
        # start = "1970-01-01T00:00:00Z"
        # stop = "2025-02-01T00:00:00Z"
        # delete_api.delete(start, stop, '_measurement="measurement1"', bucket=EventInfluxHandlers.my_bucket,
        #                   org=EventInfluxHandlers.org)
        #
        # write_api = EventInfluxHandlers.influxDbClient.write_api(write_options=SYNCHRONOUS)
        #
        # for value in range(5):
        #     point = (
        #         Point("measurement1")
        #         .tag("tagname1", "tagvalue1")
        #         .field("field1", value)
        #     )
        #     write_api.write(bucket=EventInfluxHandlers.my_bucket, org="my-init-org", record=point)
        #     time.sleep(1) # separate points by 1 second

        query_api = EventInfluxHandlers.influxDbClient.query_api()

        query = """from(bucket: "my-init-bucket")
         |> range(start: -10m)
         |> filter(fn: (r) => r._measurement == "MSFT_2021-10-29")"""
        tables = query_api.query(query, org="my-init-org")

        for table in tables:
            for record in table.records:
                print(record)

        # """
        # Close client
        # """
        # EventInfluxHandlers.influxDbClient.close()
    @staticmethod
    @events.request.add_listener
    def my_request_handler(request_type, name, response_time, response_length, response,
                               context, exception, start_time, url, **kwargs):
        if exception:
            print(f"Request to {name} failed with exception {exception}")
            status = "FAILED"
            exception_text = exception
        else:
            print(f"Successfully made a request to: {name}")
            print(f"The response was {response.text}")
            status = "PASS"
            exception_text = ""

        success_temp = \
            ('[{"measurement": "%s",\
            "tags": {\
                "hostname": "%s",\
                "requestName": "%s",\
                "requestType": "%s",\
                "status": "%s", \
                "exception": "%s" \
                 },\
            "time": "%s",\
            "fields": {\
                "responseTime": "%s",\
                "responseLength": "%s"\
            }\
         }]')

        write_api = EventInfluxHandlers.influxDbClient.write_api(write_options=SYNCHRONOUS)

        json_string = success_temp % ('measurement2', EventInfluxHandlers.hostname, name, request_type,
                                      status, exception_text, datetime.datetime.now(tz=pytz.UTC), response_time, response_length)

        write_api.write(bucket=EventInfluxHandlers.my_bucket, org="my-init-org", record=json.loads(json_string))
        time.sleep(1)  # separate points by 1 second

        # EventInfluxHandlers.influxDbClient.write_api(json.loads(json_string))

        query_api = EventInfluxHandlers.influxDbClient.query_api()

        query = """from(bucket: "my-init-bucket")
             |> range(start: -10m)
             |> filter(fn: (r) => r._measurement == "measurement2")"""
        tables = query_api.query(query, org="my-init-org")

        for table in tables:
            for record in table.records:
                print(record)