from dataclasses import dataclass, asdict
from typing import Tuple
import json

@dataclass
class Model:
    model_id: str
    model_url: str
    model_owner_id: str
    model_owner_name: str
    model_name: str
    model_type: str
    learning_rate: float
    batch_size: Tuple[int, int]
    n_steps: int
    n_epochs: int

    @classmethod
    def from_json(cls, json_str: str) -> "Model":
        data = json.loads(json_str)
        # 튜플로 변환
        data["batch_size"] = tuple(data["batch_size"])
        return cls(**data)

    def to_json(self) -> str:
        dict_data = asdict(self)
        dict_data["batch_size"] = list(self.batch_size)
        return json.dumps(dict_data, ensure_ascii=False, indent=2)
