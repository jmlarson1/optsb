#%% to do
# - more plots via env render
# -- each step, rewards/DONE, actions/DONE, states ? ? 
# ---- new plot for each episode ? ? 
# - return False to stop loop when "conditions met"/DONE
# - - conditions include, 
# - - -max values on quads/DONE, transmission < XXX%/DONE, reward high/DONE
# - if max quads outside range set = 2000 (will still trigger 'done=True' too)
# -- instead force to 2000 and give bad reward?
# - document / fix all output array value types (array, np, df, etc.)
# RL Q_Learning
# - try to get the simple q-learning going again
# - need to track <types> List, np, torch.tensor
# - then move to per-naf / ddpg

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
import collections
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influx_client import InfluxClient
from run_track import RunTRACK
from nn_policy import MultiLayerPolicy
from sklearn import preprocessing
min_max_scaler = preprocessing.MinMaxScaler()
def NormData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))
device = torch.device('cpu')


#%% gym setup
#env = gym.make("optsb-v0")
#env = gym.make("MountainCar-v0")
env = gym.make("CartPole-v1")
env.seed(1234)
obs_space = env.observation_space
action_space = env.action_space
print("The observation space: {}".format(obs_space.shape[0]))
print("The action space: {}".format(action_space.n))
env.reset()

# modified from https://github.com/seungeunrho/minimalRL/blob/master/dqn.py#
class ReplayBuffer():
    def __init__(self, buffer_limit):
        self.buffer = collections.deque(maxlen=buffer_limit)
    
    def put(self, transition):
        self.buffer.append(transition)
    
    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []
        
        for transition in mini_batch:
            s, a, r, s_prime, done_mask = transition
            s_lst.append(s)
            a_lst.append(a)
            r_lst.append(r)
            s_prime_lst.append(s_prime)
            done_mask_lst.append(done_mask)

        return np.array(s_lst), np.array(a_lst), \
               np.array(r_lst), np.array(s_prime_lst), \
               np.array(done_mask_lst)

def linear_schedule(start_e: float, end_e: float, duration: int, t: int):
    slope =  (end_e - start_e) / duration
    return max(slope * t + start_e, end_e)

#%%
#params
num_episodes = 4_000
num_steps = 10_000
epsilon = 1.0
hidden_dim1 = 20
hidden_dim2 = 30
buffer_size = 5_000
train_freq = 10
batch_size = 100
update_freq = 200
gamma = 0.99

#%% 
#MAIN RUN
loss_iterate = []
reward_iterate = []
reward_total = 0.

policy = MultiLayerPolicy(obs_space.shape[0],hidden_dim1,hidden_dim2,action_space.n)
target = MultiLayerPolicy(obs_space.shape[0],hidden_dim1,hidden_dim2,action_space.n)
target.load_state_dict(policy.state_dict())
rbuff = ReplayBuffer(buffer_size)
optimizer = optim.Adam(policy.parameters())
loss_fn = nn.MSELoss()
counter = 0
for episode in range(num_episodes):
    state = env.reset() #state should be np
    #state = torch.tensor(state).to(device).float()
    done = False
    reward_total = 0
    for step in range(num_steps):
        counter+=1
        epsilon = linear_schedule(1.0,0.05,num_episodes,episode)
        if (random.random() < epsilon):
            action = env.action_space.sample()
        else:
            q_vals = policy(state) #returns a torch tenser
            action = np.argmax(q_vals.detach().numpy())
                #env.get_action_from_qvals(q_vals.detach().numpy())
        #print("action (qvalues): {}".format(action))
        next_state, reward, done, info = env.step(action)
        reward_total+=reward
        # save to memory/replay buffer rbuff
        rbuff.put((state,action,reward,next_state,done))
        # if buffer filled & certain iteration, get sample, calc Q, losses, update policy
        if counter > batch_size and counter%train_freq==0:
            s_states, s_actions, s_rewards, s_next_states, s_dones = rbuff.sample(batch_size)
            #print("*****Inside training:*****")
            with torch.no_grad():
                target_max = torch.max(target.forward(s_next_states), dim=1)[0]
                td_target = torch.Tensor(s_rewards).to(device) + gamma * target_max * (1 - torch.Tensor(s_dones).to(device))
            old_val = policy.forward(s_states).gather(1, torch.LongTensor(s_actions).view(-1,1).to(device)).squeeze()
            loss = loss_fn(td_target, old_val)
            # optimize the midel
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(list(policy.parameters()), 1.)
            optimizer.step()
            loss_iterate.append(loss.item())
        # update the target network
        if counter % update_freq == 0:
            #print("=!=!=update target network=!=!=")
            target.load_state_dict(policy.state_dict())
        #always move the state
        state = next_state

        if (done):
            print("BREAK epi {} Total Reward: {} at {} step [sumstep {}] (epsilon {})".format(episode,reward_total,step,counter,epsilon))
            reward_iterate.append(reward_total)
            break
    #env.render()
    #print("===LOSS===: {}".format(loss_iterate))

#print(iterate_reward)
#%% Should collate all data into df each row is step



# %%
indexing = []
reward_indexing = []
for i in range(len(loss_iterate)):
    indexing.append(i)
for i in range(len(reward_iterate)):
    reward_indexing.append(i)
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
fig = go.Figure()
fig.add_trace(go.Scatter(name='reward',x=reward_indexing,y=reward_iterate))
fig.add_trace(go.Scatter(name='reward',x=indexing,y=loss_iterate))
fig.update_xaxes(title='step number')
fig.show()

# %%
