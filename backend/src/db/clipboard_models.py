import json
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Boolean, create_engine, Column, Integer, String

from fastapi_users import models

Base = declarative_base()
"""
    Default fields
    id: ID
    email: str
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    """
class User(models.BaseUser, Base):
    __tablename__ = "users"

    name = Column(String) # full name
    devices = Column(String, default="[]") # json list
    

class Clip(Base):
    __tablename__ = "clipboard"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String) # user
    text = Column(String)
    time = Column(String) # datetime
    favorite = Column(Boolean)
    
    
class Folder(Base):
    __tablename__ = "folder"
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    name = Column(String)
    clips = Column(String) # json list[Clip id]
    
    def get_clips(self):
        return json.loads(self.clips)
    
    def put_clips(self, cs):
        self.clips = json.dumps(cs)
    
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 
    
def drop_tables(engine):
    Base.metadata.drop_all(bind=engine)