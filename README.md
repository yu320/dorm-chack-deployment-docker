# 學生宿舍查核與管理系統 (Student Dormitory Inspection System)

這是一個現代化的宿舍管理平台，結合 FastAPI 後端與 Nuxt 3 前端，並可使用 Docker 進行本地開發或生產部署。

## 目錄 (Table of Contents)

- [快速開始](#快速開始)
- [開發環境](#開發環境)
- [部屬 (Production)](#部屬-production)
- [CI/CD](#cicd)
- [目錄結構](#目錄結構)
- [授權](#授權)

---

## 快速開始

以下說明涵蓋常見的本地開發與容器化部署流程；範例同時提供 PowerShell (Windows) 與 macOS/Linux 指令。

### 前置需求

- Python 3.11+
- Node.js 18+
- Docker (選用，用於啟動 MySQL 或整體服務)

### 本地開發（建議流程）

1) 啟動本地資料庫（選用 Docker）

```powershell
# 在專案根目錄啟動 db 以及 phpMyAdmin
docker compose up -d db phpmyadmin
```

2) 後端（在 `backend` 目錄）

```powershell
cd backend
python -m venv .venv
# PowerShell 啟用虛擬環境
. .venv\Scripts\Activate.ps1
# 若使用 cmd.exe: .venv\Scripts\activate.bat
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt

# 複製並編輯環境設定檔 (.env)
# PowerShell:
Copy-Item .env.example .env -ErrorAction Ignore
# macOS/Linux:
# cp .env.example .env

# 啟動開發伺服器
uvicorn main:app --reload
```

後端預設監聽 `http://127.0.0.1:8000`。

3) 前端（在 `frontend` 目錄）

```powershell
cd frontend
npm install
npm run dev
```

前端預設在 `http://localhost:3000`。

---

## 開發環境說明

- 後端使用 FastAPI、SQLAlchemy (async) 與 Alembic 做資料庫遷移。
- 前端以 Nuxt 3 + Tailwind CSS 開發。
- `backend/requirements.txt` 列出後端依賴。

若需要快速在容器中啟動整個開發環境，可以使用 `docker compose up --build`（根目錄）。

---

## 部屬 (Production)

此專案包含 `docker-compose.prod.yml` 範例，可在生產主機上使用 Docker Compose 啟動。

部署步驟（概覽）

1. 將 `docker-compose.prod.yml` 與 `backend/.env` 上傳至伺服器，並在 `.env` 中設定生產用的機密（例如 `SECRET_KEY`、資料庫密碼）。
2. 登入 GitHub Container Registry（若使用 GHCR）：

```powershell
docker login ghcr.io -u <GitHub帳號> -p <GitHub_Token>
```

3. 在伺服器上拉取並啟動服務：

```powershell
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

生產環境的 phpMyAdmin 會依 `docker-compose.prod.yml` 設定提供存取（若有啟用）。

---

## CI/CD

本專案已配置 GitHub Actions（位於 `.github/workflows/`），在 push 到 `main` 時會自動建立並推送影像到 GHCR（如已設定）。

---

## 目錄結構 (簡要)

```
.
├── backend/
├── frontend/
├── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
└── .github/workflows/
```

---

## 授權

本專案採用 MIT License。

---

若你要我把這個更新 commit 並推到 `origin/main`，或需要我做其他內容（加入徽章、更多使用範例或把 Windows 例子改為 CMD），請告訴我。

## 🌟 核心功能 (Core Features)

### 1. 查核管理 (Inspection Management)
*   **數位化評分**: 捨棄紙本，管理員可透過平板或手機直接進行宿舍評分。
*   **照片上傳**: 支援即時拍照或上傳照片作為查核佐證。
*   **自動扣分計算**: 根據預設規則自動計算扣分，減少人為計算錯誤。
*   **歷史紀錄**: 完整保存每次查核的詳細紀錄，方便隨時調閱。

### 2. 學生與住宿生管理 (Student & Resident Management)
*   **批次匯入**: 支援 Excel/CSV 格式批次匯入學生資料。
*   **房號分配**: 視覺化管理床位與房號分配。
*   **學號綁定**: 自動關聯學號與 Email，方便通知發送。

### 3. 報表與通知 (Reports & Notifications)
*   **PDF 報告生成**: 一鍵生成精美的查核結果 PDF 報告，包含照片與評語。
*   **Email 通知**: 查核完成後自動發送 Email 通知學生與相關人員。

### 4. 系統管理 (System Administration)
*   **權限控管**: 區分超級管理員、一般管理員與檢視者權限。
*   **資料備份**: 支援資料庫與上傳檔案的備份與還原。
*   **操作軌跡 (Audit Log)**: 記錄所有關鍵操作，提升系統安全性。

---

## 🛠️ 技術棧 (Tech Stack)

### Backend (後端)
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) - 高效能、易於開發的非同步 Web 框架。
*   **Database**: MySQL 8.0 (生產環境) / SQLite (本地開發測試)。
*   **ORM**: SQLAlchemy (Async) - 現代化的資料庫操作工具。
*   **Migration**: Alembic - 資料庫版本控制。
*   **Tools**: Pydantic (資料驗證), Jose (JWT 認證), ReportLab (PDF 生成)。

### Frontend (前端)
*   **Framework**: [Nuxt 3](https://nuxt.com/) (Vue 3) - 強大的全端 Vue 框架。
*   **UI Library**: Tailwind CSS - 原子化 CSS 框架，打造現代化介面。
*   **State Management**: Pinia - 輕量級狀態管理庫。
*   **Charts**: Chart.js / Vue-Chartjs - 數據視覺化圖表。
*   **PWA**: 支援漸進式網頁應用 (Progressive Web App)，可安裝於行動裝置。

### DevOps & Deployment
*   **Containerization**: Docker & Docker Compose。
*   **Web Server**: Nginx (反向代理)。
*   **CI/CD**: GitHub Actions (自動建置 Docker Image 並推送到 GHCR)。
*   **Management**: phpMyAdmin (資料庫管理介面)。

---

## ⚙️ 設定說明 (Configuration)

系統透過環境變數 (Environment Variables) 進行設定，主要設定檔位於 `backend/.env`。請參考 `backend/.env.example` 建立您的設定檔。

### 關鍵變數 (Critical)

| 變數名稱 | 說明 | 範例值 |
| :--- | :--- | :--- |
| `SQLALCHEMY_DATABASE_URL` | 資料庫連線字串 (支援 MySQL 與 SQLite) | `mysql+aiomysql://user:pass@db/app_db` |
| `SECRET_KEY` | **[重要]** 用於加密 Token 的密鑰，生產環境請務必更換 | `generate-a-long-random-string` |
| `ALGORITHM` | JWT 加密演算法 | `HS256` |
| `DEBUG` | 除錯模式 (生產環境請設為 False) | `True` / `False` |

### 初始管理員 (First Superuser)
系統初次啟動時會自動建立此管理員帳號。

| 變數名稱 | 說明 | 範例值 |
| :--- | :--- | :--- |
| `FIRST_SUPERUSER` | 管理員 Email | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | 管理員密碼 | `admin` |

### 郵件設定 (Email Settings)
用於發送通知信與重設密碼信。

| 變數名稱 | 說明 |
| :--- | :--- |
| `MAIL_USERNAME` | SMTP 帳號 (Email) |
| `MAIL_PASSWORD` | SMTP 密碼 (應用程式密碼) |
| `MAIL_FROM` | 寄件者 Email |
| `MAIL_PORT` | SMTP Port (通常為 587 或 465) |
| `MAIL_SERVER` | SMTP 伺服器 (如 `smtp.gmail.com`) |
| `MAIL_TLS` | 是否啟用 TLS (True/False) |
| `MAIL_SSL` | 是否啟用 SSL (True/False) |

### 檔案上傳與 API (File & API)

| 變數名稱 | 說明 | 範例值 |
| :--- | :--- | :--- |
| `UPLOAD_DIR` | 圖片上傳存放路徑 | `uploads` |
| `API_BASE_URL` | 後端 API 的基礎網址 | `http://localhost:8000` |
| `BACKEND_CORS_ORIGINS` | 允許跨域請求的來源 (JSON List) | `["http://localhost:3000", "https://yourdomain.com"]` |

### 設定範例 (Configuration Examples)

**本地開發環境 (Local Development)**
建立 `backend/.env`：
```ini
SQLALCHEMY_DATABASE_URL=mysql+aiomysql://dev_user:dev_password@localhost:3306/app_db
SECRET_KEY=development_secret_key
ALGORITHM=HS256
DEBUG=True
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin
# 郵件與其他設定可留空或視需求填寫
UPLOAD_DIR=uploads
API_BASE_URL=http://localhost:8000
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost", "http://127.0.0.1"]
```

**生產環境 (Production Environment)**
建立 `backend/.env`：
```ini
# 注意：db 是 docker-compose 中的服務名稱
SQLALCHEMY_DATABASE_URL=mysql+aiomysql://prod_user:YOUR_SECURE_PROD_PASSWORD@db/app_db
# 務必使用強隨機字串
SECRET_KEY=CHANGE_THIS_TO_A_VERY_LONG_RANDOM_STRING
ALGORITHM=HS256
DEBUG=False
FIRST_SUPERUSER=admin@yourdomain.com
FIRST_SUPERUSER_PASSWORD=YOUR_SECURE_ADMIN_PASSWORD
# 填寫真實的 SMTP 資訊以啟用郵件功能
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=no-reply@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
UPLOAD_DIR=uploads
API_BASE_URL=https://yourdomain.com
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

---

## 🚀 快速開始 (Quick Start)

### 1. 本地開發 (Local Development)

這種模式適合開發者進行程式碼修改與除錯。

#### 前置需求
*   Python 3.11+
*   Node.js 18+
*   Docker (選用，用於跑 MySQL)

#### 步驟
1.  **啟動資料庫 (MySQL)**:
    ```bash
    docker compose up -d db phpmyadmin
    ```
    *這會啟動一個本地的 MySQL 服務 (Port 3306) 和 phpMyAdmin (Port 8080)。*

2.  **設定後端**:
    ```bash
    cd backend
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    
    pip install -r requirements.txt
    
    # 複製設定檔
    cp .env.example .env
    # 編輯 .env，確保 SQLALCHEMY_DATABASE_URL 指向 localhost
    
    # 啟動伺服器
    uvicorn main:app --reload
    ```

3.  **設定前端**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    *瀏覽器打開 http://localhost:3000 即可看到畫面。*

---

### 2. 伺服器部署 (Production Deployment)

這種模式適合在 Linux 伺服器 (VPS) 上運行正式服務。

#### 前置需求
*   一台安裝好 Docker 與 Docker Compose 的伺服器。

#### 步驟
1.  **準備檔案**:
    將 `docker-compose.prod.yml` 與 `backend/.env` 上傳至伺服器。

2.  **設定環境變數**:
    *   修改 `.env`: 設定強密碼的 `SECRET_KEY`，將 `DEBUG` 設為 `False`。
    *   修改 `docker-compose.prod.yml`: 修改 `MYSQL_PASSWORD` 與 `MYSQL_ROOT_PASSWORD` 為強密碼。

3.  **登入 GitHub Registry**:
    ```bash
    docker login ghcr.io -u <GitHub帳號> -p <GitHub_Token>
    ```

4.  **啟動服務**:
    ```bash
    # 拉取最新映像檔
    docker compose -f docker-compose.prod.yml pull
    
    # 啟動容器
    docker compose -f docker-compose.prod.yml up -d
    ```

5.  **訪問網站**:
    *   網站首頁: `http://<Server-IP>`
    *   phpMyAdmin: `http://<Server-IP>/sys_db_admin_x9zp2/`

---

## 🔄 CI/CD 流程

本專案已設定 GitHub Actions 自動化流程 (`.github/workflows/docker-publish.yml`)。

1.  **觸發條件**: 當程式碼 Push 到 `main` 分支時。
2.  **執行動作**:
    *   自動建立 Frontend、Backend 與 Nginx 的 Docker Image。
    *   自動將 Image 推送到 GitHub Container Registry (GHCR)。
3.  **部署**: 伺服器端只需執行 `docker compose pull` 即可更新到最新版。

## 🔄 CI/CD 流程

本專案已設定 GitHub Actions 自動化流程 (`.github/workflows/docker-publish.yml`)。

1.  **觸發條件**: 當程式碼 Push 到 `main` 分支時。
2.  **執行動作**:
    *   自動建立 Frontend、Backend 與 Nginx 的 Docker Image。
    *   自動將 Image 推送到 GitHub Container Registry (GHCR)。
3.  **部署**: 伺服器端只需執行 `docker compose pull` 即可更新到最新版。

---

## 💡 開發與部署注意事項 (Development & Deployment Notes)

### 前端 API 代理機制 (Frontend API Proxy)

在您的開發與部署流程中，前端對後端 API 的請求代理方式會有所不同：

1.  **本地開發環境 (`npm run dev`)**:
    *   **代理者**: 由 `Nuxt` 內建的 `Vite` 開發伺服器負責代理。
    *   **設定位置**: `frontend/nuxt.config.ts` 中的 `vite.server.proxy`。
    *   **運作方式**: 當瀏覽器發送 `/api` 開頭的請求時，`Vite` 會將其轉發到 `http://localhost:8000` (您的本地後端服務)。
    *   **您的前端程式碼**: 會對 `相對路徑` (例如 `/api/v1/login`) 發出請求，因為 `frontend/nuxt.config.ts` 中的 `runtimeConfig.public.apiBase` 通常會設為空字串 `''`。

2.  **生產部署環境 (Docker)**:
    *   **代理者**: 由 `Nginx` 負責代理。
    *   **設定位置**: `nginx/default.conf`。
    *   **運作方式**: 部署後，使用者瀏覽器發出的 `/api` 開頭的請求會先抵達 `Nginx`，`Nginx` 再根據 `default.conf` 的規則 (例如 `location /api/v1/`) 將其轉發到 `backend` 容器。
    *   **總結**: 由於前後端的 API 請求都使用相對路徑或由 Nginx 處理路徑重寫，您無需在程式碼中針對開發或生產環境手動調整 API 請求基礎路徑。Nginx 與 Vite 代理機制無縫銜接。

### `API_BASE_URL` 的用途

*   **位於**: `backend/.env`
*   **用途**: 這個變數主要用於後端**生成絕對 URL**。例如，當後端需要發送 Email (如密碼重設連結、驗證連結) 給使用者時，它需要知道系統對外的公開網址，才能產生一個完整的、可點擊的連結 (例如 `https://yourdomain.com/reset-password?token=XYZ`)。
*   **建議設定**:
    *   **本地開發**: `http://localhost:8000` (或前端開發伺服器 `http://localhost:3000`，取決於連結應指向哪裡)。
    *   **生產環境**: `https://yourdomain.com` (您的網站公開網址，務必使用 HTTPS)。

---

## 📂 目錄結構 (Directory Structure)

```
.
├── backend/                # FastAPI 後端程式碼
│   ├── app/                # 核心應用邏輯 (Models, APIs, CRUD)
│   ├── alembic/            # 資料庫遷移腳本
│   ├── uploads/            # 使用者上傳的圖片 (掛載 Volume)
│   └── Dockerfile          # 後端 Docker 建置檔
├── frontend/               # Nuxt 3 前端程式碼
│   ├── pages/              # 頁面路由
│   ├── components/         # Vue 元件
│   ├── stores/             # Pinia 狀態管理
│   └── Dockerfile          # 前端 Docker 建置檔
├── nginx/                  # Nginx 設定與 Dockerfile
├── docker-compose.yml      # 開發環境 Docker 設定
├── docker-compose.prod.yml # 生產環境 Docker 設定
└── .github/workflows/      # CI/CD 設定檔
```

## ✅ 生產環境部署檢查清單 (Deployment Checklist)

在上線前，請務必確認伺服器上的設定符合以下要求：

1.  **修改資料庫密碼 (強制)**:
    *   [ ] 修改 `docker-compose.prod.yml` 中的 `MYSQL_PASSWORD` 與 `MYSQL_ROOT_PASSWORD` (勿使用預設值)。
    *   [ ] 修改 `backend/.env` 中的 `SQLALCHEMY_DATABASE_URL`，確保密碼與上述一致。

2.  **強化安全性**:
    *   [ ] `backend/.env` 中的 `DEBUG` 必須設為 `False`。
    *   [ ] `backend/.env` 中的 `SECRET_KEY` 必須更換為強隨機字串 (可使用 `openssl rand -hex 32` 生成)。

3.  **網域與 CORS**:
    *   [ ] `backend/.env` 中的 `BACKEND_CORS_ORIGINS` 必須包含您的真實網域 (如 `["https://yourdomain.com"]`)。
    *   [ ] `backend/.env` 中的 `API_BASE_URL` 修改為您的真實 API 網址。

4.  **SMTP 郵件**:
    *   [ ] 若需發送通知信，請在 `backend/.env` 填入正確的 SMTP 資訊 (Gmail 需申請應用程式密碼)。

5.  **防火牆與 Port**:
    *   [ ] 確認伺服器防火牆 (UFW / Security Group) 已開放 Port 80 (HTTP) 與 443 (HTTPS)。

## 📝 License

此專案採用 MIT License。