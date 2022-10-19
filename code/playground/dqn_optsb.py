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
import plotly.offline as pyo
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import plotly.io as pio
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
env = gym.make("optsb-v0")
#env = gym.make("MountainCar-v0")
#env = gym.make("CartPole-v1")
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

# %%
#pio.renderers.default = "png"
def plotter():
#rewards
    fig_reward = make_subplots(rows=2,cols=1,shared_xaxes=True,vertical_spacing=0.02) #go.Figure()
    fig_reward.add_trace(go.Scatter(name='reward',x=episode_indexing,y=reward_iterate,mode='lines'),row=1,col=1)
    fig_reward.add_trace(go.Scatter(name='good rewards',x=episode_good_indexing,y=reward_good_iterate,mode='markers'),row=1,col=1)
    fig_reward.add_trace(go.Scatter(name='reward total',x=episode_indexing,y=reward_total_iterate,mode='lines'),row=2,col=1)
    fig_reward.add_trace(go.Scatter(name='good total rewards',x=episode_good_indexing,y=reward_good_total_iterate,mode='markers'),row=2,col=1)
    fig_reward.update_xaxes(title='episode number')
    fig_reward.write_image("reward.png", width=1200, height=800)

#steps
    fig_step = go.Figure()
    fig_step.add_trace(go.Scatter(name='steps',x=episode_indexing,y=steps_iterate,mode='lines'))
    fig_step.add_trace(go.Scatter(name='steps',x=episode_good_indexing,y=steps_good_iterate,mode='markers'))
    fig_step.update_xaxes(title='steps during episode')
    fig_step.write_image("step.png",width=1200,height=600)

#state
    fig_q = make_subplots(2,3,shared_xaxes=True,vertical_spacing=0.02)
    fig_q.add_trace(go.Scatter(name='quad1',x=episode_indexing,y=quadvals1_iterate,mode='lines'),row=1,col=1)
    fig_q.add_trace(go.Scatter(name='good quad1',x=episode_good_indexing,y=quadvals1_good_iterate,mode='markers'),row=2,col=1)
    fig_q.update_yaxes(range=[0,2000],row=1,col=1)
    fig_q.update_yaxes(range=[0,2000],row=2,col=1)
    fig_q.add_trace(go.Scatter(name='quad2',x=episode_indexing,y=quadvals2_iterate,mode='lines'),row=1,col=2)
    fig_q.add_trace(go.Scatter(name='good quad2',x=episode_good_indexing,y=quadvals2_good_iterate,mode='markers'),row=2,col=2)
    fig_q.update_yaxes(range=[-2000,0],row=1,col=2)
    fig_q.update_yaxes(range=[-2000,0],row=2,col=2)
    fig_q.add_trace(go.Scatter(name='quad3',x=episode_indexing,y=quadvals3_iterate,mode='lines'),row=1,col=3)
    fig_q.add_trace(go.Scatter(name='good quad3',x=episode_good_indexing,y=quadvals3_good_iterate,mode='markers'),row=2,col=3)
    fig_q.update_yaxes(range=[0,2000],row=1,col=3)  
    fig_q.update_yaxes(range=[0,2000],row=2,col=3)
    fig_q.update_xaxes(title='episode number')
    fig_q.write_image("quads.png", width=1200, height=800)

#loss
    fig_loss = go.Figure()
    fig_loss.add_trace(go.Scatter(name='loss',x=train_indexing,y=loss_iterate))
    fig_loss.update_xaxes(title='training number')
    fig_loss.write_image("loss_tot.png",width=1200,height=600)


#%%
#params
num_episodes = 1_000
num_steps = 10_000
epsilon = 0.5
hidden_dim1 = 64
hidden_dim2 = 64
buffer_size = 1_000
train_freq = 10
batch_size = 64
update_freq = 100
gamma = 0.99

#%% 
#MAIN RUN
episode_indexing = []
step_indexing = []
train_indexing = []
loss_iterate = []
reward_iterate = []
reward_total_iterate = []
quadvals1_iterate = []
quadvals2_iterate = []
quadvals3_iterate = []
steps_iterate = []
#goods
episode_good_indexing = []
step_good_indexing = []
#train_good_indexing = []
#loss_good_iterate = []
reward_good_iterate = []
reward_good_total_iterate = []
quadvals1_good_iterate = []
quadvals2_good_iterate = []
quadvals3_good_iterate = []
steps_good_iterate = []
#sums
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
        epsilon = linear_schedule(0.8,0.05,num_episodes,episode)
        if (random.random() < epsilon):
            action = env.action_space.sample()
        else:
            q_vals = policy(state) #returns a torch tenser
            action = np.argmax(q_vals.detach().numpy())
                #env.get_action_from_qvals(q_vals.detach().numpy())
        #print("action (qvalues): {}".format(action))
        next_state, reward, done, info = env.step(action)
        reward_total+=reward
        quadvals1 = next_state[0]
        quadvals2 = next_state[1]
        quadvals3 = next_state[2]
        #reward_iterate.append(reward)
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
            # optimize the m0del
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(list(policy.parameters()), 1.)
            optimizer.step()
            loss_iterate.append(loss.item())
            train_indexing.append(counter)

            #loss_good_iterate.append(

        # update the target network
        if counter % update_freq == 0:
            #print("=!=!=update target network=!=!=")
            target.load_state_dict(policy.state_dict())
        #always move the state
        state = next_state

        if (done):
            print("BREAK epi {} Total Reward: {} at {} step [sumstep {}] (epsilon {})".format(episode,reward_total,step,counter,epsilon))
            print("Quadvals {} {} {} Reward {})".format(quadvals1,quadvals2,quadvals3,reward))
            episode_indexing.append(episode)
            reward_total_iterate.append(reward_total)
            reward_iterate.append(reward)
            quadvals1_iterate.append(quadvals1)
            quadvals2_iterate.append(quadvals2)
            quadvals3_iterate.append(quadvals3)
            steps_iterate.append(step)
            if (reward > env.get_optimal_reward_value()):
                episode_good_indexing.append(episode)
                reward_good_iterate.append(reward)
                reward_good_total_iterate.append(reward_total)
                quadvals1_good_iterate.append(quadvals1)
                quadvals2_good_iterate.append(quadvals2)
                quadvals3_good_iterate.append(quadvals3)
                steps_good_iterate.append(step)
            plotter()
            break
    #env.render()
    #print("===LOSS===: {}".format(loss_iterate))

#print(iterate_reward)
#%% Should collate all data into df each row is step
# %%
# %%
