from pydantic_settings import BaseSettings
from pydantic import ConfigDict, model_validator
import os
import logging
from typing import Optional

# Build a path to the .env file.
# It should be in the 'backend' directory, which is two levels up from this file.
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

logger = logging.getLogger("uvicorn")

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=env_path)

    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # First superuser
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    # Email settings
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # Debug settings
    DEBUG: bool = False
    TESTING: bool = False

    # Upload settings
    UPLOAD_DIR: str = "uploads" # Directory to store uploaded files

    # Base URL for the API (e.g., "http://localhost:8000" or "https://api.yourdomain.com")
    API_BASE_URL: str = ""

    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Project settings
    PROJECT_NAME: str = "Chack"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    @model_validator(mode='after')
    def check_security_settings(self):
        if not self.DEBUG:
            # Check CORS for localhost in production
            for origin in self.BACKEND_CORS_ORIGINS:
                if "localhost" in origin or "127.0.0.1" in origin:
                    logger.warning(
                        f"⚠️ SECURITY WARNING: 'localhost' or '127.0.0.1' found in CORS origins ({origin}) "
                        "while DEBUG is False. This is dangerous for production."
                    )
            
            # Check for short SECRET_KEY
            if len(self.SECRET_KEY) < 32:
                 logger.warning(
                    "⚠️ SECURITY WARNING: SECRET_KEY is too short (< 32 chars). "
                    "Please use a stronger key in production."
                )
        return self

settings = Settings()
