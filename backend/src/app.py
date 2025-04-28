from fastapi import FastAPI, APIRouter

import fastapi
from starlette.middleware import cors

from . import router
from .db import db

DEV_MODE = True

def set_up_router() -> APIRouter:
    
    server = APIRouter()
    
    server.add_api_route(path="/users", endpoint=router.create_user, methods=["POST"])
    
    server.add_api_route(path="/users/{user_id}", endpoint=router.get_user, methods=["POST"])
    
    server.add_api_route(path="/user/{user_id}/clipboard", endpoint=router.get_clipboard, methods=["GET"])
    
    server.add_api_route(path="/user/{user_id}/clipboard", endpoint=router.add_to_clipboard, methods=["POST"])
    
    server.add_api_websocket_route(path="/user/{userId}/updateClipboard", endpoint=router.clipboard_socket)
    
    server.add_api_websocket_route(path="/user/{userId}/updateFolder/{folderName}", endpoint=router.folder_socket)
    
    server.add_api_route(path="/user/{userId}/clip/{clipId}/folder/{folderName}", endpoint=router.add_to_folder, methods=["POST"])
        
    server.add_api_route(path="/user/{userId}/addFolder/{folderName}", endpoint=router.add_folder, methods=["POST"])
    
    server.add_api_route(path="/user/{userId}/removeFolder/{folderName}", endpoint=router.remove_folder, methods=["DELETE"])
    
    server.add_api_route(path="/user/{userId}/folders", endpoint=router.get_folders, methods=["GET"])
    
    server.add_api_route(path="/user/{userId}/folder/{folderName}", endpoint=router.get_folder, methods=["GET"])
    
    
    
    return server
    

def app_factory():
    router = set_up_router()
    
    app = fastapi.FastAPI()
    
    app.include_router(router)
    
    if DEV_MODE:
        app.add_middleware(
            cors.CORSMiddleware,
            allow_origins=[
                "http://localhost:3000"
            ],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    
    db.init_db()
        
    return app
    
    


    