import gym
from gym import spaces
import numpy as np

class GridPosition:
    """2D 그리드에서의 위치를 나타내는 클래스"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_list(self):
        return [self.x, self.y]

class My2DEnv(gym.Env):
    """사용자 정의 2D 강화학습 환경"""
    metadata = {'render.modes': ['human']}

    def __init__(self, grid_size=GridPosition(10, 10), walls=None, traps=None, goal=None, agent_start=GridPosition(0, 0),
                 max_steps=100):
        super().__init__()
        self.grid_size = grid_size
        self.walls = walls if walls is not None else []
        self.traps = traps if traps is not None else []
        self.goal = goal if goal is not None else [grid_size.x - 1, grid_size.y - 1]
        self.agent_start = agent_start

        self.max_steps = max_steps
        self.current_step = 0

        self.state = None

        # 상태 공간: [x, y] 위치
        self.observation_space = spaces.Box(
            low=np.array([0, 0], dtype=np.float32),
            high=np.array([grid_size.x - 1, grid_size.y - 1], dtype=np.float32),
            shape=(2,),
            dtype=np.float32
        )

        # 행동 공간: 0: 왼쪽, 1: 오른쪽, 2: 위, 3: 아래
        self.action_space = spaces.Discrete(4)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array(self.agent_start.as_list(), dtype=np.float32)
        self.current_step = 0
        return self.state.copy(), {}

    def step(self, action):
        x, y = self.state.astype(int)

        # 이동 후보 위치 계산
        if action == 0:    # 왼쪽
            nx, ny = x - 1, y
        elif action == 1:  # 오른쪽
            nx, ny = x + 1, y
        elif action == 2:  # 위
            nx, ny = x, y + 1
        elif action == 3:  # 아래
            nx, ny = x, y - 1
        else:
            raise ValueError(f"Invalid action {action}")

        # 맵 범위 및 벽 충돌 검사
        if 0 <= nx < self.grid_size.x and 0 <= ny < self.grid_size.y:
            if [nx, ny] not in self.walls:
                self.state = np.array([nx, ny], dtype=np.float32)

        self.current_step += 1

        reward = -0.1  # 기본 보상
        terminated = False

        # 목표 도달 검사
        if np.array_equal(self.state.astype(int), self.goal):
            reward = 1.0
            terminated = True

        # 함정 도달 검사
        if list(self.state.astype(int)) in self.traps:
            reward = -1.0
            terminated = True

        # 최대 스텝 도달 검사
        truncated = self.current_step >= self.max_steps
        if truncated:
            reward = -1.0 # 최대 스텝 도달 시 패널티

        return self.state.copy(), reward, terminated, truncated, {}

    def render(self, mode='human'):
        pass # 시각화는 클라이언트에서 담당

    def close(self):
        pass