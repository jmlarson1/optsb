#%% to do
# - more plots via env render
# -- each step, rewards, actions, states ? ? 
# ---- new plot for each episode ? ? 
# - return False to stop loop when "conditions met"
# - - conditions include, 
# - - -max values on quads, transmission < XXX%, reward high/DONE
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
#%%
#params
num_episodes = 1
num_steps = 25

#%% 
#MAIN RUN
iterate_reward = []
accumulative_reward = []
indexing = []
for episode in range(num_episodes):
    # initialize new episode params
    state = env.reset()
    state = torch.tensor(state.to_numpy()).to(device).float()
    done = False
    rewards_current_episode = 0

    for step in tqdm.tqdm(range(num_steps), desc=f'Run {episode}'):
        action = env.querry_action()
        print("action: {}".format(action))
        next_state, reward, done, info = env.step(action)
        iterate_reward.append(reward)
        #accumulative_reward.append(iterate_reward.sum())
        indexing.append(episode*num_steps+step)
        if (done):
            print("GOT A TRUE VALUE FOR DONE on step: {}".format(step))
            break
print(iterate_reward)
#%% Should collate all data into df each row is step

env.render()


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
