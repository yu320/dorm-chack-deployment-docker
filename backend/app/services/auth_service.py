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
        user = await crud_user.get_by_username(self.db, username=username)
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
        db_user = await crud_user.get_by_username(self.db, username=user_in.username)
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        
        assigned_roles: List[str] = []
        # 處理使用者角色，第一個使用者為 Admin，其餘預設為 Student
        first_user_records = await crud_user.get_multi(self.db, skip=0, limit=1)
        if len(first_user_records) == 0: 
            assigned_roles.append("admin") # Assign admin role to the first user
        else:
            assigned_roles.append("student") # Default to student for others

        created_user = await crud_user.create(self.db, obj_in=user_in, role_names=assigned_roles)  
        
        # 發送驗證信
        if hasattr(created_user, "verification_token") and created_user.verification_token:
            # Import inside method to avoid circular dependency
            from .notification_service import notification_service
            
            verification_link = f"{settings.API_BASE_URL}/verify-email?token={created_user.verification_token}"
            
            # Generate link (assuming frontend handles /verify-email?token=...)
            # Wait, verification link structure needs to match frontend route. 
            # If frontend is Nuxt, it might be something like /verify?token=...
            # Or is it an API link that redirects?
            # The prompt implies "Click link to register success". Usually this means frontend page.
            # Let's assume frontend has a page /verify-email that takes the token.
            # However, the current `auth.py` endpoint is GET /verify-email/{token} returning JSON.
            # If the user clicks this directly, they get a JSON response "Email verified successfully".
            # That's fine for an API-centric approach, but better if it redirects to a login page.
            # For now, I will point to the Frontend URL if possible, or the API URL if strictly backend task.
            # The `password-recovery` uses `settings.API_BASE_URL/reset-password?token=...`.
            # Let's assume `settings.API_BASE_URL` points to the Frontend (or API?). 
            # In `auth.py`: `reset_link = f"{settings.API_BASE_URL}/reset-password?token={reset_token}" # Frontend URL`
            # So I should use the same pattern.
            
            # Note: verify-email endpoint in auth.py is `@router.get("/verify-email/{token}")`. 
            # This is an API endpoint. If I send this link, the browser opens JSON.
            # If I want a frontend page, I should send e.g. `http://frontend/verify-email?token=...`
            # and that page calls the API.
            # Given the `password-recovery` logic in `auth.py` uses `reset-password?token=...` as a Frontend URL,
            # I should probably use a Frontend URL for verification too.
            # Let's use `/verify-email?token=` and ensure the frontend handles it.
            # Wait, I am only modifying backend now? 
            # The user asked for "Click link to register success".
            # I will stick to the pattern used in password reset.
            
            verification_link = f"{settings.API_BASE_URL}/verify-email?token={created_user.verification_token}"

            # Determine language (default to en or infer from context if possible, but here we have no request context easily)
            # We could pass language in UserCreate? No. Default to 'zh' for this project context? 
            # Or just 'en'. Let's default to 'zh' given the context files are largely Chinese oriented.
            lang = "zh" 

            await notification_service.send_verification_email(
                to_email=created_user.email, 
                username=created_user.username, 
                verification_link=verification_link,
                lang=lang
            )

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
        user = await crud_user.get_by_username(self.db, username=token_data.username)
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
