from pydantic import BaseModel
class ModelConfig(BaseModel):
    model_owner_id: str
    model_owner_name: str
    model_name: str
    model_type: str
    learning_rate: float
    batch_size: int
    gamma: float
    epsilon_start: float
    epsilon_min: float
    epsilon_decay: float
    update_target_every: int


class ModelSchema(ModelConfig):
    model_id: str
    model_url: str

    @classmethod
    def from_model(cls, model):
        """
        SQLAlchemy Model 인스턴스(model)로부터 ModelSchema 인스턴스를 생성합니다.
        """
        return cls(
            model_id=model.model_id,
            model_url=model.model_url,
            model_owner_id=model.model_owner_id,
            model_owner_name=model.model_owner_name,
            model_name=model.model_name,
            model_type=model.model_type,
            learning_rate=model.learning_rate,
            batch_size=model.batch_size,
            gamma=model.gamma,
            epsilon_start=model.epsilon_start,
            epsilon_min=model.epsilon_min,
            epsilon_decay=model.epsilon_decay,
            update_target_every=model.update_target_every,
        )
class ModelResponse(ModelSchema):
    type: int

class ModelListResponse(BaseModel):
    type: int
    models: list[ModelSchema]
