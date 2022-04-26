from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

class InfluxClient:
    def __init__(self,url,token,org,bucket): 
        self._url=url
        self._org=org 
        self._bucket = bucket
        self._client = InfluxDBClient(url=url, token=token, org=org)
    
    def return_client(self):
        return self._client

    def write_data(self,data,write_option=ASYNCHRONOUS):
        write_api = self._client.write_api(write_option)
        write_api.write(self._bucket, self._org , data, write_precision='s')

    def write_data_df(self,df,measure_name,write_option=ASYNCHRONOUS):
        write_api = self._client.write_api(write_option)
        write_api.write(self._bucket,record=df,data_frame_measurement_name=measure_name)

    def query_data(self,query): 
        query_api = self._client.query_api()
        result = query_api.query_data_frame(org=self._org, query=query)
        # results = []
        # for table in result:
        #     for record in table.records:
        #         results.append((record.get_value(), record.get_field()))
        #print(results)
        return result #dataframe

    def delete_data(self,measurement):
        delete_api = self._client.delete_api()
        start = "1970-01-01T00:00:00Z"
        stop = datetime.utcnow()#"2021-10-30T00:00:00Z"
        delete_api.delete(start, stop, f'_measurement="{measurement}"', 
        bucket=self._bucket, org=self._org)
