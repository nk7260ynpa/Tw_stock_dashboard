# 台股儀表板 (Tw Stock Dashboard)

整合現有台股專案的統一入口 LaunchPad，提供工具卡片式導覽介面。點擊卡片可在頁面內以
iframe 嵌入各服務，無需開新分頁。

本專案同時擔任**反向代理（reverse proxy）閘道**：把瀏覽器對 `/app/<service>/*` 的請求，
轉發到 `db_network` 內部的各子服務容器。如此整個平台只需對外公開儀表板一個 port（8002），
其餘子服務皆不必各自對外曝露。本專案本身**不持有任何業務資料，也沒有資料庫連線**。

## 整合服務

工具卡片清單由 `src/tw_stock_dashboard/config/tools.json` 定義；反向代理目標由
`src/tw_stock_dashboard/web/routers/proxy.py` 的 `SERVICE_MAP` 定義。兩者需同步維護。

| 卡片 | 子服務 ID | 代理目標（`db_network` 容器:port） | 卡片連結 |
|------|-----------|-----------------------------------|----------|
| 熱門話題 | `hot` | `tw_stock_hot:5050` | `/app/hot/` |
| 台股網頁 | `webpage` | `tw-stock-webpage:8000` | `/app/webpage/` |
| 台股資料庫操作 | `db-operating` | `tw_stock_db_operating:8080` | `/app/db-operating/` |
| 台股工具集 | `tools` | `tw_stock_tools:8000` | `/app/tools/` |
| 台股指標分析 | `indicator` | `tw-stock-indicator:5001` | `/app/indicator/` |
| 台股 ML 預測分析 | `ml` | `tw-stock-ml:5002` | `/app/ml/` |
| 台股新聞 | `news` | `tw_stock_news:8003` | `/app/news/` |
| 特殊資訊 Dashboard | `specialinfo` | `tw-stock-specialinfo:5055` | `/app/specialinfo/` |
| 主機資源監控 | — | Grafana（不經代理） | `http://localhost:3000/...` |

> 註：主機資源監控（Grafana）卡片直接連到 `http://localhost:3000`，不經反向代理。
> 各子服務的容器命名規則不一致（有底線 `tw_stock_*`，也有連字號 `tw-stock-*`），
> `SERVICE_MAP` 須與該子專案實際容器名相符。

## 技術架構

- **後端**：FastAPI（Python 3.12），提供工具 API、反向代理與前端靜態檔案服務。
- **反向代理**：以 `httpx.AsyncClient` 串流轉發 request/response，無資料庫連線。
- **前端**：React 18 + Vite，build 後由 FastAPI 提供靜態檔案（SPA）。
- **容器化**：Docker 單一容器（multi-stage build，先 build 前端再裝 Python 後端）。
- **網路**：加入外部 Docker 網路 `db_network`，以容器名與各子服務互通。
- **依賴**：`fastapi`、`uvicorn`、`httpx`（無資料庫驅動）。

## 專案架構

