# schemas.py
from fastapi_users import schemas
from typing import Optional
from uuid import UUID

class UserRead(schemas.BaseUser[UUID]):
    name: Optional[str] = None
    devices: Optional[str] = None

class UserCreate(schemas.BaseUserCreate):
    name: Optional[str] = None
    devices: Optional[str] = None