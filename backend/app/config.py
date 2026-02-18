"""應用程式設定檔，使用 pydantic-settings 載入環境變數。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定。"""

    APP_NAME: str = "Tw Stock Dashboard"
    APP_VERSION: str = "0.1.0"

    # CORS 設定
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