```
Tw_stock_dashboard/
├── src/                                # Python 後端
│   └── tw_stock_dashboard/
│       ├── main.py                     # 主程式進入點（啟動 uvicorn）
│       ├── logger.py                   # 日誌設定
│       ├── config/
│       │   └── tools.json              # 工具卡片清單設定
│       └── web/
│           ├── app.py                  # FastAPI 應用程式（路由註冊 + SPA 靜態檔）
│           └── routers/
│               ├── tools.py            # 工具清單 API 路由（/api/tools）
│               └── proxy.py            # 反向代理路由（/app/<service>/...）
├── frontend/                           # React 前端
│   ├── src/
│   │   ├── App.jsx                     # 主元件（卡片首頁 + iframe 內嵌）
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── main.jsx                    # React 進入點
│   │   └── components/
│   │       ├── LaunchPad.jsx           # 工具網格容器
│   │       ├── LaunchPad.css
│   │       ├── ToolCard.jsx            # 工具卡片元件
│   │       └── ToolCard.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js                  # Vite 設定（dev server 代理 /api → :8000）
├── tests/                              # 單元測試
│   ├── test_api.py                     # 工具 API 測試
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

## 架構說明

### 啟動鏈

`docker/Dockerfile` 的 `CMD` → `python -m tw_stock_dashboard.main` → `uvicorn` 啟動
`tw_stock_dashboard.web.app:app`（host `0.0.0.0`、容器內 port `8000`）。對外 port 映射在
`run.sh` / `docker-compose.yaml` 完成（`127.0.0.1:8002 -> 8000`）。

### 路由註冊順序（`web/app.py`）

`app.py` 依序註冊三類路由，順序至關重要：

1. `tools_router` — `/api/tools`，回傳工具卡片清單。
2. `proxy_router` — `/app/<service>/...`，反向代理至各子服務。
3. SPA catch-all `GET /{full_path:path}` — 回傳 React `index.html`。

catch-all 會吞掉所有未匹配路徑，因此**反向代理路由必須在它之前註冊**，否則會被
SPA 攔截。新增任何後端路由時都要排在 catch-all 之前。

### 反向代理（`web/routers/proxy.py`）

- `SERVICE_MAP` 把服務 ID 對應到 `db_network` 內部 DNS 名稱與 port。**新增子服務時，
  須同時修改此處與 `config/tools.json`**。
- 共享一個 `httpx.AsyncClient`（lazy 建立、FastAPI `shutdown` 事件時關閉），以串流方式
  轉發 request/response body。
- 過濾 hop-by-hop headers，以及 `content-encoding`／`content-length`（httpx 會自動解壓）；
  並改寫 3xx 回應的 `Location`，加回 `/app/<service>` 前綴，使子服務的相對跳轉在代理下
  仍正確。
- 採 `follow_redirects=False`，redirect 交由瀏覽器處理（搭配 Location 改寫）。
- 未知服務回傳 404，目標服務無法連線時回傳 502。

### 靜態檔定位

套件安裝後 `__file__` 指向 site-packages，無法用相對路徑定位前端 `dist`。`app.py` 依序嘗試
`STATIC_DIR` 環境變數 → `/app/frontend/dist`（容器內路徑，由 Dockerfile 從 frontend-builder
階段複製）→ 專案相對路徑。

### 工具卡片資料流

`config/tools.json`（陣列，每筆含 `id`／`name`／`description`／`icon`／`url`／`enabled`）
→ `/api/tools` 只回傳 `enabled` 為真的項目 → 前端 `App.jsx` fetch 後渲染 `LaunchPad` →
`ToolCard`。點擊卡片不開新分頁，而是在頁面內以 `<iframe>` 內嵌（url 帶 `?t=timestamp`
破快取）。卡片的 `url` 多為代理路徑 `/app/<service>/`；server-monitor（Grafana）例外，
直連 `http://localhost:3000`。`tools.json` 已宣告於 `pyproject.toml` 的 `package-data`，
新增卡片後須重建 image 才會生效。

## API 端點

| Endpoint | 方法 | 功能 |
|----------|------|------|
| `/api/tools` | GET | 取得已啟用（`enabled` 為真）的工具卡片清單 |
| `/app/<service>/<path>` | 任意 | 反向代理至 `SERVICE_MAP` 對應的子服務 |
| `/{full_path:path}` | GET | SPA catch-all，回傳 React `index.html` |

## 快速開始

所有 Python 都在 Docker container 內執行，本機不需 Python 環境。

### 前置需求

