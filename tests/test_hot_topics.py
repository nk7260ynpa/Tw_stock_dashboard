"""熱門話題 API 端點測試。

測試漲停板與跌停板 API 的回應格式與錯誤處理。
因測試環境無資料庫連線，使用 mock 模擬資料庫查詢。
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from tw_stock_dashboard.web.app import app

client = TestClient(app)


@pytest.fixture()
def mock_engines():
    """模擬資料庫引擎，避免實際連線。"""
    with patch(
        "tw_stock_dashboard.web.routers.hot_topics._get_engine"
    ) as mock_get_engine:
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        yield mock_engine


def _make_mock_rows(rows_data):
    """建立模擬的資料庫查詢結果列。

    Args:
        rows_data: 欄位值清單。

    Returns:
        模擬的 Row 物件清單。
    """
    mock_rows = []
    for row_data in rows_data:
        mock_row = MagicMock()
        for key, value in row_data.items():
            setattr(mock_row, key, value)
        mock_rows.append(mock_row)
    return mock_rows


class TestGetHotTopics:
    """測試 GET /api/hot-topics 端點。"""

    def test_response_format_with_mock(self, mock_engines):
        """測試回應格式包含必要欄位。"""
        mock_conn = MagicMock()
        mock_engines.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn,
        )
        mock_engines.connect.return_value.__exit__ = MagicMock(
            return_value=False,
        )

        # 模擬最近交易日查詢
        mock_date_result = MagicMock()
        mock_date_row = MagicMock()
        mock_date_row.latest_date = "2026-02-27"
        mock_date_result.fetchone.return_value = mock_date_row

        # 模擬漲停查詢（空結果）
        mock_empty_result = MagicMock()
        mock_empty_result.__iter__ = MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = [
            mock_date_result,      # _get_latest_trading_date
            mock_empty_result,     # TWSE limit_up
            mock_empty_result,     # TPEX limit_up
            mock_empty_result,     # TWSE limit_down
            mock_empty_result,     # TPEX limit_down
        ]

        response = client.get("/api/hot-topics")
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "limit_up" in data
        assert "limit_down" in data
        assert isinstance(data["limit_up"], list)
        assert isinstance(data["limit_down"], list)

    def test_with_specific_date(self, mock_engines):
        """測試指定日期查詢。"""
        mock_conn = MagicMock()
        mock_engines.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn,
        )
        mock_engines.connect.return_value.__exit__ = MagicMock(
            return_value=False,
        )

        mock_empty_result = MagicMock()
        mock_empty_result.__iter__ = MagicMock(return_value=iter([]))

        mock_conn.execute.side_effect = [
            mock_empty_result,     # TWSE limit_up
            mock_empty_result,     # TPEX limit_up
            mock_empty_result,     # TWSE limit_down
            mock_empty_result,     # TPEX limit_down
        ]

        response = client.get("/api/hot-topics?date=2026-02-27")
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2026-02-27"


class TestGetAvailableDates:
    """測試 GET /api/hot-topics/dates 端點。"""

    def test_dates_response_format(self, mock_engines):
        """測試可用日期回應格式。"""
        mock_conn = MagicMock()
        mock_engines.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn,
        )
        mock_engines.connect.return_value.__exit__ = MagicMock(
            return_value=False,
        )

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(
            return_value=iter([("2026-02-27",), ("2026-02-26",)]),
        )

        mock_conn.execute.return_value = mock_result

        response = client.get("/api/hot-topics/dates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_dates_with_limit(self, mock_engines):
        """測試日期查詢的 limit 參數。"""
        mock_conn = MagicMock()
        mock_engines.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn,
        )
        mock_engines.connect.return_value.__exit__ = MagicMock(
            return_value=False,
        )

        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        mock_conn.execute.return_value = mock_result

        response = client.get("/api/hot-topics/dates?limit=10")
        assert response.status_code == 200


class TestHotTopicsRouteRegistered:
    """測試路由是否正確註冊。"""

    def test_hot_topics_route_exists(self):
        """確認 /api/hot-topics 路由已註冊。"""
        routes = [route.path for route in app.routes]
        assert "/api/hot-topics" in routes

    def test_hot_topics_dates_route_exists(self):
        """確認 /api/hot-topics/dates 路由已註冊。"""
        routes = [route.path for route in app.routes]
        assert "/api/hot-topics/dates" in routes
