#%%
## lets go incorp q-learning ?? why not...
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
temp = env.reset()

# print(temp)
# net = MultiLayerPolicy(3,10,10,3).to(device)
# X = torch.tensor(temp.to_numpy()).to(device).float()
# print(X.float())
# temp2 = net(X)
# temp3 = temp2[0,:].detach().numpy()
# print(temp3)
# _, _, _, _ = env.step(temp3)

# policy setup
input_dim = env.observation_space
hidden_dim = 32
hidden_dim2 = 24
output_dim = env.action_space
print("in {}, out {}".format(input_dim, output_dim))

#%%
#memory / replay
Experience = namedtuple(
    'Experience',
    ('state', 'action', 'next_state', 'reward')
)

class ReplayMemory():
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.push_count = 0
    def push(self, experience): #save, overwrite older if too many
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.push_count % self.capacity] = experience
        self.push_count += 1
    def sample(self, batch_size): #return sampe of batch_size
        return random.sample(self.memory, batch_size)
    def can_provide_sample(self, batch_size): #bool T/F
        return len(self.memory) >= batch_size

class EpsilonGreedyStrategy():
    def __init__(self, start, end, decay):
        self.start = start
        self.end = end
        self.decay = decay
    def get_exploration_rate(self, current_step):
        return self.end + (self.start - self.end) * \
            math.exp(-1. * current_step * self.decay)

class Agent():
    def __init__(self, strategy, num_actions, device):
        self.current_step = 0
        self.strategy = strategy
        self.num_actions = num_actions
        self.device = device
    def select_action(self, state, policy_net):
        rate = self.strategy.get_exploration_rate(self.current_step)
        self.current_step += 1
        if rate > random.random():
            action = random.randrange(self.num_actions)
            return torch.tensor([action]).to(self.device) # explore      
        else:
            with torch.no_grad():
                return policy_net(state).argmax(dim=1).to(self.device) # exploit

#%%
#params

num_episodes = 1
num_steps = 10

batch_size = 5
gamma = 0.999
eps_start = 1
eps_end = 0.01
eps_decay = 0.001
target_update = 10
memory_size = 100
lr = 0.001

train_rewards = torch.zeros(num_steps, num_episodes)
test_rewards = torch.zeros(num_steps, num_episodes)
train_loss = torch.zeros(num_steps, num_episodes)
train_info = [dict() for i in range(num_steps*num_episodes)]
test_info = [dict() for i in range(num_steps*num_episodes)]
device = torch.device('cpu')


#%% 
#MAIN RUN
reward_all_episodes = []
policy = MultiLayerPolicy(input_dim, hidden_dim, hidden_dim2, output_dim)
policy.to(device)
target = MultiLayerPolicy(input_dim, hidden_dim, hidden_dim2, output_dim)
target.to(device)
target.load_state_dict(policy.state_dict())
target.eval()
# policy.apply(init_weights)
memory = ReplayMemory(memory_size)
optimizer = optim.Adam(policy.parameters(), lr=lr, betas=(0.9, 0.999))

#%%
for episode in range(num_episodes):
    # initialize new episode params
    state = env.reset()
    state = torch.tensor(state.to_numpy()).to(device).float()
    done = False
    rewards_current_episode = 0
    policy.train()

    for step in tqdm.tqdm(range(num_steps), desc=f'Run {episode}'):
        if np.random.random() < 0.0: #update later
            action = env.querry_action()
        else:
            action = policy(state)
            action = action[0,:].detach().numpy()
        print(action)
        next_state, reward, done, info = env.step(action)
        next_state = torch.tensor(next_state.to_numpy()).to(device).float()
        print(info)
        reward_all_episodes.append(reward)
        memory.push(Experience(state, action, next_state, reward))
        state = next_state #torch.tensor(next_state.to_numpy()).to(device).float()
        #loss = 1.#update_policy(policy, state, action, reward, next_state, discount_factor, optimizer)
        if memory.can_provide_sample(batch_size):
            experiences = memory.sample(batch_size)
            print(experiences)
            # states, actions, rewards, next_states = extract_tensors(experiences)
            # current_q_values = QValues.get_current(policy_net, states, actions)
            # next_q_values = QValues.get_next(target_net, next_states)
            # target_q_values = (next_q_values * gamma) + rewards
            # loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
            # optimizer.zero_grad()
            # loss.backward()
            # optimizer.step()
# %%
