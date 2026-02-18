"""資料庫連線管理。"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """SQLAlchemy 基礎模型類別。"""


async def get_session() -> AsyncSession:
    """取得資料庫 session。

    Yields:
        AsyncSession: 非同步資料庫 session。
    """
    async with async_session() as session:
        yield session
