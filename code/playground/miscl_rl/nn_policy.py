import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributions as distributions
device = torch.device('cpu')
import numpy as np
import gym

class MultiLayerPolicy(nn.Module):
    def __init__(self, input_dim, hidden_dim, hidden_dim2, output_dim):
        super().__init__()

        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim2)
        self.fc3 = nn.Linear(hidden_dim2, output_dim)

    def forward(self, x):
        x = torch.tensor(x).to(device).float()
        x = torch.tanh(self.fc1(x))
        x = torch.tanh(self.fc2(x))
        x = self.fc3(x)
        # x = self.fc_1(x)
        # x = F.relu(x)
        # x = self.fc_2(x)
        # x = F.relu(x)
        # x = self.fc_3(x)
        return x

# ALGO LOGIC: initialize agent here:
class QNetwork(nn.Module):
    def __init__(self, env):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(np.array(env.observation_space.shape).prod(), 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, env.action_space.n)

    def forward(self, x, device):
        x = torch.Tensor(x).to(device)
        x = torch.tanh(self.fc1(x))
        x = torch.tanh(self.fc2(x))
        x = self.fc3(x)
        return x