- [Docker](https://docs.docker.com/get-docker/)
- 外部 Docker 網路 `db_network` 已建立（各子服務皆掛載於此網路）。
- 欲透過卡片開啟的子服務容器已啟動（否則該卡片代理會回傳 502）。

### 建立與啟動

```bash
# 1. 建立 Docker image（multi-stage：先 build 前端，再裝 Python 後端）
./docker/build.sh

# 2. 啟動服務（移除舊容器 → 以 restart=always 重啟，掛載 logs，加入 db_network）
./run.sh
```

亦可改用 docker-compose（會自動 build）：

```bash
docker compose -f docker/docker-compose.yaml up -d --build
```

### 服務端點

| 服務 | 網址 |
|------|------|
| 台股儀表板 | <http://localhost:8002> |

> 對外僅綁定 `127.0.0.1:8002`（容器內 port 8000）。各子服務不對外曝露，
> 一律經由 `/app/<service>/` 代理存取。

### 停止服務

```bash
docker rm -f tw_stock_dashboard
```

## 開發指南

### 新增工具卡片

1. 編輯 `src/tw_stock_dashboard/config/tools.json`，新增卡片項目。
2. 若新卡片需經反向代理，於 `src/tw_stock_dashboard/web/routers/proxy.py` 的
   `SERVICE_MAP` 加入對應的容器名與 port。
3. 重建 Docker image 後生效。

### 執行單元測試

測試使用 FastAPI `TestClient`，直接 import `tw_stock_dashboard.web.app:app`，不需啟動容器網路。

```bash
docker run --rm \
  -v "$(pwd)/src:/app/src" \
  -v "$(pwd)/tests:/app/tests" \
  nk7260ynpa/tw_stock_dashboard:latest \
  pytest tests/ -v
```

### 前端開發（在容器外用 Node 直接開發時）

```bash
cd frontend
npm install
npm run dev      # Vite dev server :5173，已設定 proxy 把 /api 轉到 localhost:8000
npm run build    # 產出 dist/，正式環境由 FastAPI 提供靜態檔
```

### 查看日誌

```bash
cat logs/tw_stock_dashboard.log
```

## CI/CD

本專案有兩條管線並存，皆由推送符合 `v*.*.*` 格式的 tag 觸發建置。

### GitHub Actions（DockerHub）

`.github/workflows/docker-publish.yml`：建置後推送
`nk7260ynpa/tw_stock_dashboard:<版本號>` 與 `:latest` 至 DockerHub。

觸發範例：

```bash
git tag v1.0.0
git push origin v1.0.0
```

必要的 repository secrets（Settings > Secrets and variables > Actions）：

| Secret | 說明 |
|--------|------|
| `DOCKER_USERNAME` | DockerHub 帳號 |
| `DOCKER_PASSWORD` | DockerHub 密碼或 Access Token |

### GitLab Flow（Harbor 自架）

`.gitlab-ci.yml` 在自架 GitLab 上實作 GitLab Flow，將建置、升版、部署串成完整流程，
最終把 image 推送至 Harbor 並自動部署。

| 階段 | 觸發條件 | 行為 |
|------|----------|------|
| `build` | 於 `main` 推送 `v*.*.*` tag | 建置 image，推送 `<版本號>` 與 `latest` 至 Harbor |
| `promote` | 推送 `production` 分支 | 將 Harbor 的 `latest` 重新打上 `production` 標籤推回 |
| `deploy` | 推送 `production` 分支 | 拉取 `production` image，重啟 `tw_stock_dashboard` 容器 |

典型流程：在 `main` 開發並打版本 tag（產生 `latest`）→ 將 `main` 合併進 `production`
分支 → `promote` 升版、`deploy` 自動部署上線。

必要的 Runner 環境變數（由 GitLab Runner 注入，未進版控）：

| 變數 | 說明 |
|------|------|
| `HARBOR_USERNAME` | Harbor 帳號 |
| `HARBOR_PASSWORD` | Harbor 密碼 |
| `HARBOR_REGISTRY` | Harbor registry 位址（例：`127.0.0.1:8081`） |

## 授權條款

本專案採用 MIT 授權條款，詳見 [LICENSE](LICENSE) 檔案。
