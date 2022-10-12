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
from nn_policy import MultiLayerPolicy
from sklearn import preprocessing
import gym_hybrid
import gym_optsb
import pytest
from stable_baselines3.common.env_checker import check_env

env = gym.make("optsb-v0")

checkit = False
if (checkit) :
  with pytest.warns(Warning):
    check_env(env=env, warn=True)

# from stable_baselines3 import PPO

# env = gym.make("optsb-v0")

# model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=10_000)

obs = env.reset()
for i in range(20):
  obs, reward, done, info = env.step(env.action_space.sample())
  print("obs: {}, reward: {}, done: {}".format(obs, reward, done))
  env.render()
#     action, _states = model.predict(obs, deterministic=True)
#     
#     env.render()
#     if done:
#       obs = env.reset()

# env.close()