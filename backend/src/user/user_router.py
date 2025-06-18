


import os
from uuid import UUID
from fastapi import Request
from fastapi_users import FastAPIUsers
import fastapi_users
import jwt

from db.clipboard_models import User
from db.schemas import UserCreate, UserRead

from fastapi_users import BaseUserManager, UUIDIDMixin, InvalidPasswordException
from uuid import UUID
from typing import Optional
from dotenv import load_dotenv

from jwt_auth import jwt_backend

load_dotenv()

RESET_PASS_SECRET=os.getenv("RESET_PASSWORD_SECRET")
VERIFICATION_TOKEN_SECRET=os.getenv("VERIFICATION_TOKEN_SECRET")

class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    user_db_model = User
    reset_password_token_secret = RESET_PASS_SECRET
    verification_token_secret = VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.id} has registered.")
        # send welcome email, etc.
        
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
        # send verification email
        
    async def validate_password(
        self,
        password: str,
        user: UserCreate | User
    ) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

async def get_user_manager(user_db):
    yield UserManager(user_db)

def get_user_router():
     
    fastapi_users = FastAPIUsers[User, UUID] (
        get_user_manager,
        [jwt_backend], # Just use JWT auth for now
        User,
        UserCreate
    )
    
    current_active_user = fastapi_users.current_user(active=True)
    
    fastapi_users.get_auth_router(jwt_backend)
    
    
    return user_router
    