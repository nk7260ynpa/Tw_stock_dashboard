# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口儀表板，提供工具卡片式導覽介面。

## 技術架構

- **後端**：FastAPI (Python 3.12)
- **前端**：React + Vite
- **容器化**：Docker（單一容器，multi-stage build）

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
│   │   ├── App.jsx                     # 主元件
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
├── requirements.txt                    # Python 依賴
├── run.sh                              # 啟動腳本
└── README.md
```

## 快速開始

### 前置需求

- [Docker](https://docs.docker.com/get-docker/)

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

### 執行單元測試

```bash
docker run --rm \
  -v "$(pwd)/src:/app/src" \
  -v "$(pwd)/tests:/app/tests" \
  -e PYTHONPATH=/app/src \
  nk7260ynpa/tw_stock_dashboard:latest \
  pytest tests/ -v
```

### 查看日誌

```bash
cat logs/tw_stock_dashboard.log
```

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
