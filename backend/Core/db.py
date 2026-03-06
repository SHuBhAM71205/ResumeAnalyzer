from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from backend.Core.config import settings


engine = create_async_engine(settings.DATABASE_URL, pool_size=20, max_overflow=0)


SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session
