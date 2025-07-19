from pydantic import BaseModel
class Position(BaseModel):
    x: int
    y: int
class ModelConfig(BaseModel):
    model_owner_id: str
    model_owner_name: str
    model_name: str
    model_type: str
    learning_rate: float
    batch_size: Position
    n_steps: int
    n_epochs: int

class ModelSchema(ModelConfig):
    model_id: str
    model_url: str
class ModelResponse(ModelSchema):
    type: int
    model_id: str
    model_url: str

class ModelListResponse(BaseModel):
    type: int
    models: list[ModelSchema]
