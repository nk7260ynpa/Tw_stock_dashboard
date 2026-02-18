"""工具 API 路由。

提供工具清單的 RESTful API。
"""

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(prefix="/api/tools", tags=["tools"])

TOOLS_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "tools.json"


def _load_tools() -> list[dict]:
    """從設定檔載入工具清單。

    Returns:
        工具清單。
    """
    with open(TOOLS_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


@router.get("")
def get_tools() -> list[dict]:
    """取得所有已啟用的工具。

    Returns:
        已啟用的工具清單。
    """
    tools = _load_tools()
    return [t for t in tools if t.get("enabled", True)]
