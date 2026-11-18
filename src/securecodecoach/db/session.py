from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from securecodecoach.config import get_settings
from securecodecoach.db.url import to_async_database_url

settings = get_settings()

DATABASE_URL = to_async_database_url(settings.database_url)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"ssl": "require"},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
