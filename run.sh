#!/bin/bash
# 啟動台股儀表板服務

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 確保 logs 資料夾存在
mkdir -p "${SCRIPT_DIR}/logs"

echo "=== 啟動台股儀表板 ==="

# 載入環境變數（如果 .env 存在）
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
  echo "載入 .env 環境變數..."
  set -a
  source "${SCRIPT_DIR}/.env"
  set +a
fi

# 使用 docker compose 啟動服務
docker compose -f "${SCRIPT_DIR}/docker/docker-compose.yaml" \
  --env-file "${SCRIPT_DIR}/.env" \
  up --build -d

echo "=== 服務啟動完成 ==="
echo "後端 API：http://localhost:${BACKEND_PORT:-8001}"
echo "API 文件：http://localhost:${BACKEND_PORT:-8001}/docs"
echo "前端頁面：http://localhost:5173"
echo ""
echo "查看日誌：docker compose -f docker/docker-compose.yaml logs -f"
echo "停止服務：docker compose -f docker/docker-compose.yaml down"
