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

def extract_tensors(experiences):
    # Convert batch of Experiences to Experience of batches
    batch = Experience(*zip(*experiences))

    t1 = torch.stack(batch.state)
    t2 = torch.stack(batch.action)
    t3 = torch.stack(batch.reward)
    t4 = torch.stack(batch.next_state)

    return (t1,t2,t3,t4)

class QValues():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def get_current(policy, states, actions):
        return policy(states)#.gather(dim=1, index=actions.unsqueeze(-1))

    @staticmethod        
    def get_next(target_net, next_states):   
        return target_net(next_states)             
        # final_state_locations = next_states.flatten(start_dim=1) \
        #     .max(dim=1)[0].eq(0).type(torch.bool)
        # non_final_state_locations = (final_state_locations == False)
        # non_final_states = next_states[non_final_state_locations]
        # batch_size = next_states.shape[0]
        # values = torch.zeros(batch_size).to(QValues.device)
        # values[non_final_state_locations] = target_net(non_final_states) #.max(dim=1)[0].detach()
        # return values
#%%
#params
num_episodes = 1
num_steps = 10
batch_size = 2
target_update = 2
memory_size = 5
gamma = 0.999
eps_start = 1
eps_end = 0.01
eps_decay = 0.001
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
running_losses = []
running_rewards = []
indexing = []
for episode in range(num_episodes):
    # initialize new episode params
    state = env.reset()
    state = torch.tensor(state.to_numpy()).to(device).float()
    done = False
    rewards_current_episode = 0
    policy.train()

    for step in tqdm.tqdm(range(num_steps), desc=f'Run {episode}'):
        if np.random.random() < 0.5: #update later
            action = env.querry_action()
        else:
            qvalues = policy(state)
            qvalues = qvalues[0,:].detach().numpy()
            print("qvalues: {}:".format(qvalues))
            action = env.get_action(qvalues)
        print("action: {}".format(action))
        next_state, reward, done, info = env.step(action)
        next_state = torch.tensor(next_state.to_numpy()).to(device).float()
        reward_all_episodes.append(reward)
        #action = torch.from_numpy(action).to(device).float()
        action = torch.tensor([action],dtype=torch.float).to(device).float()
        reward = torch.tensor([reward],dtype=torch.float).to(device).float()
        running_rewards.append(reward.item())
        memory.push(Experience(state, action, next_state, reward))
        state = next_state #torch.tensor(next_state.to_numpy()).to(device).float()
        #loss = 1.#update_policy(policy, state, action, reward, next_state, discount_factor, optimizer)
        if memory.can_provide_sample(batch_size):
            experiences = memory.sample(batch_size)
            states, actions, rewards, next_states = extract_tensors(experiences)
            current_q_values = QValues.get_current(policy, states, actions)
            next_q_values = QValues.get_next(target, next_states)
            # get max value & index from next
            # combine to get value (next_q_values * gamma) + rewards
            # replace current with target (only for the max index)
            #max_q_values = 0 #match current_q_values form
            #target_q_values = (next_q_values * gamma) + rewards
            #loss = F.mse_loss(current_q_values, target_q_values.unsqueeze(1))
            test = current_q_values.detach().numpy() #np.array(current_q_values)
            test2 = next_q_values.detach().numpy() #np.array(next_q_values)
            #test[test2.argmax()] = (test2[test2.argmax()] + rewards)
            print("test2: {}".format(test2))
            print(np.argmax(test2,axis=1))
            print(test2[test2.argmax()])
            target_q_values = list(test)
            loss = F.mse_loss(current_q_values, target_q_values)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_losses.append(loss.item())
        indexing.append(episode*step+step+1)
        if step % target_update == 0:
            target.load_state_dict(policy.state_dict())
print(running_rewards)
print(running_losses)
# %%
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots

fig = go.Figure()
fig.add_trace(go.Scatter(name='reward',x=indexing,y=running_rewards))
fig.add_trace(go.Scatter(name='loss',x=indexing,y=running_losses))
fig.update_xaxes(title='step number')
fig.show()

# %%
