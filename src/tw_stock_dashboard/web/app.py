"""FastAPI 應用程式。

提供 API 端點與前端靜態檔案服務。
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from tw_stock_dashboard.web.routers.tools import router as tools_router

app = FastAPI(title="台股儀表板", version="0.1.0")

# 註冊 API 路由
app.include_router(tools_router)

# 前端靜態檔案（React 建置產出）
STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    # 掛載靜態資源（CSS、JS 等）
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """處理所有非 API 路徑，回傳 index.html 供 React Router 處理。"""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
