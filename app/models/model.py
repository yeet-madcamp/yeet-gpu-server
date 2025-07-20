from sqlalchemy import Column, String, Float, Integer, JSON
from app.database.base import Base

class Model(Base):
    __tablename__ = "models"

    model_id = Column(String, primary_key=True, index=True)  # model_id
    model_url = Column(String, nullable=False)  # model_url

    model_owner_id = Column(String, nullable=False)
    model_owner_name = Column(String, nullable=False)

    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)

    learning_rate = Column(Float, nullable=False)

    batch_size = Column(JSON)

    gamma = Column(Float, nullable=False)
    epsilon_start = Column(Float, nullable=False)
    epsilon_min = Column(Float, nullable=False)
    epsilon_decay = Column(Float, nullable=False)
    update_target_every = Column(Integer, nullable=False)

    @classmethod
    def from_model_config(cls, model_id: str, model_url: str, config):
        """
        ModelConfig 객체(config)와 model_id, model_url을 받아 Model 인스턴스 생성
        """
        return cls(
            model_id=model_id,
            model_url=model_url,
            model_owner_id=config.model_owner_id,
            model_owner_name=config.model_owner_name,
            model_name=config.model_name,
            model_type=config.model_type,
            learning_rate=config.learning_rate,
            batch_size=config.batch_size,  # int or list/tuple, schema에 맞게 처리
            gamma=config.gamma,
            epsilon_start=config.epsilon_start,
            epsilon_min=config.epsilon_min,
            epsilon_decay=config.epsilon_decay,
            update_target_every=config.update_target_every
        )
