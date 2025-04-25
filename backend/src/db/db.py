
from functools import wraps
import json
from typing import Callable, ParamSpec, TypeVar
from uuid import uuid4
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from db.models import Clip, Folder, User

from db import models

R = TypeVar("R")
P = ParamSpec("P")

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

    with session_maker() as session:
        create_test_user(session)
    

def session_handler(func: Callable[P, R]) -> Callable[P, R | None]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        # Instantiate a new session
        session = session_maker()
        try:
            # Pass session as an argument to the wrapped function
            return func(session, *args, **kwargs)
        except Exception as e:
            print(f"Database error in {func.__name__}: {e}")
            try:
                session.rollback()  # Rollback if there was an error
                print(f"Rollback successful")
            except Exception as rollback_error:
                print(f"Rollback error in {func.__name__}: {rollback_error}")
        finally:
            session.close()  # Ensure session is closed after the operation

    return wrapper
        
@session_handler
def create_test_user(session: Session):
        
    user = User(id='1', name="testuser", email="testemail@test.com")
    
    session.add(user)
    session.commit()
    
class Body(BaseModel):
    text: str
    user: str
    time: str

@session_handler
def add_to_clipboard(session: Session, userId: str, text: str, time: str):
    id = str(uuid4())
    new_clip = Clip(id=id, user_id=userId, text=text, time=time) # Generate time in backend?
    
    session.add(new_clip)
    
    session.commit()
    
    return [{"text": new_clip.text, "time": new_clip.time}]

@session_handler
def get_clipboard(session: Session, user_id: str):
    clipboard = session.query(Clip).filter(Clip.user_id == user_id).all()

    if clipboard is None:
        return []

    return [{"text": clip.text, "time": clip.time} for clip in clipboard]

@session_handler
def toggle_clipboard_folder_status(session: Session, user_id, clip_id, folder_name):
    
    folder = session.query(Folder).filter_by(user_id=user_id, name=folder_name).first()
    
    if not folder:
        print("Folder does not exist")
        return {"status": "failure"}
        
    try:
        clip_ids: list[str] = folder.get_clips()
    except json.JSONDecodeError:
        print(f"Error parsing clips as json: {folder.clips}")
        return {"status": "failure"}

    if clip_id in clip_ids:
        # remove from folder
        clip_ids.remove(clip_id)
        folder.put_clips(clip_ids)
        
    else:
        # add to folder
        clip_ids.append(clip_id)
        folder.put_clips(clip_ids)

    session.commit()
    
    return {"status": "success"}

@session_handler
def create_favorites_folder(session: Session, user_id):
    
    user = session.query(User).filter_by(user_id=user_id).first()
    
    if not user:
        print("Folder does not exist")
        return
    
    id = str(uuid4())
    
    folder = Folder(id=id, user_id=user_id, name="favorites", clips=json.dumps([]))
    
    session.add(folder)
    session.commit()
    
    # return {"status": "success", "message": "Successfully created new folder", "data": {"id": id}}

@session_handler
def create_user(session: Session, name: str, email: str):
    id = str(uuid4())
    user = User(id=id, name=name, email=email)
    session.add(user)
    session.commit()
    
    create_favorites_folder(id)
    
    return id

@session_handler
def get_user(session: Session, user_id: str):
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user