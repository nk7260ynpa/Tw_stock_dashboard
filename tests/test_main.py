"""主程式基礎測試。"""

from tw_stock_dashboard.main import main


def test_main_exists():
    """確認 main 函式存在且可呼叫。"""
    assert callable(main)
