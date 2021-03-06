#%% to do
# - more plots via env render
# -- each step, rewards/DONE, actions/DONE, states ? ? 
# ---- new plot for each episode ? ? 
# - return False to stop loop when "conditions met"/DONE
# - - conditions include, 
# - - -max values on quads/DONE, transmission < XXX%/DONE, reward high/DONE
# - if max quads outside range set = 2000 (will still trigger 'done=True' too)
# - document / fix all output array value types (array, np, df, etc.)

#%%
import pandas as pd
import gym
import gym_optsb
from datetime import datetime
import random
import math
from dotenv import load_dotenv, main
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import tqdm
import numpy as np
from collections import namedtuple
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from run_track import RunTRACK
from nn_policy import MultiLayerPolicy
device = torch.device('cpu')


#%% gym setup
env = gym.make("optsb-v0")
#env = gym.make("MountainCar-v0")
obs_space = env.observation_space
action_space = env.action_space
print("The observation space: {}".format(obs_space.shape[0]))
print("The action space: {}".format(action_space.n))
env.reset()

#%%
#params
num_episodes = 1
num_steps = 3
epsilon = 1.
hidden_dim1 = 10
hidden_dim2 = 20
#%% 
#MAIN RUN
print(random.random())
policy = MultiLayerPolicy(obs_space.shape[0],hidden_dim1,hidden_dim2,action_space.n)
for episode in range(num_episodes):
    # initialize new episode params
    state = env.reset()
    state = torch.tensor(state).to(device).float()
    done = False
    rewards_current_episode = 0

    for step in tqdm.tqdm(range(num_steps), desc=f'Run {episode}'):
        if (random.random() < epsilon):
            print("Random")
            action = env.action_space.sample()
        else:
            q_vals = policy(state) #returns a torch tenser
            print(q_vals)
            action = env.get_action_from_qvals(q_vals.detach().numpy())
        print("action (qvalues): {} ({})".format(action,q_vals.detach().numpy()))
        next_state, reward, done, info = env.step(action)
        if (done):
            print("Break Before Final Step: {}".format(step))
            break

    env.render()
#print(iterate_reward)
#%% Should collate all data into df each row is step



# %%
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.graph_objs import Scatter
# from plotly.subplots import make_subplots
# fig = go.Figure()
# fig.add_trace(go.Scatter(name='reward',x=indexing,y=iterate_reward))
# fig.update_xaxes(title='step number')
# fig.show()

# %%
