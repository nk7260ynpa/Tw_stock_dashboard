#!/bin/bash
# 建立台股儀表板 Docker images

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "${SCRIPT_DIR}")"

echo "=== 建立台股儀表板 Docker Images ==="

echo "[1/2] 建立後端 image..."
docker build \
  -t tw-stock-backend:latest \
  -f "${SCRIPT_DIR}/Dockerfile.backend" \
  "${PROJECT_ROOT}"

echo "[2/2] 建立前端 image..."
docker build \
  -t tw-stock-frontend:latest \
  -f "${SCRIPT_DIR}/Dockerfile.frontend" \
  "${PROJECT_ROOT}"

echo "=== Docker Images 建立完成 ==="
docker images | grep tw-stock
