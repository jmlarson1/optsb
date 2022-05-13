import gym
from gym import envs
import numpy as np
import pandas as pd
import gym
import gym_anytrading.envs
import gym_anytrading.datasets
import quantstats as qs
import matplotlib.pyplot as plt
import datetime
import pandas_datareader.data as web
from pandas import Series, DataFrame
import plotly.express as px
import plotly.graph_objects as go
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as distributions
import tqdm
import collections
import random

class MultiLayerPolicy(nn.Module):
    def __init__(self, input_dim, hidden_dim, hidden_dim2, output_dim):
        super().__init__()

        self.fc_1 = nn.Linear(input_dim, hidden_dim)
        self.fc_2 = nn.Linear(hidden_dim, hidden_dim2)
        self.fc_3 = nn.Linear(hidden_dim2, output_dim)

    def forward(self, x):
        x = self.fc_1(x)
        x = F.relu(x)
        x = self.fc_2(x)
        x = F.relu(x)
        x = self.fc_3(x)
        return x
