# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口儀表板，提供工具卡片式導覽介面。

## 技術架構

- **後端**：FastAPI (Python 3.12)
- **前端**：React + TypeScript + Vite
- **容器化**：Docker + Docker Compose

## 專案架構

```
Tw_stock_dashboard/
├── backend/                    # FastAPI 後端
│   ├── app/
│   │   ├── main.py             # FastAPI 應用程式入口
│   │   ├── config.py           # 設定檔（環境變數載入）
│   │   └── api/v1/router.py    # API v1 路由（工具清單）
│   ├── requirements.txt
│   ├── pytest.ini
│   └── tests/                  # 單元測試
├── frontend/                   # React + TypeScript + Vite 前端
│   ├── src/
│   │   ├── App.tsx             # 主元件（工具卡片頁面）
│   │   ├── App.css             # 頁面樣式
│   │   ├── index.css           # 全域樣式
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
| 後端 API | <http://localhost:8001> |
| API 文件 (Swagger) | <http://localhost:8001/docs> |
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
docker exec tw-stock-backend pytest tests/ -v
```

### 查看日誌

```bash
docker compose -f docker/docker-compose.yaml logs -f
```

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
