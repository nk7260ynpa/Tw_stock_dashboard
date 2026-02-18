#!/usr/bin/env bash
#
# 啟動主程式的執行腳本。
# 透過 Docker container 執行，並掛載 logs 資料夾。

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly IMAGE_NAME="nk7260ynpa/tw_stock_dashboard"
readonly IMAGE_TAG="latest"
readonly CONTAINER_NAME="tw_stock_dashboard"

# 確保 logs 目錄存在
mkdir -p "${SCRIPT_DIR}/logs"

# 移除已存在的同名容器（若有）
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker rm -f "${CONTAINER_NAME}" > /dev/null 2>&1
fi

echo "啟動 ${CONTAINER_NAME} ..."
echo "開啟瀏覽器前往 http://localhost:8002"

docker run \
  --name "${CONTAINER_NAME}" \
  --network db_network \
  -p 8002:8000 \
  -v "${SCRIPT_DIR}/logs:/app/logs" \
  "${IMAGE_NAME}:${IMAGE_TAG}"
