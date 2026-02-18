"""FastAPI 應用程式基礎測試。"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """測試健康檢查端點回傳正常狀態。"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_api_v1_status(client):
    """測試 API v1 狀態端點回傳正常。"""
    response = await client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["api_version"] == "v1"
    assert data["status"] == "ok"
