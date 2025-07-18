from sqlalchemy import Column, Integer, String, JSON
from app.database.base import Base

class MapModel(Base):
    __tablename__ = "maps"

    id = Column(String, primary_key=True, index=True)
    map_url = Column(String)
    map_name = Column(String)
    map_type = Column(String)
    map_owner_id = Column(String)
    map_owner_name = Column(String)
    map_size = Column(JSON)         # [x, y]
    agent_pos = Column(JSON)        # [x, y]
    exit_pos = Column(JSON)         # [x, y]
    bit_list = Column(JSON)
    trap_list = Column(JSON)
    max_steps = Column(Integer)
