

import json
from uuid import uuid4
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .db import db
from .db.models import Clipboard, User

from sqlalchemy.orm import Session
        
def create_user(name: str, email: str, db: Session = Depends(db.get_db)):
    id = str(uuid4())
    user = User(id=id, name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id: ", id}


def get_user(user_id: str, db: Session = Depends(db.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def clipboard_socket(websocket: WebSocket, userId: str, db: Session = Depends(db.get_db)):
    await websocket.accept()
    
    try:
        clipboard_items: list[dict] = get_clipboard(userId, db=db) 
    
        # Upon open, send the current state of the clipboard
        if clipboard_items and len(clipboard_items) != 0:
            print("sending current clipboard")
            clip_text = json.dumps(clipboard_items)
            await websocket.send_text(clip_text)
        
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            
            try:
                data_d = json.loads(data)
            except json.JSONDecodeError:
                print(f"Could not parse data: {data}")
                continue
            if not isinstance(data_d, dict):
                print(f"Data was not a dict: {data}")
                continue

            text = data_d.get('text', '')
            time = data_d.get('time', '')
            
            body = Body(text=text, user=userId, time=time)
                    
            await websocket.send_text(json.dumps(add_to_clipboard(userId, body, db=db)))
    except WebSocketDisconnect:
        print("Client disconnected")

def get_clipboard(user_id: str, db: Session = Depends(db.get_db)):
    clipboard = db.query(Clipboard).filter(Clipboard.user_id == user_id).all()

    if clipboard is None:
        return []

    return [{"text": clip.text, "time": clip.time} for clip in clipboard]

class Body(BaseModel):
    text: str
    user: str
    time: str

def add_to_clipboard(userId: str, body: Body, db: Session = Depends(db.get_db)):
    id = str(uuid4())
    new_clip = Clipboard(id=id, user_id=userId, text=body.text, time=body.time) # Generate time in backend?
    
    db.add(new_clip)
    
    db.commit()
    
    return [{"text": new_clip.text, "time": new_clip.time}]