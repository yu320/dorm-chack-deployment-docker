from fastapi import Depends, HTTPException, status, Request # Import Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
from sqlalchemy import select # Import select for async queries
from sqlalchemy.orm import joinedload

from . import schemas, models
from .crud import crud_user
from .utils.security import verify_password
from .database import get_db # Import the async get_db from database.py
from .config import settings

from .services.auth_service import AuthService, get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# 新增從 Cookie 獲取 Token 的依賴項
async def get_token_from_cookie(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return access_token

async def get_token_from_cookie_optional(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")

async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> models.User:
    return await auth_service.get_current_user(token)

async def get_current_active_user(
    token: str = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> models.User:
    return await auth_service.get_current_active_user(token)





from typing import Optional, Union, List

# ... (imports remain same)

class PermissionChecker:
    def __init__(self, required_permissions: Union[str, List[str]], logic: str = "AND"):
        """
        :param required_permissions: A single permission string or a list of permission strings.
        :param logic: 'AND' (user must have all) or 'OR' (user must have at least one). Defaults to 'AND'.
        """
        self.required_permissions = [required_permissions] if isinstance(required_permissions, str) else required_permissions
        self.logic = logic.upper()
        if self.logic not in ["AND", "OR"]:
             raise ValueError("Permission logic must be 'AND' or 'OR'")

    def __call__(self, current_user: models.User = Depends(get_current_active_user)):
        user_permissions = crud_user.get_user_permissions(current_user)
        
        # Super-admin check
        if "admin:full_access" in user_permissions:
            return current_user
            
        has_permission = False
        if self.logic == "OR":
            has_permission = any(perm in user_permissions for perm in self.required_permissions)
        else: # AND
            has_permission = all(perm in user_permissions for perm in self.required_permissions)

        if not has_permission:
            perms_str = ", ".join(self.required_permissions)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"The user does not have the required permissions ({self.logic}): {perms_str}",
            )
        return current_user
