#%%
import pandas as pd
import gym
import gym_optsb
from datetime import datetime
from dotenv import load_dotenv, main
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient

#%%
load_dotenv()
url = os.getenv('URL')
token = os.getenv('TOKEN')
org = os.getenv('ORG')
bucket = os.getenv('BUCKET')
print(url,bucket)

client = InfluxClient(url, token, org, bucket) #connected to db
#CheckStatusLevel(client.return_client())
#Need some way to check Client is connected

#%%s
env = gym.make("optsb-v0")
env.client_connect(client,bucket)
env.reset()
#%%
#pick random action, process step
action_val = 4
state, reward, _, _ = env.step(action_val)
# %%
max_time = state[0]['_time'].values.max()
print(state)
# need to return only proper data in state, or build proper array
#int(v: max_time)


#%%
for i in range(4):
    state, reward, done, info = env.step(i)
    print(reward)

# %%
#%% misc db stuff
for i in range(2):
    data = [ Point('Data').tag("type","detector").tag("location","target")
        .field("pos1",i).field("pos2",2.).field("rate1",i+1.).field("rate2",6.)
        .time(time=datetime.utcnow())]
    client.write_data(data)

client.delete_data("Data")

# %%
