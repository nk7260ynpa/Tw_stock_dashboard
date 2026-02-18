"""API v1 路由註冊。"""

from fastapi import APIRouter

api_v1_router = APIRouter()


@api_v1_router.get("/status")
async def api_status():
    """API v1 狀態檢查。"""
    return {"api_version": "v1", "status": "ok"}
