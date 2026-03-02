"""熱門話題 API 路由。

提供今日漲停板與跌停板股票資料的 RESTful API。
從 TWSE 和 TPEX 資料庫的 DailyPrice 表查詢，
以漲跌幅是否達到 10% 為判斷標準。
"""

import logging
import os
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

logger = logging.getLogger("tw_stock_dashboard")

router = APIRouter(prefix="/api/hot-topics", tags=["hot-topics"])

# 資料庫連線設定
DB_HOST = os.environ.get("DB_HOST", "tw_stock_database")
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "stock")

# 漲跌幅門檻（台股漲跌幅限制為 10%）
LIMIT_THRESHOLD = Decimal("9.5")

_engines: dict[str, Engine] = {}


def _get_engine(db_name: str) -> Engine:
    """取得或建立指定資料庫的 SQLAlchemy 引擎（延遲初始化）。

    Args:
        db_name: 資料庫名稱（TWSE 或 TPEX）。

    Returns:
        SQLAlchemy Engine 實例。
    """
    if db_name not in _engines:
        url = (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{db_name}"
        )
        _engines[db_name] = create_engine(
            url, pool_pre_ping=True, pool_recycle=3600,
        )
        logger.info("資料庫連線建立完成: %s:%s/%s", DB_HOST, DB_PORT, db_name)
    return _engines[db_name]


