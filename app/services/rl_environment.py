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
        self.success = 0
        self.x_min = -(grid_size.width // 2)
        self.x_max = grid_size.width // 2
        self.y_min = -(grid_size.height // 2)
        self.y_max = grid_size.height // 2

        self.walls = walls if walls is not None else []
        self.traps = traps if traps is not None else []
        self.bits = bits if bits is not None else []
        self.goal = goal if goal is not None else GridPosition(self.x_max, self.y_max)
        self.agent_start = agent_start

        self.max_steps = max_steps
        self.current_step = 0

        self.state = None
        self.collected_bits = set()
        self.max_bits = MAX_BITS

        # 상태 공간: [x, y] + 각 비트의 먹음 여부(최대 MAX_BITS개)
        self.observation_space = spaces.Box(
            low=np.array([self.x_min, self.y_min] + [0]*self.max_bits, dtype=np.float32),
            high=np.array([self.x_max, self.y_max] + [1]*self.max_bits, dtype=np.float32),
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
        bit_flags = [0.0] * self.max_bits
        agent_pos = GridPosition(int(self.state[0]), int(self.state[1]))
        for i, bit in enumerate(self.bits):
            if i < self.max_bits:
                bit_flags[i] = 1.0 if bit in self.collected_bits or agent_pos == bit else 0.0
        return np.array(list(self.state) + bit_flags, dtype=np.float32)

    def in_grid(self, x, y):
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max

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

        reward = -0.05
        attempted_move_blocked = False

        # 맵 범위 및 벽 충돌 검사
        if self.in_grid(nx, ny):
            if GridPosition(nx, ny) not in self.walls:
                self.state = np.array([nx, ny], dtype=np.float32)
            else:
                attempted_move_blocked = True
        else:
            attempted_move_blocked = True

        if attempted_move_blocked:
            reward += -0.15

        self.current_step += 1
        terminated = False

        agent_pos = GridPosition(int(self.state[0]), int(self.state[1]))

        # 비트 먹기
        for i, bit in enumerate(self.bits):
            if i < self.max_bits and agent_pos == bit and bit not in self.collected_bits:
                self.collected_bits.add(bit)
                reward += 2.0
                reward += (self.max_bits - len(self.collected_bits)) * 0.3

        exit_open = len(self.collected_bits) == len(self.bits)

        if agent_pos == self.goal:
            if exit_open:
                reward += 10.0
                reward += max(0.0, (self.max_steps - self.current_step) * 0.1)
                terminated = True
                self.success += 1
            else:
                reward += -1.0

        if agent_pos in self.traps:
            reward += -5.0
            terminated = True

        truncated = self.current_step >= self.max_steps
        if truncated:
            reward += -2.0

        return self._get_obs(), reward, terminated, truncated, {}

    def pos_to_idx(self, pos: GridPosition):
        xi = pos.x - self.x_min
        yi = pos.y - self.y_min
        if not (0 <= xi < self.grid_size.width and 0 <= yi < self.grid_size.height):
            return None, None
        return xi, yi

    def render(self, mode='human'):
        grid = [['⬜' for _ in range(self.grid_size.width)] for _ in range(self.grid_size.height)]

        for wall in self.walls:
            xi, yi = self.pos_to_idx(wall)
            if xi is not None and yi is not None:
                grid[yi][xi] = '⬛'

        for trap in self.traps:
            xi, yi = self.pos_to_idx(trap)
            if xi is not None and yi is not None:
                grid[yi][xi] = '💀'

        for i, bit in enumerate(self.bits):
            if i < self.max_bits:
                xi, yi = self.pos_to_idx(bit)
                if xi is not None and yi is not None:
                    if bit in self.collected_bits:
                        grid[yi][xi] = '✨'
                    else:
                        grid[yi][xi] = '🔸'

        xi, yi = self.pos_to_idx(self.goal)
        if xi is not None and yi is not None:
            grid[yi][xi] = '🏁'

        x, y = self.state.astype(int)
        xi, yi = self.pos_to_idx(GridPosition(x, y))
        if xi is not None and yi is not None:
            grid[yi][xi] = '🤖'

        clear_output(wait=True)
        for row in grid[::-1]:
            print(' '.join(row), flush=True)
        print(f"Step: {self.current_step} / {self.max_steps} | Success: {self.success} | Collected Bits: {len(self.collected_bits)} / {self.max_bits}", flush=True)

    def close(self):
        pass