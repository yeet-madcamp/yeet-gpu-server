import gym
from gym import spaces
import numpy as np

from grid_position import GridPosition


class My2DEnv(gym.Env):
    def __init__(self, grid_size=GridPosition(10, 10), walls=None, traps=None, goal=None, agent=GridPosition(0, 0),
                 max_steps=100):
        super().__init__()
        self.grid_size = grid_size
        self.walls = walls if walls is not None else []
        self.traps = traps if traps is not None else []
        self.goal = goal if goal is not None else [grid_size.x - 1, grid_size.y - 1]
        self.agent_start = agent

        self.max_steps = max_steps
        self.current_step = 0  # 현재 스텝 수 초기화

        self.state = None

        # 상태 공간: [x, y] 위치
        self.observation_space = spaces.Box(low=np.array([0, 0], dtype=np.float32),
                                            high=np.array([grid_size.x - 1, grid_size.y - 1], dtype=np.float32),
                                            shape=(2,),
                                            dtype=np.float32)

        # 0: 왼쪽, 1: 오른쪽, 2: 위, 3: 아래
        self.action_space = spaces.Discrete(4)

    def reset(self, seed=None, options=None):
        self.state = np.array(self.agent_start.as_list(), dtype=np.float32)
        self.current_step = 0

        return self.state.copy(), {}

    def step(self, action):
        x, y = self.state.astype(int)

        # 이동 후보
        if action == 0:
            nx, ny = x - 1, y
        elif action == 1:
            nx, ny = x + 1, y
        elif action == 2:
            nx, ny = x, y + 1
        else:
            nx, ny = x, y - 1

        # 맵 범위 및 벽 충돌 검사
        if 0 <= nx < self.grid_size.x and 0 <= ny < self.grid_size.y:
            if [nx, ny] not in self.walls:
                self.state = np.array([nx, ny], dtype=np.float32)

        self.current_step += 1

        reward = -0.1
        done = False

        # 골 도달
        if np.array_equal(self.state.astype(int), self.goal):
            reward = 1.0
            done = True

        # 함정 도달
        if list(self.state.astype(int)) in self.traps:
            reward = -1.0
            done = True

        if self.current_step >= self.max_steps:
            reward = -1.0
            done = True

        return self.state.copy(), reward, done, False, {}
