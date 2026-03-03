# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口儀表板，提供工具卡片式導覽介面。
點擊卡片可在頁面內以 iframe 嵌入各服務，無需開新分頁。
另外提供「熱門話題」頁面，顯示今日漲停板與跌停板股票。

## 整合服務

| 卡片 | 專案 | Port |
|------|------|------|
| 台股網頁 | Tw_stock_webpage | 7938 |
| 台股資料庫操作 | Tw_stock_db_operating | 8080 |
| 台股工具集 | Tw_stock_tools | 8000 |
| 主機資源監控 | Tw_stock_server_monitor (Grafana) | 3000 |
| 台股指標分析 | Tw_stock_indicator | 5001 |
| 台股新聞 | Tw_stock_news | 8003 |

## 技術架構

- **後端**：FastAPI (Python 3.12)，提供 API + 靜態檔案服務
- **前端**：React + Vite + React Router，build 後由 FastAPI 提供靜態檔案
- **資料庫**：MySQL（TWSE、TPEX 資料庫的 DailyPrice 和 StockName 表）
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
│               ├── tools.py            # 工具 API 路由
│               └── hot_topics.py       # 熱門話題 API 路由（漲跌停）
├── frontend/                           # React 前端
│   ├── src/
│   │   ├── App.jsx                     # 主元件（路由 + iframe 嵌入）
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── main.jsx                    # React 進入點
│   │   └── components/
│   │       ├── LaunchPad.jsx           # 工具網格容器
│   │       ├── LaunchPad.css
│   │       ├── ToolCard.jsx            # 工具卡片元件
│   │       ├── ToolCard.css
│   │       ├── HotTopics.jsx           # 熱門話題頁面（漲跌停板）
│   │       └── HotTopics.css
│   ├── package.json
│   └── vite.config.js
├── tests/                              # 單元測試
│   ├── test_api.py                     # 工具 API 測試
│   ├── test_hot_topics.py              # 熱門話題 API 測試
│   └── test_main.py                    # 主程式測試
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

## 頁面與 API

### 前端頁面

| 路徑 | 功能 |
|------|------|
| `/` | LaunchPad 工具卡片首頁 |
| `/hot-topics` | 熱門話題 — 漲停板與跌停板 |

### API 端點

| Endpoint | 方法 | 功能 |
|----------|------|------|
| `/api/tools` | GET | 取得已啟用的工具清單 |
| `/api/hot-topics` | GET | 取得漲停/跌停股票（`?date=YYYY-MM-DD`） |
| `/api/hot-topics/dates` | GET | 列出最近有交易的日期（`?limit=30`） |

## 快速開始

### 前置需求

- [Docker](https://docs.docker.com/get-docker/)
- `db_network` Docker 網路已建立
- MySQL 資料庫服務運行中（漲跌停功能需要 TWSE、TPEX 資料庫）

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
| 熱門話題 | <http://localhost:8002/hot-topics> |

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

## CI/CD

本專案使用 GitHub Actions 自動建置並推送 Docker image 至 DockerHub。

### 觸發條件

推送符合 `v*.*.*` 格式的 tag 時自動觸發，例如：

```bash
git tag v1.0.0
git push origin v1.0.0
```

### 自動化流程

1. Checkout 原始碼
2. 從 tag 擷取版本號
3. 登入 DockerHub（使用 repository secrets）
4. 建置 Docker image（multi-stage build）
5. 推送版本號 tag 與 `latest` tag 至 DockerHub

### 必要 Secrets

在 GitHub repository 的 Settings > Secrets and variables > Actions 中設定：

| Secret | 說明 |
|--------|------|
| `DOCKER_USERNAME` | DockerHub 帳號 |
| `DOCKER_PASSWORD` | DockerHub 密碼或 Access Token |

### 版本紀錄

| 版本 | 說明 |
|------|------|
| v1.0.0 | 初始版本 — LaunchPad 工具卡片、熱門話題頁面 |

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
