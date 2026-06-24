from ...db.session import AsyncSessionLocal

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
