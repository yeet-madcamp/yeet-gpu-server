from sqlalchemy import Column, String, Float, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, index=True)  # model_id
    url = Column(String, nullable=False)  # model_url

    model_owner_id = Column(String, nullable=False)
    model_owner_name = Column(String, nullable=False)

    model_name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)

    learning_rate = Column(Float, nullable=False)

    batch_size = Column(JSON)

    n_steps = Column(Integer, nullable=False)
    n_epochs = Column(Integer, nullable=False)
