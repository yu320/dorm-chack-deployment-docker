from fastapi import Depends, HTTPException, status, Request, Response # [修改] 引入 Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select 
from sqlalchemy.orm import joinedload

from . import schemas, models
from .crud import crud_user
from .utils.security import verify_password
from .database import get_db 
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

# [新增] 核心邏輯：檢查並自動刷新 Token 的共用函式
def check_and_refresh_token(response: Response, token: str, auth_service: AuthService, user: models.User):
    """
    檢查 Token 是否快過期，如果是，則簽發新 Token 並透過 Set-Cookie 延長使用者會話。
    """
    try:
        # 解碼 Token 以取得過期時間 (exp)
        # 注意：前端傳來的 Token 已經通過了 auth_service.get_current_user 的驗證，所以這裡是安全的
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp")
        
        if exp:
            now = datetime.now(timezone.utc)
            exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
            time_left = exp_time - now
            
            # 設定門檻：如果剩餘時間 < 設定值 (例如 30 分鐘)
            threshold = timedelta(minutes=settings.SLIDING_REFRESH_THRESHOLD_MINUTES)
            
            if time_left < threshold:
                # 1. 產生全新的 Access Token (重置時間為完整的 60 分鐘)
                access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                new_token = auth_service.create_access_token(
                    data={"sub": user.username}, expires_delta=access_token_expires
                )
                
                # 2. 透過 Set-Cookie Header，讓瀏覽器在背景更新 Cookie
                response.set_cookie(
                    key="access_token",
                    value=new_token,
                    httponly=True,
                    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    path="/",
                    secure=not settings.DEBUG,
                    samesite="lax",
                )
                # print(f"🔄 Token Refreshed for user: {user.username}") # 開發時可開啟此行確認運作

    except Exception as e:
        # 如果刷新檢查過程失敗（例如 decode 異常），不要讓整個請求失敗，只在 console 留紀錄
        print(f"⚠️ Token refresh check failed: {e}")

# [修改] 注入 Response 並呼叫刷新邏輯
async def get_current_user(
    response: Response, # [新增] 注入 Response 物件
    token: str = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> models.User:
    user = await auth_service.get_current_user(token)
    # 執行滑動過期檢查
    check_and_refresh_token(response, token, auth_service, user)
    return user

# [修改] 注入 Response 並呼叫刷新邏輯
async def get_current_active_user(
    response: Response, # [新增] 注入 Response 物件
    token: str = Depends(get_token_from_cookie),
    auth_service: AuthService = Depends(get_auth_service)
) -> models.User:
    user = await auth_service.get_current_active_user(token)
    # 執行滑動過期檢查
    check_and_refresh_token(response, token, auth_service, user)
    return user

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