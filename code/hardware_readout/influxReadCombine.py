#%% https://docs.influxdata.com/influxdb/v1.8/tools/api_client_libraries/#python
#imports
import argparse
import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.rest import ApiException
#from influxdb_client.client.write_api import SYNCHRONOUS

#%%
# setup / check db connection
bucket = "my-bucket"
client = InfluxDBClient(url="http://raisordaq.onenet:8086", token="my-token", org="my-org")
#write_api = client.write_api(write_options=SYNCHRONOUS)

"""Check that the InfluxDB is running."""
print("> Checking connection ...", end=" ")
client.api_client.call_api('/ping', 'GET')
print("ok")

#%%
#query check too
"""Check that the credentials has permission to query from the Bucket"""
print("> Checking credentials for query ...", end=" ")
try:
    client.query_api().query(f"from(bucket:\"{bucket}\") |> range(start: -1m) |> limit(n:1)", "my-org")
except ApiException as e:
    # missing credentials
    if e.status == 404:
        raise Exception(f"The specified token doesn't have sufficient credentials to read from '{bucket}' "
                        f"or specified bucket doesn't exists.") from e
    raise
print("ok")

#%% read from db to panda
#p = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
#write_api.write(bucket=bucket, record=p)
query_api = client.query_api()
data_frame = query_api.query_data_frame('from(bucket:"my-bucket") '
                                        '|> range(start: -10m) ')
print(data_frame.to_string())

#%%
#Close client
client.close()

#%%
## using Table structure
# tables = query_api.query('from(bucket:"my-bucket") |> range(start: -10m)')

# for table in tables:
#     print(table)
#     for row in table.records:
#         print (row.values)


# ## using csv library
# csv_result = query_api.query_csv('from(bucket:"my-bucket") |> range(start: -10m)')
# val_count = 0
# for row in csv_result:
#     for cell in row:
#         val_count += 1
