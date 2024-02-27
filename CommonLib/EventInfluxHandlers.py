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
    data_base_name = "locustdb"
    table_name = "REST_Table"

    my_bucket = "my-init-bucket"
    token = "secret-token"
    org = "my-init-org"

    influxDbClient = InfluxDBClient(url="http://localhost:8086", token=token, org=org, bucket=my_bucket)

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
         |> filter(fn: (r) => r._measurement == "measurement1")"""
        tables = query_api.query(query, org="my-init-org")

        for table in tables:
            for record in table.records:
                print(record)

        # """
        # Close client
        # """
        # EventInfluxHandlers.influxDbClient.close()
    @staticmethod
    # @events.request.add_listener
    # def request_success_handlers(request_type, name, response_time, response_length, **kwagrs):
    def my_request_handler(request_type, name, response_time, response_length, response,
                               context, exception, start_time, url, **kwargs):
        if exception:
            print(f"Request to {name} failed with exception {exception}")
        else:
            print(f"Successfully made a request to: {name}")
            print(f"The response was {response.text}")
        success_temp = \
            '[{"measurement": "%s",\
            "tags": {\
                "hostname": "%s",\
                "requestName": "%s",\
                "requestType": "%s",\
                "status": "%s"\
            },\
            "time": "%s",\
            "fields": {\
                "responseTime": "%s",\
                "responseLength": "%s"\
            }\
         }]'

        write_api = EventInfluxHandlers.influxDbClient.write_api(write_options=SYNCHRONOUS)

        json_string = success_temp % ('measurement2', EventInfluxHandlers.hostname, name, request_type,
                                      "PASS", datetime.datetime.now(tz=pytz.UTC), response_time, response_length)

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

    # @staticmethod
    # @events.request_failure.add_listener
    # def request_failure_handlers(request_type, name, response_time, response_length, exception, **kwagrs):
    #     failure_temp = \
    #         '[{"measurement": "%s",\
    #         "tags": {\
    #             "hostname": "%s",\
    #             "requestName": "%s",\
    #             "requestType": "%s",\
    #             "status": "%s",\
    #             "exception": "%s"\
    #         },\
    #         "time": "%s",\
    #         "fields": {\
    #             "responseTime": "%s",\
    #             "responseLength": "%s"\
    #         }\
    #      }]'
    #
    #     json_string = failure_temp % (EventInfluxHandlers.table_name, EventInfluxHandlers.hostname, name, request_type,
    #                                   "FAIL", exception, datetime.datetime.now(tz=pytz.UTC),
    #                                   response_time, response_length)
    #     EventInfluxHandlers.influxDbClient.write_points(json.loads(json_string))
    #
    