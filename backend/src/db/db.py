from functools import wraps
import json
import os
from typing import Callable, ParamSpec, TypeVar
from uuid import uuid4
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import Engine, create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from db.clipboard_models import Clip, Folder, User
from fastapi_users import password

import dotenv
from db import clipboard_models

R = TypeVar("R")
P = ParamSpec("P")

Base = declarative_base()


dotenv.load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "False") == "True"

print(os.getenv("TEST", "dotenv failed to load"))

# Note: 
if DEV_MODE:
    DATABASE_URL = "sqlite+aiosqlite:///./dev.db"
else:
    DATABASE_URL = os.getenv("SUPABASE_URL")

engine: Engine = None
session_maker = None

pw_helper = password.PasswordHelper()

async def init_db():
    global engine
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    global session_maker
    
    
    session_maker = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    
    if os.getenv("DROP_TABLES", "False") == "True":
        print("Dropping tables")
        clipboard_models.drop_tables(engine)
        
    await clipboard_models.create_tables(engine)

    test_user_id = create_test_user()
    print(f"Created test user with id: {test_user_id}")

def session_handler(func: Callable[P, R]) -> Callable[P, R | None]:

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
        if kwargs.get('session') is not None:
            return func(*args, **kwargs)
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
    
    hashed = pw_helper.hash("testpass")
            
    test_user = User(name="testuser", 
                     email="testemail@test.com", 
                     hashed_password=hashed, 
                     is_active=True,
                     is_superuser=False,
                     is_verified=False,
                     devices="[]")
    
    session.add(test_user)
    session.commit()
    
    return test_user.id
    
class Body(BaseModel):
    text: str
    user: str
    time: str

@session_handler
def add_to_clipboard(session: Session, userId: str, text: str, time: str, folder: str):
    id = str(uuid4())
    new_clip = Clip(id=id, user_id=userId, text=text, time=time, favorite=folder=="Favorites") # Generate time in backend?
    
    session.add(new_clip)
    
    if folder != "All":
        folder = session.query(Folder).filter_by(user_id=userId, name=folder).first()
        
        if not folder:
            print("Folder does not exist")
            return {"status": "failure"}
            
        try:
            clip_ids: list[str] = folder.get_clips()
        except json.JSONDecodeError:
            print(f"Error parsing clips as json: {folder.clips}")
            return {"status": "failure"}

        clip_ids.append(id)
        folder.put_clips(clip_ids)
        
        session.add(folder)
    
    session.commit()
    
    return {"text": new_clip.text, "time": new_clip.time, "id": new_clip.id, "favorite": new_clip.favorite}

@session_handler
def get_clipboard(session: Session, user_id: str):
    clipboard = session.query(Clip).filter(Clip.user_id == user_id).all()

    if clipboard is None:
        return []
    
    clipboard.sort(key=lambda clip: clip.time, reverse=True)
    contents = [{"text": clip.text, "time": clip.time, "id": clip.id, "favorite": clip.favorite} for clip in clipboard]
    print(f"Clipboard contents: ", contents)
    return contents

@session_handler
def toggle_clip_in_folder(session: Session, user_id, clip_id, folder_name):
    
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
        
    if folder_name == "Favorites":
        clip = session.query(Clip).filter_by(id=clip_id).first()
        if clip:
            clip.favorite = not clip.favorite
            session.add(clip)

    session.commit()

@session_handler
def create_favorites_folder(session: Session, user_id):
    
    user = session.query(User).filter_by(id=user_id).first()
    
    if not user:
        print("User missing from db")
        return
    
    id = str(uuid4())
    
    folder = Folder(id=id, user_id=user_id, name="Favorites", clips=json.dumps([]))
    
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

@session_handler
def get_clip(session: Session, clip_id: str):
    clip = session.query(Clip).filter(Clip.id == clip_id).first()
    return clip

@session_handler
def get_folder(session: Session, user_id: str, folder_name: str):
    print("Getting folder: ", folder_name)
    if folder_name == "All":
        return get_clipboard(user_id)
    
    folder = session.query(Folder).filter_by(user_id=user_id, name=folder_name).first()
    if not folder:
        return []
    
    clip_ids = [c for c in folder.get_clips() if c]
    
    if len(clip_ids) == 0:
        return []
    
    clips = [c for c in map(lambda clip_id: get_clip(session=session, clip_id=clip_id), clip_ids) if c]
    clips.sort(key=lambda clip: clip.time, reverse=True)
    
    contents = [{"text": clip.text, "time": clip.time, "id": clip.id, "favorite": clip.favorite} for clip in clips]
    print(f"Contents of folder {folder_name}: ", contents)
    
    return contents
    

@session_handler
def get_folders(session: Session, user_id):
    return {"status": "success", "folders": [{"name": folder.name} for folder in session.query(Folder).filter_by(user_id=user_id).all()]}

@session_handler
def add_folder(session: Session, user_id, folder_name):
    id = str(uuid4())
    
    folder = Folder(id=id, user_id=user_id, name=folder_name, clips=json.dumps([]))
    
    session.add(folder)
    session.commit()
    
    return {"status": "success", "message": "Successfully created new folder", "data": {"id": id}}

@session_handler
def remove_folder(session: Session, user_id, folder_name):
    folder = session.query(Folder).filter_by(user_id=user_id, name=folder_name).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    session.delete(folder)
    session.commit()
    
    return {"status": "success", "message": "Successfully deleted folder"}