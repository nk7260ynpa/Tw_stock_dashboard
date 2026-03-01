# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口儀表板，提供工具卡片式導覽介面。
點擊卡片可在頁面內以 iframe 嵌入各服務，無需開新分頁。

## 整合服務

| 卡片 | 專案 | Port |
|------|------|------|
| 🌐 台股網頁 | Tw_stock_webpage | 7938 |
| 🗄️ 台股資料庫操作 | Tw_stock_db_operating | 8080 |
| 🔧 台股工具集 | Tw_stock_tools | 8000 |
| 📡 主機資源監控 | Tw_stock_server_monitor (Grafana) | 3000 |
| 📉 台股指標分析 | Tw_stock_indicator | 5001 |

## 技術架構

- **後端**：FastAPI (Python 3.12)，提供 API + 靜態檔案服務
- **前端**：React + Vite，build 後由 FastAPI 提供靜態檔案
- **容器化**：Docker 單一容器（multi-stage build）
- **網路**：加入 `db_network` 外部網路

## 專案架構

```
Tw_stock_dashboard/
├── src/                                # Python 後端
│   └── tw_stock_dashboard/
│       ├── main.py                     # 主程式進入點
│       ├── logger.py                   # 日誌設定
│       ├── config/
│       │   └── tools.json              # 工具清單設定
│       └── web/
│           ├── app.py                  # FastAPI 應用程式
│           └── routers/
│               └── tools.py            # 工具 API 路由
├── frontend/                           # React 前端
│   ├── src/
│   │   ├── App.jsx                     # 主元件（含 iframe 嵌入）
│   │   ├── App.css
│   │   ├── index.css
│   │   └── components/
│   │       ├── LaunchPad.jsx           # 工具網格容器
│   │       ├── LaunchPad.css
│   │       ├── ToolCard.jsx            # 工具卡片元件
│   │       └── ToolCard.css
│   ├── package.json
│   └── vite.config.js
├── tests/                              # 單元測試
├── docker/
│   ├── build.sh                        # 建立 Docker image
│   ├── Dockerfile                      # Multi-stage Dockerfile
│   └── docker-compose.yaml
├── logs/                               # 日誌資料夾
├── pyproject.toml                      # Python 套件定義 (PEP 621)
├── requirements.txt                    # Python 釘版依賴（Docker 環境）
├── run.sh                              # 啟動腳本
└── README.md
```

## 快速開始

### 前置需求

- [Docker](https://docs.docker.com/get-docker/)
- `db_network` Docker 網路已建立

### 建立與啟動

```bash
# 1. 建立 Docker image
./docker/build.sh

# 2. 啟動服務
./run.sh
```

### 服務端點

| 服務 | 網址 |
|------|------|
| 台股儀表板 | <http://localhost:8002> |

### 停止服務

```bash
docker rm -f tw_stock_dashboard
```

## 開發指南

### 新增工具卡片

編輯 `src/tw_stock_dashboard/config/tools.json`，新增項目後重建 Docker image 即可。

### 執行單元測試

```bash
docker run --rm \
  -v "$(pwd)/src:/app/src" \
  -v "$(pwd)/tests:/app/tests" \
  nk7260ynpa/tw_stock_dashboard:latest \
  pytest tests/ -v
```

### 查看日誌

```bash
cat logs/tw_stock_dashboard.log
```

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
