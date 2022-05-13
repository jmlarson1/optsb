#%%
## lets go incorp q-learning ?? why not...
import pandas as pd
import gym
import gym_optsb
from datetime import datetime
from dotenv import load_dotenv, main
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import tqdm
import numpy as np
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from run_track import RunTRACK
from nn_policy import MultiLayerPolicy

#%% gym setup
env = gym.make("optsb-v0")
env.reset()

# policy setup
input_dim = env.observation_space
hidden_dim = 32
hidden_dim2 = 24
output_dim = env.action_space
print("in {}, out {}".format(input_dim, output_dim))

num_episodes = 1
num_steps = 10
discount_factor = 0.5
start_epsilon = 1.0
end_epsilon = 0.01
epsilon_decay = 0.995

train_rewards = torch.zeros(num_steps, num_episodes)
test_rewards = torch.zeros(num_steps, num_episodes)
train_loss = torch.zeros(num_steps, num_episodes)
train_info = [dict() for i in range(num_steps*num_episodes)]
test_info = [dict() for i in range(num_steps*num_episodes)]
device = torch.device('cpu')

#%% MAIN RUN
reward_all_episodes = []
policy = MultiLayerPolicy(input_dim, hidden_dim, hidden_dim2, output_dim)
policy = policy.to(device)
# policy.apply(init_weights)
epsilon = start_epsilon
optimizer = optim.Adam(policy.parameters(), lr=0.001, betas=(0.9, 0.999))

for episode in range(num_episodes):
    # initialize new episode params
    state = env.reset()
    done = False
    rewards_current_episode = 0


    for step in tqdm.tqdm(range(num_steps), desc=f'Run {episode}'):
        policy.train()
        if np.random.random() < epsilon:
            action = env.querry_action()
        else:
            action = policy(state)
        next_state, reward, done, info = env.step(action)
        print(info)
        reward_all_episodes.append(reward)
        state = next_state
        loss = 1.#update_policy(policy, state, action, reward, next_state, discount_factor, optimizer)

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
