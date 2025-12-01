import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings

# Helper to parse the database URL and replace the database name
def get_test_db_url(original_url: str, test_db_name: str = "test_chack") -> str:
    # Assuming format: mysql+mysqlconnector://user:pass@host:port/dbname
    # or mysql+aiomysql://...
    # We want to connect to the server, not the specific DB first to create it
    
    # Simple string manipulation for now, can be robustified with urlparse if needed
    base_url = original_url.rsplit('/', 1)[0]
    return f"{base_url}/{test_db_name}", base_url

async def create_test_database():
    db_name = "test_chack"
    
    # Get the production DB URL from settings
    original_url = settings.SQLALCHEMY_DATABASE_URL
    
    # We need a URL that connects to the MySQL server but not a specific DB (or 'mysql' system db)
    # to execute CREATE DATABASE.
    # Construct a URL to connect to 'mysql' system database or just the root
    # Note: settings.SQLALCHEMY_DATABASE_URL is synchronous (mysql+mysqlconnector) usually?
    # Let's check what the config says. The config uses mysql+mysqlconnector by default for sync?
    # But tests need async.
    
    # Let's assume we use the async driver for this operation
    if "mysql+mysqlconnector" in original_url:
        async_base_url = original_url.replace("mysql+mysqlconnector", "mysql+aiomysql")
    else:
        async_base_url = original_url

    server_url = async_base_url.rsplit('/', 1)[0] # Remove database name
    
    print(f"Connecting to MySQL server at: {server_url}...")
    
    # Connect to the server (no specific DB, or 'information_schema')
    engine = create_async_engine(f"{server_url}/information_schema", echo=True)
    
    async with engine.begin() as conn:
        # Check if database exists
        result = await conn.execute(text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}'"))
        if result.fetchone():
            print(f"Database '{db_name}' already exists.")
            # Optional: Drop it to start fresh?
            # await conn.execute(text(f"DROP DATABASE {db_name}"))
            # print(f"Database '{db_name}' dropped.")
        else:
            print(f"Database '{db_name}' does not exist. Creating...")
            await conn.execute(text(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            print(f"Database '{db_name}' created successfully.")

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_test_database())
