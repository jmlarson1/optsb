#%% https://docs.influxdata.com/influxdb/v1.8/tools/api_client_libraries/#python
#imports
import argparse
import pandas as pd
from influxdb import DataFrameClient
from influxdb_client import InfluxDBClient, Point
from influxdb_client.rest import ApiException
#from influxdb_client.client.write_api import SYNCHRONOUS

#%%
#variables
hostname="raisordaq.onenet"
portnumber=8086
uname="admin"
dbname="db"
df = pd.DataFrame()
#%%
# older way to connect and read
client = DataFrameClient(host=hostname, port=portnumber, database=dbname)
result = client.query('select * from fc') #returns a list

_data_frame = result['fc']
print(list(_data_frame.columns))
tmp = list(_data_frame.columns)
print(_data_frame[['value']])

# %%
