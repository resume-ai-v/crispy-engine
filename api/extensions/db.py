# extensions/db.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://launchhire_user:JCPsai7au1DT7GceyZt84mjusrfjJVBZ@dpg-d11m1k8dl3ps73cud8d0-a.oregon-postgres.render.com/launchhire")

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
