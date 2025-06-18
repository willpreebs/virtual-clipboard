

import json
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from db import clipboard_models, db
from sqlalchemy.orm import Session
        

def set_up_router() -> APIRouter:
    
    server = APIRouter()
    
    # server.add_api_route(path="/users", endpoint=router.create_user, methods=["POST"])
    
    # server.add_api_route(path="/users/{user_id}", endpoint=router.get_user, methods=["POST"])
    
    
    server.add_api_route(path="/user/{user_id}/clipboard", endpoint=get_clipboard, methods=["GET"])
    
    server.add_api_route(path="/user/{userId}/clipboard", endpoint=add_to_clipboard, methods=["POST"])
        
    server.add_api_websocket_route(path="/user/{userId}/updateFolder/{folderName}", endpoint=socket)
    
    server.add_api_route(path="/user/{userId}/clip/{clipId}/folder/{folderName}", endpoint=add_to_folder, methods=["POST"])
        
    server.add_api_route(path="/user/{userId}/addFolder/{folderName}", endpoint=add_folder, methods=["POST"])
    
    server.add_api_route(path="/user/{userId}/removeFolder/{folderName}", endpoint=remove_folder, methods=["DELETE"])
    
    server.add_api_route(path="/user/{userId}/folders", endpoint=get_folders, methods=["GET"])
    
    server.add_api_route(path="/user/{userId}/folder/{folderName}", endpoint=get_folder, methods=["GET"])
    
    return server


def create_user(name: str, email: str):
    
    id = db.create_user(name, email)
    
    if id:
        return {"status": "success", "message": "Created new user", "data": {"id: ", id}}
    else:
        return {"status": "failure", "message": "Failed to create new user", "data": {}}
def get_user(user_id: str):
    return db.get_user(user_id)

async def socket(websocket: WebSocket, userId: str, folderName: str):
    await websocket.accept()
    
    try:
        clipboard_items: list[dict] = db.get_folder(userId, folderName)
    
        # Upon open, send the current state of the clipboard
        if clipboard_items and len(clipboard_items) != 0:
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
            
            clip_dict: dict = db.add_to_clipboard(userId, text, time, folder=folderName)
                             
            await websocket.send_text(json.dumps(clip_dict))
    except WebSocketDisconnect:
        print("Client disconnected")

def get_clipboard(user_id: str):
    return db.get_clipboard(user_id)

class Body(BaseModel):
    text: str
    time: str
    
def add_to_clipboard(userId: str, body: Body):
    print(f"Received request to post to clipboard with text: {body.text} at time: {body.time}")
    

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