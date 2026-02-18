# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口儀表板，提供股票資料視覺化介面。

## 技術架構

- **後端**：FastAPI (Python 3.12)
- **前端**：React + TypeScript + Vite
- **資料庫**：MySQL 8.0
- **容器化**：Docker + Docker Compose

## 專案架構

```
Tw_stock_dashboard/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── main.py             # FastAPI 應用程式入口
│   │   ├── config.py           # 設定檔（環境變數載入）
│   │   ├── api/v1/             # API v1 路由
│   │   ├── models/             # SQLAlchemy 資料庫模型
│   │   ├── schemas/            # Pydantic 資料驗證模型
│   │   ├── services/           # 業務邏輯層
│   │   └── db/                 # 資料庫連線管理
│   ├── requirements.txt
│   └── tests/                  # 單元測試
├── frontend/                   # React + TypeScript + Vite 前端
│   ├── src/
│   │   ├── App.tsx             # 主元件
│   │   ├── components/         # 共用元件
│   │   ├── pages/              # 頁面元件
│   │   └── services/api.ts     # API 呼叫層
│   ├── package.json
│   └── vite.config.ts
├── docker/
│   ├── build.sh                # 建立 Docker images
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yaml     # 服務編排
├── logs/                       # 日誌資料夾
├── run.sh                      # 啟動腳本
├── .env.example                # 環境變數範本
└── README.md
```

## 快速開始

### 前置需求

- [Docker](https://docs.docker.com/get-docker/) 與 Docker Compose

### 啟動服務

```bash
# 1. 複製環境變數範本
cp .env.example .env

# 2. 啟動所有服務
./run.sh
```

### 服務端點

| 服務 | 網址 |
|------|------|
| 後端 API | <http://localhost:8000> |
| API 文件 (Swagger) | <http://localhost:8000/docs> |
| 前端頁面 | <http://localhost:5173> |

### 停止服務

```bash
docker compose -f docker/docker-compose.yaml down
```

## 開發指南

### 建立 Docker Images

```bash
./docker/build.sh
```

### 執行單元測試

```bash
# 在後端容器中執行
docker exec tw-stock-backend pytest tests/ -v
```

### 查看日誌

```bash
# 查看所有服務日誌
docker compose -f docker/docker-compose.yaml logs -f

# 查看特定服務日誌
docker compose -f docker/docker-compose.yaml logs -f backend
```

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
