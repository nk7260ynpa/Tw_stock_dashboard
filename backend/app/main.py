"""台股儀表板 FastAPI 應用程式入口。"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="台股儀表板 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康檢查端點。"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.on_event("startup")
async def startup_event():
    """應用程式啟動事件。"""
    logger.info("台股儀表板 API 啟動完成")


@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉事件。"""
    logger.info("台股儀表板 API 正在關閉")
