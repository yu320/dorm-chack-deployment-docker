# backend/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, models
from ..crud import crud_user
from ..utils.security import verify_password, get_password_hash
from ..config import settings
from ..database import get_db
# from .notification_service import notification_service # 避免循環引用，在需要時再引入

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        """
        驗證使用者憑證。
        """
        user = await crud_user.get_user_by_username(self.db, username=username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        建立 JWT Access Token。
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def register_user(self, user_in: schemas.UserCreate) -> models.User:
        """
        註冊新使用者。
        """
        db_user = await crud_user.get_user_by_username(self.db, username=user_in.username)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        
        assigned_roles: List[str] = []
        # 處理使用者角色，第一個使用者為 Admin
        first_user = await crud_user.get_users(self.db, skip=0, limit=1)
        if first_user["total"] == 0: # Check total count, not the list itself
            assigned_roles.append("admin") # Assign admin role to the first user

        logger.debug(f"Calling crud_user.create_user with user_in={user_in.model_dump()}, role_names={assigned_roles}") # Debug print
        created_user, _ = await crud_user.create_user(self.db, user_in=user_in, role_names=assigned_roles)  # Unpack tuple
        # TODO: 發送驗證信

        return created_user

    async def get_current_user(self, token: str) -> models.User:
        """
        從 JWT Token 中獲取當前使用者。
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = schemas.TokenData(username=username)
        except JWTError:
            raise credentials_exception
        user = await crud_user.get_user_by_username(self.db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

    async def get_current_active_user(self, token: str) -> models.User:
        """
        獲取當前活躍使用者。
        """
        current_user = await self.get_current_user(token)
        if not current_user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        return current_user

# 可以建立一個依賴注入函數來提供 AuthService 實例
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
