from dataclasses import dataclass, asdict
from typing import Tuple, List
import json


@dataclass
class Map:
    map_id: str
    map_url: str
    map_size: Tuple[int, int]
    agent_pos: Tuple[int, int]
    exit_pos: Tuple[int, int]
    bit_list: List[Tuple[int, int]]
    trap_list: List[Tuple[int, int]]
    map_owner_id: str
    map_owner_name: str
    map_name: str
    map_type: str
    max_steps: int

    @classmethod
    def from_json(cls, json_str: str) -> "Map":
        data = json.loads(json_str)
        # 튜플로 변환할 항목 처리
        data["map_size"] = tuple(data["map_size"])
        data["agent_pos"] = tuple(data["agent_pos"])
        data["exit_pos"] = tuple(data["exit_pos"])
        data["bit_list"] = [tuple(pos) for pos in data["bit_list"]]
        data["trap_list"] = [tuple(pos) for pos in data["trap_list"]]
        return cls(**data)

    def to_json(self) -> str:
        # 튜플은 JSON 직렬화가 안 되므로 리스트로 변환
        dict_data = asdict(self)
        dict_data["map_size"] = list(self.map_size)
        dict_data["agent_pos"] = list(self.agent_pos)
        dict_data["exit_pos"] = list(self.exit_pos)
        dict_data["bit_list"] = [list(pos) for pos in self.bit_list]
        dict_data["trap_list"] = [list(pos) for pos in self.trap_list]
        return json.dumps(dict_data, ensure_ascii=False, indent=2)
