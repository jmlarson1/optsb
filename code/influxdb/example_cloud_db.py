#%%
from datetime import datetime
from dotenv import load_dotenv, main
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client.version import CLIENT_VERSION
from influx_client import InfluxClient
#%% get database info
load_dotenv()
url = os.getenv('URL')
token = os.getenv('TOKEN')
org = os.getenv('ORG')
bucket = os.getenv('BUCKET')

#%% main

client = InfluxClient(url, token, org, bucket) #connected to db
query1 = f'from(bucket: "{bucket}") \
    |> range(start: -1d) \
    |> filter(fn: (r) => r["_measurement"] == "Data")'
#%%
for i in range(2):
    data = [
        Point('Data')
        .tag("type","detector")
        .tag("location","target")
        .field("pos1",i)
        .field("pos2",2.)
        .field("rate1",i+1.)
        .field("rate2",6.)
        .time(time=datetime.utcnow())
    ]
    client.write_data(data)

#%%
#query = f'from(bucket: "{bucket}") |> range(start: -1d) |> filter(fn: (r) => r._measurement == "{kind}")'
query1 = f'from(bucket: "{bucket}") \
    |> range(start: -1d) \
    |> filter(fn: (r) => r["_measurement"] == "Data")'

df_query1 = client.query_data(query1)
#%%
s
#%%
client.delete_data("Data")

# %%