def _query_twse_limit_stocks(
    query_date: str,
    direction: str,
) -> list[dict[str, Any]]:
    """查詢 TWSE 漲停或跌停股票。

    Args:
        query_date: 查詢日期，格式 YYYY-MM-DD。
        direction: 方向，"up" 為漲停，"down" 為跌停。

    Returns:
        符合條件的股票清單。
    """
    engine = _get_engine("TWSE")

    # 漲停：Change > 0 且漲幅 >= 門檻
    # 跌停：Change < 0 且跌幅 >= 門檻
    if direction == "up":
        condition = (
            "d.`Change` > 0 "
            "AND d.ClosingPrice > 0 "
            "AND (d.ClosingPrice - d.`Change`) > 0 "
            "AND (d.`Change` / (d.ClosingPrice - d.`Change`) * 100) >= :threshold"
        )
    else:
        condition = (
            "d.`Change` < 0 "
            "AND d.ClosingPrice > 0 "
            "AND (d.ClosingPrice - d.`Change`) > 0 "
            "AND (ABS(d.`Change`) / (d.ClosingPrice - d.`Change`) * 100) >= :threshold"
        )

    # 僅查詢一般股票（4 位數代碼），排除權證、ETN 等衍生性商品
    sql = text(f"""
        SELECT
            d.SecurityCode AS code,
            COALESCE(s.StockName, '') AS name,
            d.ClosingPrice AS close_price,
            d.`Change` AS price_change,
            ROUND(d.`Change` / (d.ClosingPrice - d.`Change`) * 100, 2)
                AS change_percent,
            d.TradeVolume AS volume
        FROM TWSE.DailyPrice d
        LEFT JOIN TWSE.StockName s ON d.SecurityCode = s.SecurityCode
        WHERE d.Date = :query_date
        AND d.SecurityCode REGEXP '^[0-9]{{4}}$'
        AND {condition}
        ORDER BY ABS(d.`Change` / (d.ClosingPrice - d.`Change`) * 100) DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {"query_date": query_date, "threshold": float(LIMIT_THRESHOLD)},
        )
        return [
            {
                "code": row.code,
                "name": row.name,
                "close_price": float(row.close_price),
                "change": float(row.price_change),
                "change_percent": float(row.change_percent),
                "volume": int(row.volume),
                "market": "TWSE",
            }
            for row in result
        ]


def _query_tpex_limit_stocks(
    query_date: str,
    direction: str,
) -> list[dict[str, Any]]:
    """查詢 TPEX 漲停或跌停股票。

    Args:
        query_date: 查詢日期，格式 YYYY-MM-DD。
        direction: 方向，"up" 為漲停，"down" 為跌停。

    Returns:
        符合條件的股票清單。
    """
    engine = _get_engine("TPEX")

    if direction == "up":
        condition = (
            "d.`Change` > 0 "
            "AND d.`Close` > 0 "
            "AND (d.`Close` - d.`Change`) > 0 "
            "AND (d.`Change` / (d.`Close` - d.`Change`) * 100) >= :threshold"
        )
    else:
        condition = (
            "d.`Change` < 0 "
            "AND d.`Close` > 0 "
            "AND (d.`Close` - d.`Change`) > 0 "
            "AND (ABS(d.`Change`) / (d.`Close` - d.`Change`) * 100) >= :threshold"
        )

    # 僅查詢一般股票（4 位數代碼），排除權證、ETN 等衍生性商品
    sql = text(f"""
        SELECT
            d.Code AS code,
            COALESCE(s.Name, '') AS name,
            d.`Close` AS close_price,
            d.`Change` AS price_change,
            ROUND(d.`Change` / (d.`Close` - d.`Change`) * 100, 2)
                AS change_percent,
            COALESCE(d.TradeVolume, 0) AS volume
        FROM TPEX.DailyPrice d
        LEFT JOIN TPEX.StockName s ON d.Code = s.Code
        WHERE d.Date = :query_date
        AND d.Code REGEXP '^[0-9]{{4}}$'
        AND {condition}
        ORDER BY ABS(d.`Change` / (d.`Close` - d.`Change`) * 100) DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(
            sql,
            {"query_date": query_date, "threshold": float(LIMIT_THRESHOLD)},
        )
        return [
            {
                "code": row.code,
                "name": row.name,
                "close_price": float(row.close_price),
                "change": float(row.price_change),
                "change_percent": float(row.change_percent),
                "volume": int(row.volume),
                "market": "TPEX",
            }
            for row in result
        ]


def _get_latest_trading_date() -> str | None:
    """從 TWSE.DailyPrice 取得最近一個交易日的日期。

    Returns:
        最近交易日的日期字串（YYYY-MM-DD），若無資料則回傳 None。
    """
    engine = _get_engine("TWSE")
    sql = text("SELECT MAX(Date) AS latest_date FROM TWSE.DailyPrice")

    with engine.connect() as conn:
        result = conn.execute(sql)
        row = result.fetchone()
        if row and row.latest_date:
            return str(row.latest_date)
    return None


@router.get("")
def get_hot_topics(
    query_date: str | None = Query(
        default=None,
        alias="date",
        description="查詢日期，格式 YYYY-MM-DD。未指定時使用最近交易日。",
    ),
) -> dict[str, Any]:
    """取得漲停板與跌停板股票清單。

    合併查詢 TWSE（上市）與 TPEX（上櫃）兩個市場的資料，
    回傳漲幅或跌幅達到 10% 門檻的股票。

    Args:
        query_date: 查詢日期（YYYY-MM-DD），未指定時自動使用最近交易日。

    Returns:
        包含漲停板、跌停板清單及查詢日期的字典。
    """
    try:
        # 若未指定日期，使用最近交易日
        if not query_date:
            query_date = _get_latest_trading_date()
            if not query_date:
                return {
                    "date": None,
                    "limit_up": [],
                    "limit_down": [],
                    "message": "資料庫中無交易資料",
                }

        # 查詢漲停板（TWSE + TPEX）
        limit_up = []
        limit_up.extend(_query_twse_limit_stocks(query_date, "up"))
        limit_up.extend(_query_tpex_limit_stocks(query_date, "up"))
        # 依漲幅降冪排列
        limit_up.sort(key=lambda x: x["change_percent"], reverse=True)

        # 查詢跌停板（TWSE + TPEX）
        limit_down = []
        limit_down.extend(_query_twse_limit_stocks(query_date, "down"))
        limit_down.extend(_query_tpex_limit_stocks(query_date, "down"))
        # 依跌幅（絕對值）降冪排列
        limit_down.sort(key=lambda x: abs(x["change_percent"]), reverse=True)

        logger.info(
            "查詢熱門話題: date=%s, 漲停=%d 檔, 跌停=%d 檔",
            query_date,
            len(limit_up),
            len(limit_down),
        )

        return {
            "date": query_date,
            "limit_up": limit_up,
            "limit_down": limit_down,
        }

    except Exception:
        logger.exception("查詢熱門話題失敗")
        raise HTTPException(status_code=500, detail="查詢漲跌停資料失敗")


@router.get("/dates")
def get_available_dates(
    limit: int = Query(default=30, ge=1, le=365, description="回傳的日期數量"),
) -> list[str]:
    """列出最近有交易資料的日期。

    從 TWSE.DailyPrice 取得最近 N 個交易日。

    Args:
        limit: 回傳的日期數量，預設 30。

    Returns:
        日期字串清單，按日期降冪排列。
    """
    engine = _get_engine("TWSE")

    try:
        sql = text(
            "SELECT DISTINCT Date FROM TWSE.DailyPrice "
            "ORDER BY Date DESC LIMIT :limit"
        )
        with engine.connect() as conn:
            result = conn.execute(sql, {"limit": limit})
            dates = [str(row[0]) for row in result]

        logger.info("查詢可用交易日期: 共 %d 筆", len(dates))
        return dates

    except Exception:
        logger.exception("查詢可用日期失敗")
        raise HTTPException(status_code=500, detail="查詢日期資料失敗")
