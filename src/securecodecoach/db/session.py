from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from securecodecoach.config import Settings, get_settings
from securecodecoach.db.url import get_connect_args, to_async_database_url

settings = get_settings()

DATABASE_URL = to_async_database_url(settings.database_url)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=get_connect_args(settings.database_url),
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def make_engine(database_url: str | Settings | None = None) -> AsyncEngine:
    if isinstance(database_url, Settings):
        url = database_url.database_url
    else:
        url = database_url or settings.database_url
    return create_async_engine(
        to_async_database_url(url),
        echo=False,
        pool_pre_ping=True,
        connect_args=get_connect_args(url),
    )


def make_sessionmaker(bind_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
    )
