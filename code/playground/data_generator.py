#%%
## setup to run TRACK with random quad value in new directory (if testing is off)
## could be used to generate a lot of data
import pandas as pd
import gym
import gym_optsb
from datetime import datetime
from dotenv import load_dotenv, main
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from run_track import RunTRACK

#%%
env = gym.make("optsb-v0")
env.reset()
#%%
#pick random action, process step
df_results = pd.DataFrame()
reward_list=[]
action_list = []
state_list = []
for i in range (10):
    action = env.querry_action()#[1100,-2000,1250]
    action_list.append(action)
    state, reward, _, info = env.step(action)
    print(info)
    df_results = df_results.append(state, ignore_index = True)
    state_list.append(state)
    reward_list.append(reward)
    
df_results[['Q1','Q2','Q3']] = action_list
df_results["reward"] = reward_list

print(df_results)
#%%

temp = os.getcwd()
print(temp)

head, tail = os.path.split(os.getcwd())
head
# %%
#%% misc db stuff
# for i in range(2):
#     data = [ Point('Data').tag("type","detector").tag("location","target")
#         .field("pos1",i).field("pos2",2.).field("rate1",i+1.).field("rate2",6.)
#         .time(time=datetime.utcnow())]
#     client.write_data(data)

# client.delete_data("Data")

#%% future stuff for db with data

# #%%
# load_dotenv()
# url = os.getenv('URL')
# token = os.getenv('TOKEN')
# org = os.getenv('ORG')
# bucket = os.getenv('BUCKET')
# print(url,bucket)

# client = InfluxClient(url, token, org, bucket) #connected to db
# #CheckStatusLevel(client.return_client())
# #Need some way to check Client is connected

# #%%s
# env = gym.make("optsb-v0")
# env.client_connect(client,bucket)
# env.reset()


# %%
