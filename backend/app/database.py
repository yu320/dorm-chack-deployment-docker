from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from .config import settings

# Update the database URL for aiomysql
ASYNC_SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL.replace(
    "mysql+mysqlconnector://", "mysql+aiomysql://"
)

async_engine = create_async_engine(
    ASYNC_SQLALCHEMY_DATABASE_URL,
    echo=settings.DEBUG, # Set to False in production
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
