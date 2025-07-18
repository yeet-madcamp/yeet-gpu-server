from pydantic import BaseModel
from typing import List, Tuple

class MapConfig(BaseModel):
    map_url: str
    map_name: str
    map_type: str
    map_owner_id: str
    map_owner_name: str
    map_size: Tuple[int, int]
    agent_pos: Tuple[int, int]
    exit_pos: Tuple[int, int]
    bit_list: List[List[int]]
    trap_list: List[List[int]]
    max_steps: int

class MapResponse(MapConfig):
    map_id: str
