import numpy as np


class GridPosition:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def as_tuple(self):
        return (self.x, self.y)

    def as_list(self):
        return [self.x, self.y]

    def as_array(self, dtype=np.float32):
        return np.array([self.x, self.y], dtype=dtype)

    def __eq__(self, other):
        if isinstance(other, GridPosition):
            return self.x == other.x and self.y == other.y
        if isinstance(other, (list, tuple, np.ndarray)):
            return (self.x, self.y) == tuple(other)
        return False

    def __repr__(self):
        return f"GridPosition(x={self.x}, y={self.y})"

    def copy(self):
        return GridPosition(self.x, self.y)
