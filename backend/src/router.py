

import json
from typing import Optional
from uuid import uuid4
from fastapi import Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .db import db
from .db.models import Clip, User

from sqlalchemy.orm import Session
        
def create_user(name: str, email: str):
    
    id = db.create_user(name, email)
    
    if id:
        return {"status": "success", "message": "Created new user", "data": {"id: ", id}}
    else:
        return {"status": "failure", "message": "Failed to create new user", "data": {}}
def get_user(user_id: str):
    return db.get_user(user_id)

async def clipboard_socket(websocket: WebSocket, userId: str):
    await websocket.accept()
    
    try:
        clipboard_items: list[dict] = db.get_clipboard(userId) 
    
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
                                
            await websocket.send_text(json.dumps(db.add_to_clipboard(userId, text, time)))
    except WebSocketDisconnect:
        print("Client disconnected")
        

async def folder_socket(websocket: WebSocket, userId: str, folderName: str):
    await websocket.accept()
    
    try:
        clipboard_items: list[dict] = db.get_folder(userId, folderName)
    
        # Upon open, send the current state of the clipboard
        if clipboard_items and len(clipboard_items) != 0:
            print("sending folder: ", folderName)
            clip_text = json.dumps(clipboard_items)
            await websocket.send_text(clip_text)
        
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data} on folder: {folderName}")
            
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
            
            clip = db.add_to_clipboard(userId, text, time)
            if clip and folderName != 'All':
                c = clip[0]
                clip_id = c.get('id')
                db.toggle_clip_in_folder(userId, clip_id, folderName)
                                
            await websocket.send_text(json.dumps(clip))
    except WebSocketDisconnect:
        print("Client disconnected")

def get_clipboard(user_id: str):
    return db.get_clipboard(user_id)

class Body(BaseModel):
    text: str
    user: str
    time: str
    
def add_to_clipboard(userId: str, text: Body):
    ...
    

def add_to_folder(userId: str, clipId: str, folderName: str):
    return db.toggle_clip_in_folder(userId, clipId, folderName)

def get_folders(userId: str):
    return db.get_folders(userId)

def add_folder(userId: str, folderName: str):
    return db.add_folder(userId, folderName)

def get_folder(userId: str, folderName: str):
    return db.get_folder(userId, folderName)

def remove_folder(userId: str, folderName: str):
    return db.remove_folder(userId, folderName)