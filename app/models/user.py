from sqlalchemy import Column, String
from app.database.base import Base  # SQLAlchemy declarative base

class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
