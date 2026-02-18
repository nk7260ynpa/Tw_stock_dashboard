"""應用程式設定檔，使用 pydantic-settings 載入環境變數。"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用程式設定。"""

    APP_NAME: str = "Tw Stock Dashboard"
    APP_VERSION: str = "0.1.0"

    # 資料庫設定
    DB_HOST: str = "mysql"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "tw_stock_dashboard"

    # CORS 設定
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def database_url(self) -> str:
        """組合資料庫連線字串。"""
        return (
            f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
