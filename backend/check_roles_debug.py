import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import Role

async def check_roles():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Role))
        roles = result.scalars().all()
        print(f"Total roles found: {len(roles)}")
        for role in roles:
            print(f"Role: {role.name}, ID: {role.id}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.join(os.getcwd(), 'backend'))
    asyncio.run(check_roles())
