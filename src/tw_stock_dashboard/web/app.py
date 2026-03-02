"""FastAPI 應用程式。

提供 API 端點與前端靜態檔案服務。
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from tw_stock_dashboard.web.routers.hot_topics import router as hot_topics_router
from tw_stock_dashboard.web.routers.tools import router as tools_router

logger = logging.getLogger(__name__)

app = FastAPI(title="台股儀表板", version="0.1.0")

# 註冊 API 路由
app.include_router(tools_router)
app.include_router(hot_topics_router)

# 前端靜態檔案（React 建置產出）
# 因套件安裝後 __file__ 指向 site-packages，無法用相對路徑定位
# 優先使用環境變數，再嘗試常見路徑
_static_candidates = [
    os.environ.get("STATIC_DIR", ""),
    "/app/frontend/dist",  # Docker 容器內路徑
    str(Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"),
]
STATIC_DIR: Path | None = None
for _candidate in _static_candidates:
    if _candidate and Path(_candidate).is_dir():
        STATIC_DIR = Path(_candidate)
        break

if STATIC_DIR is not None:
    logger.info("靜態檔案目錄: %s", STATIC_DIR)
    # 掛載靜態資源（CSS、JS 等）
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """處理所有非 API 路徑，回傳 index.html 供 React Router 處理。"""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    logger.warning("找不到前端靜態檔案目錄，嘗試路徑: %s", _static_candidates)
