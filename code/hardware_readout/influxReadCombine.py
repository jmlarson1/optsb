#%% https://docs.influxdata.com/influxdb/v1.8/tools/api_client_libraries/#python
#imports
import argparse
import pandas as pd
from influxdb_client import InfluxDBClient, Point
#from influxdb_client.client.write_api import SYNCHRONOUS

#%%
# setup db connection
bucket = "my-bucket"
client = InfluxDBClient(url="http://raisordaq.onenet:8086") #, token="my-token", org="my-org")
#write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

#%% read from db to panda
#p = Point("my_measurement").tag("location", "Prague").field("temperature", 25.3)
#write_api.write(bucket=bucket, record=p)
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
