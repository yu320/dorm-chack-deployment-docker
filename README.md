# 學生宿舍查核與管理系統 (Student Dormitory Inspection System)

這是一個現代化、全功能的宿舍管理平台，旨在簡化宿舍查核、學生管理與行政作業流程。系統結合了高效的 FastAPI 後端與互動豐富的 Nuxt 3 前端，並採用 Docker 容器化技術實現快速部署。

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

## 📝 License

此專案採用 MIT License。