import html # Import html for escaping
import logging # Import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request # Import Request
from urllib.parse import urljoin # Import urljoin
from sqlalchemy import select # For verifying user status

from ... import schemas, auth as auth_dependency
from ...crud import crud_user, crud_audit # Make sure crud_user and crud_audit are imported
from ...utils import security # Import security module
from ...utils.email import send_email as send_email_util # Import email sender
from ...config import settings
from ...services.auth_service import AuthService, get_auth_service
from ...services.notification_service import notification_service
from ...limiter import limiter # 引入 limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/token", response_model=schemas.Token)
@limiter.limit("5/minute")  # Temporarily disabled to debug
async def login_for_access_token(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logs in a user, sets an HttpOnly cookie for the access token,
    and returns an access token.
    """
    user = await auth_service.authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Audit Log: Login
    await crud_audit.create(
        db=auth_service.db,
        obj_in={
            "action": "LOGIN",
            "resource_type": "User",
            "resource_id": str(user.id),
            "details": {"username": user.username},
        },
        user_id=user.id,
        ip_address=request.client.host if request.client else None
    )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        secure=not settings.DEBUG,
        samesite="lax",
    )
    return {"access_token": access_token, "token_type": "bearer"} # 返回 token 物件

@router.post("/logout")
async def logout(
    response: Response, # Inject Response
    token: str | None = Depends(auth_dependency.get_token_from_cookie_optional), # Use optional dependency
    auth_service: AuthService = Depends(get_auth_service)
):
    # Always delete the cookie first to ensure logout happens on the client side
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=not settings.DEBUG,
        samesite="lax",
        httponly=True
    )

    if not token:
        return {"message": "Successfully logged out (no token found)"}

    try:
        # user = await auth_service.get_current_user(token) # We don't strictly need the user object to blacklist the token
        
        # Decode token to get JTI and EXP for blocklisting
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        
        if jti and exp:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            await crud_user.add_token_to_blocklist(auth_service.db, jti=jti, expires_at=expires_at)
            
    except JWTError:
        # Token is invalid, but we already deleted the cookie, so just ignore
        pass
    except Exception as e:
        # Log other errors but don't fail the logout request
        logger.error(f"Error during logout token blocklisting: {e}")

    return {"message": "Successfully logged out"}

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(
    request: Request, # 引入 Request
    user_in: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
        """
        Registers a new user. Email verification is handled by AuthService.
        """
        db_user = await crud_user.get_by_email(auth_service.db, email=user_in.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        try:
            user = await auth_service.register_user(user_in)
        except ValueError as e:
             raise HTTPException(status_code=400, detail=str(e))

        return user


@router.get("/verify-email/{token}", response_model=schemas.Message, status_code=status.HTTP_200_OK)
async def verify_email(token: str, auth_service: AuthService = Depends(get_auth_service)):
    """
    Verifies the user's email address using the provided token.
    """
    user = await crud_user.verify_user_account(auth_service.db, verification_token=token) # 使用 auth_service.db
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    
    return {"message": "Email verified successfully. Your account is now active."}

@router.post("/password-recovery", response_model=schemas.Message, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def password_recovery(
    request: Request, # 引入 Request for link generation
    email_data: schemas.RequestPasswordReset,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Requests a password reset by sending a reset token to the user's email.
    """
    user = await crud_user.get_user_by_email(auth_service.db, email=email_data.email)
    if not user:
        # For security, don't reveal if the user exists or not
        return {"message": "If an account with that email exists, a password reset link has been sent."}
    
    # Use the security module to create a JWT reset token
    expires_delta = timedelta(minutes=60) # Set expiration to 60 minutes
    reset_token = security.create_password_reset_token(email=email_data.email, expires_delta=expires_delta)
    
    reset_link = f"{settings.API_BASE_URL}/reset-password?token={reset_token}" # Frontend URL

    # DX Optimization: Log reset link in DEBUG mode
    if settings.DEBUG:
        logger.info(f"==========================================")
        logger.info(f"PASSWORD RESET LINK (DEBUG): {reset_link}")
        logger.info(f"==========================================")
    
    # Detect language
    accept_language = request.headers.get("accept-language", "en")
    lang = "zh" if "zh" in accept_language.lower() else "en"

    # Send password reset email in background
    background_tasks.add_task(
        notification_service.send_password_reset_email,
        to_email=user.email,
        username=user.username,
        reset_link=reset_link,
        lang=lang
    )

    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/reset-password", response_model=schemas.Message, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    password_reset_data: schemas.ResetPassword,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Resets the user's password using a valid reset token.
    """
    if password_reset_data.new_password != password_reset_data.confirm_password:
        raise HTTPException(status_code=400, detail="New password and confirmation do not match.")
    
    # Verify the reset token using the security module
    email = security.verify_password_reset_token(password_reset_data.token)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token.")

    user = await crud_user.reset_user_password(
        auth_service.db,
        email=email,
        new_password=password_reset_data.new_password
    )
    if not user:
        raise HTTPException(status_code=400, detail="User not found or an issue occurred during password reset.")
    
    return {"message": "Password has been reset successfully."}

