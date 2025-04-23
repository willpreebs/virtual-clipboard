
from sqlalchemy import Engine, create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

from . import models

Base = declarative_base()

DATABASE_URL = "sqlite:///./test.db"

engine: Engine = None
session_maker = None

def init_db():
    global engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    global session_maker
    
    
    session_maker = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    models.create_tables(engine)
    
# Dependency to get DB session
def get_db():
    session = session_maker()
    try:
        yield session
    finally:
        session.close()

