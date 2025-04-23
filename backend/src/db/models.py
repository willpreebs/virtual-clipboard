from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True) # uuid
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    devices = Column(String) # json list


class Clipboard(Base):
    __tablename__ = "clipboard"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String) # user
    text = Column(String)
    time = Column(String) # datetime
    
    
def create_tables(engine):
    Base.metadata.create_all(bind=engine)