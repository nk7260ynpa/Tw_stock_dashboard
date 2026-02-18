"""API 端點測試。"""

from fastapi.testclient import TestClient

from tw_stock_dashboard.web.app import app

client = TestClient(app)


def test_get_tools():
    """測試工具清單 API 回傳正確資料。"""
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    tool = data[0]
    assert "id" in tool
    assert "name" in tool
    assert "description" in tool
    assert "icon" in tool
