"""API v1 路由註冊。"""

from fastapi import APIRouter

api_v1_router = APIRouter()

# 儀表板工具清單
DASHBOARD_TOOLS = [
    {
        "id": "tw-stock-tools",
        "name": "台股工具集",
        "description": "股票獲利計算機、股利計算機等實用工具",
        "icon": "🔧",
    },
    {
        "id": "tw-stock-analysis",
        "name": "台股分析",
        "description": "技術分析、基本面分析等股票分析工具",
        "icon": "📊",
    },
    {
        "id": "tw-stock-monitor",
        "name": "股價監控",
        "description": "即時股價追蹤與自訂警示通知",
        "icon": "📈",
    },
    {
        "id": "tw-stock-news",
        "name": "市場資訊",
        "description": "台股新聞、公告與市場動態彙整",
        "icon": "📰",
    },
]


@api_v1_router.get("/status")
async def api_status():
    """API v1 狀態檢查。"""
    return {"api_version": "v1", "status": "ok"}


@api_v1_router.get("/tools")
async def get_tools():
    """取得儀表板工具清單。"""
    return {"tools": DASHBOARD_TOOLS}
