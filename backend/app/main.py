"""台股儀表板 FastAPI 應用程式入口。"""

import logging
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理。"""
    logger.info("台股儀表板 API 啟動完成")
    yield
    logger.info("台股儀表板 API 正在關閉")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="台股儀表板 API",
    lifespan=lifespan,
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
