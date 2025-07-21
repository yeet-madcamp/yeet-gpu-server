import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque

MAX_BITS = 20  # 환경과 동일하게 최대 비트 개수 고정


class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, action_dim)
        )

    def forward(self, x):
        return self.fc(x)


class DQNAgent:
    def __init__(
            self, action_dim, state_dim, device='cpu',
            learning_rate=1e-3, batch_size=64, gamma=0.99, epsilon_start=1.0,
            epsilon_min=0.05, epsilon_decay=0.995, update_target_every=10
    ):
        # 상태 차원: x, y + 최대 비트 개수
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = device
        self.model = DQN(self.state_dim, action_dim).to(device)
        self.target = DQN(self.state_dim, action_dim).to(device)
        self.target.load_state_dict(self.model.state_dict())
        self.memory = deque(maxlen=10000)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.batch_size = batch_size
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.update_target_every = update_target_every

    def select_action(self, state):
        if np.random.rand() < self.epsilon:
            return random.randrange(self.action_dim)
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            qvals = self.model(state)
        return qvals.argmax().item()

    def store(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_step(self):
        if len(self.memory) < self.batch_size:
            return None
        batch = random.sample(self.memory, self.batch_size)
        state, action, reward, next_state, done = map(np.array, zip(*batch))
        state = torch.FloatTensor(state).to(self.device)
        next_state = torch.FloatTensor(next_state).to(self.device)
        action = torch.LongTensor(action).to(self.device)
        reward = torch.FloatTensor(reward).to(self.device)
        done = torch.FloatTensor(done.astype(np.float32)).to(self.device)

        qvals = self.model(state).gather(1, action.unsqueeze(1)).squeeze(1)
        with torch.no_grad():
            next_qvals = self.target(next_state).max(1)[0]
            target = reward + self.gamma * next_qvals * (1 - done)
        loss = nn.MSELoss()(qvals, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def update_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)

    def update_target_network(self):
        self.target.load_state_dict(self.model.state_dict())
