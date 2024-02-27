from datetime import datetime
from dotenv import load_dotenv
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from datetime import datetime
import csv


class InfluxClient:
    def __init__(self, token, org, bucket):
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClient(url="http://localhost:8086", token=token)

    def write_data(self, data, write_option=SYNCHRONOUS):
        write_api = self._client.write_api(write_option)
        write_api.write(self._bucket, self._org, data, write_precision='s')

    def query_data(self, query):
        query_api = self._client.query_api()
        result = query_api.query(org=self._org, query=query)
        results = []
        for table in result:
            for record in table.records:
                results.append((record.get_value(), record.get_field()))
        print(results)
        return results

    def delete_data(self, measurement):
        delete_api = self._client.delete_api()
        start = "1970-01-01T00:00:00Z"
        stop = "2025-10-30T00:00:00Z"
        delete_api.delete(start, stop, f'_measurement="{measurement}"', bucket=self._bucket, org=self._org)

    def delete_all_data(self, measurements):
        for mea in measurements:
            self.delete_data(mea)

load_dotenv()
token = os.getenv('TOKEN')
org = os.getenv('ORG')
bucket = os.getenv('BUCKET')

IC = InfluxClient(token, org, bucket)

'''
Write Data for MSFT Stock
'''
script_dir = os.path.dirname(__file__)
abs_file_path = os.path.join(script_dir, 'MSFT.csv')

MSFT_file = open(abs_file_path)
csvreader = csv.reader(MSFT_file)
header = next(csvreader)
rows = []
# for row in csvreader:
#     date, open, high, low = row[0], row[1], row[2], row[3]
#     line_protocol_string = ''
#     line_protocol_string +=f'MSFT_{date},'
#     line_protocol_string += f'stock=MSFT '
#     line_protocol_string += f'Open={open},High={high},Low={low} '
#     line_protocol_string += str(int(datetime.strptime(date, '%Y-%m-%d').timestamp()))
#     rows.append(line_protocol_string)

# for row in csvreader:
#     date = row[0]
#     line_protocol_string = f"MSFT_{date}"
#     rows.append(line_protocol_string)

print(rows)
# IC.write_data(rows)

IC.write_data(["MSFT_2021-10-29,stock=MSFT Open=62.80,High=63.85,Low=62.15"])

'''
    Return the High Value for MSFT stock for since 1st October,2021
'''
query1 = 'from(bucket: "my-init-bucket")\
|> range(start: 1633124983)\
|> filter(fn: (r) => r._field == "High")\
|> filter(fn: (r) => r._measurement == "MSFT_2021-10-29")'
IC.query_data(query1)

# IC.delete_data("MSFT_2021-10-29")
# IC.delete_all_data(rows)

'''
    Return the High Value for the MSFT stock on 2021-10-29
'''
query2 = 'from(bucket: "my-init-bucket")\
|> range(start: 1633124983)\
|> filter(fn: (r) => r._field == "High")\
|> filter(fn: (r) => r._measurement == "MSFT_2021-10-29")'
IC.query_data(query2)
