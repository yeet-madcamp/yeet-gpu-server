import gym
from gym import spaces
import numpy as np
from typing import List
from IPython.display import clear_output

class Size:
    """2D 그리드의 크기를 나타내는 클래스"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

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

    def __init__(self, grid_size: Size = Size(9, 9), walls: List[GridPosition] = None, traps: List[GridPosition] = None, goal: GridPosition = None, agent_start=GridPosition(0, 0),
                 max_steps=100):
        super().__init__()
        self.grid_size = grid_size
        self.walls = walls if walls is not None else []
        self.traps = traps if traps is not None else []
        self.goal = goal if goal is not None else GridPosition(grid_size.width - 1, grid_size.height - 1)
        self.agent_start = agent_start

        self.max_steps = max_steps
        self.current_step = 0

        self.state = None

        # 상태 공간: [x, y] 위치
        self.observation_space = spaces.Box(
            low=np.array([0, 0], dtype=np.float32),
            high=np.array([grid_size.width - 1, grid_size.height - 1], dtype=np.float32),
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

        # 기본 보상
        reward = -0.1
        attempted_move_blocked = False

        # 맵 범위 및 벽 충돌 검사
        if 0 <= nx < self.grid_size.width and 0 <= ny < self.grid_size.height:
            if [nx, ny] not in self.walls:
                self.state = np.array([nx, ny], dtype=np.float32)
            else:
                attempted_move_blocked = True  # 벽에 막힘
        else:
            attempted_move_blocked = True  # 맵 밖으로 나감

        # 벽에 부딪힌 경우 추가 패널티
        if attempted_move_blocked:
            reward += -0.2  # 총 -0.3이 됨

        self.current_step += 1
        terminated = False

        # 목표 도달 검사
        if np.array_equal(self.state.astype(int), np.array(self.goal.as_list())):
            reward = 1.0
            terminated = True

        # 함정 도달 검사
        if list(self.state.astype(int)) in self.traps:
            reward = -1.0
            terminated = True

        # 최대 스텝 도달 검사
        truncated = self.current_step >= self.max_steps
        if truncated:
            reward = -1.0

        return self.state.copy(), reward, terminated, truncated, {}

    def render(self, mode='human'):
        grid = [['⬜' for _ in range(self.grid_size.width)] for _ in range(self.grid_size.height)]

        # 벽
        for wall in self.walls:
            grid[wall.y][wall.x] = '⬛'

        # 트랩
        for trap in self.traps:
            grid[trap.y][trap.x] = '💀'

        # 목표
        if isinstance(self.goal, GridPosition):
            grid[self.goal.y][self.goal.x] = '🏁'

        # 에이전트
        x, y = self.state.astype(int)
        grid[y][x] = '🤖'

        # 터미널 시각화
        clear_output(wait=True)
        for row in reversed(grid):  # (0,0) 위치를 좌하단으로
            print(' '.join(row))
        print(f"Step: {self.current_step} / {self.max_steps}")

    def close(self):
        pass