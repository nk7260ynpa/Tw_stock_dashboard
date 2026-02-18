"""pytest 設定與共用 fixtures。"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client():
    """建立測試用 HTTP 客戶端。

    Yields:
        AsyncClient: 非同步 HTTP 測試客戶端。
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
