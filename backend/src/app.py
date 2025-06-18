import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

import fastapi
from starlette.middleware import cors

from db import db
import clipboard.clip_router as clip_router

DEV_MODE = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield

    

def app_factory():
    router = set_up_router()
    
    app = fastapi.FastAPI(lifespan=lifespan)
    
    app.include_router(router)
    
    app.include_router()
    
    if DEV_MODE:
        app.add_middleware(
            cors.CORSMiddleware,
            allow_origins=[
                "http://localhost:3000"
            ],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    
    asyncio.run(db.init_db())
        
    return app
    
    


    