import json
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Boolean, create_engine, Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) # uuid
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    devices = Column(String) # json list


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
    
def create_tables(engine):
    Base.metadata.create_all(bind=engine)
    
def drop_tables(engine):
    Base.metadata.drop_all(bind=engine)