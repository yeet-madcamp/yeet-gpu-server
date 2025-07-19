from pydantic import BaseModel
from typing import List, Tuple


class Position(BaseModel):
    x: int
    y: int

class MapConfig(BaseModel):
    map_name: str
    map_type: str
    map_owner_id: str
    map_owner_name: str
    map_size: Tuple[int, int]
    agent_pos: Position
    exit_pos: Position
    wall_list: List[Position]
    bit_list: List[Position]
    trap_list: List[Position]
    max_steps: int

class MapSchema(MapConfig):
    map_id: str
    map_url: str
class MapResponse(MapSchema):
    type: int

class MapListResponse(BaseModel):
    type: int
    user_id: str
    maps: List[MapSchema]
