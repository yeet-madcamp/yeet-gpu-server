import gym
from gym import spaces
import numpy as np
from typing import List
from IPython.display import clear_output

MAX_BITS = 3  # 최대 비트 개수

class Size:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

class GridPosition:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_list(self):
        return [self.x, self.y]

    def __eq__(self, other):
        if isinstance(other, GridPosition):
            return self.x == other.x and self.y == other.y
        if isinstance(other, (list, tuple, np.ndarray)):
            return self.x == other[0] and self.y == other[1]
        return False

    def __hash__(self):
        return hash((self.x, self.y))

class My2DEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 grid_size: Size = Size(9, 9),
                 walls: List[GridPosition] = None,
                 traps: List[GridPosition] = None,
                 bits: List[GridPosition] = None,
                 goal: GridPosition = None,
                 agent_start=GridPosition(0, 0),
                 max_steps=100):
        super().__init__()
        self.grid_size = grid_size
        self.walls = walls if walls is not None else []
        self.traps = traps if traps is not None else []
        self.bits = bits if bits is not None else []
        self.goal = goal if goal is not None else GridPosition(grid_size.width - 1, grid_size.height - 1)
        self.agent_start = agent_start

        self.max_steps = max_steps
        self.current_step = 0

        self.state = None
        self.collected_bits = set()
        self.max_bits = MAX_BITS

        # 상태 공간: [x, y] + 각 비트의 먹음 여부(최대 MAX_BITS개)
        self.observation_space = spaces.Box(
            low=np.array([0, 0] + [0]*self.max_bits, dtype=np.float32),
            high=np.array([grid_size.width - 1, grid_size.height - 1] + [1]*self.max_bits, dtype=np.float32),
            shape=(2 + self.max_bits,),
            dtype=np.float32
        )

        self.action_space = spaces.Discrete(4)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.array(self.agent_start.as_list(), dtype=np.float32)
        self.current_step = 0
        self.collected_bits = set()
        return self._get_obs(), {}

    def _get_obs(self):
        # [agent_x, agent_y, bit1_collected, ..., bitMAXBITS_collected]
        bit_flags = [0.0] * self.max_bits
        agent_pos = GridPosition(int(self.state[0]), int(self.state[1]))
        for i, bit in enumerate(self.bits):
            if i < self.max_bits:
                bit_flags[i] = 1.0 if bit in self.collected_bits or agent_pos == bit else 0.0
        # 남은 비트 자리는 0.0 패딩
        return np.array(list(self.state) + bit_flags, dtype=np.float32)

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

        reward = -0.1
        attempted_move_blocked = False

        # 맵 범위 및 벽 충돌 검사
        if 0 <= nx < self.grid_size.width and 0 <= ny < self.grid_size.height:
            if [nx, ny] not in self.walls:
                self.state = np.array([nx, ny], dtype=np.float32)
            else:
                attempted_move_blocked = True
        else:
            attempted_move_blocked = True

        if attempted_move_blocked:
            reward += -0.1

        self.current_step += 1
        terminated = False

        agent_pos = GridPosition(int(self.state[0]), int(self.state[1]))

        # 비트 먹기
        for i, bit in enumerate(self.bits):
            if i < self.max_bits and agent_pos == bit and bit not in self.collected_bits:
                self.collected_bits.add(bit)
                reward += 0.5  # 비트 먹으면 추가 리워드

        # 출구 오픈 조건: 모든 비트가 먹혀야 함
        exit_open = len(self.collected_bits) == len(self.bits)

        # 목표 도달: 출구 오픈 상태에서만 성공 처리
        if agent_pos == self.goal:
            if exit_open:
                reward = 1.0
                terminated = True
            else:
                reward = -0.3  # 출구 닫혀있을 때 도달하면 패널티

        if [int(self.state[0]), int(self.state[1])] in self.traps:
            reward = -5.0
            terminated = True

        truncated = self.current_step >= self.max_steps
        if truncated:
            reward = -1.0

        return self._get_obs(), reward, terminated, truncated, {}

    def render(self, mode='human'):
        grid = [['⬜' for _ in range(self.grid_size.width)] for _ in range(self.grid_size.height)]

        for wall in self.walls:
            grid[wall.y][wall.x] = '⬛'

        for trap in self.traps:
            grid[trap.y][trap.x] = '💀'

        # 비트
        for i, bit in enumerate(self.bits):
            if i < self.max_bits:
                if bit in self.collected_bits:
                    grid[bit.y][bit.x] = '✨'  # 먹힌 비트
                else:
                    grid[bit.y][bit.x] = '🔸'  # 남은 비트

        # 목표
        grid[self.goal.y][self.goal.x] = '🏁'

        x, y = self.state.astype(int)
        grid[y][x] = '🤖'

        clear_output(wait=True)
        for row in reversed(grid):
            print(' '.join(row))
        print(f"Step: {self.current_step} / {self.max_steps}")

    def close(self):
        pass