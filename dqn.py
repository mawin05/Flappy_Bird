import torch.nn as nn
import torch.nn.functional as F


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=256):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)
