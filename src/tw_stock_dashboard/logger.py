"""日誌設定模組。

提供統一的 logging 設定，將日誌同時輸出至終端與檔案。
"""

import logging
from pathlib import Path


def setup_logger(
    name: str = "tw_stock_dashboard",
    log_level: int = logging.INFO,
) -> logging.Logger:
    """建立並設定 logger。

    Args:
        name: Logger 名稱。
        log_level: 日誌等級，預設為 INFO。

    Returns:
        設定完成的 Logger 實例。
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 避免重複新增 handler
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 終端輸出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 檔案輸出
    log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tw_stock_dashboard.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
