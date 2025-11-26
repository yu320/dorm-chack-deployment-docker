# 學生宿舍檢查系統 (Student Dormitory Inspection System)

## 專案簡介
這是一個用於管理學生宿舍檢查流程的系統。它提供了一個後端 API 服務，用於處理使用者管理、宿舍房間與床位配置、學生資料、檢查紀錄的建立與查詢，並支援將檢查報告匯出為 PDF 檔案。前端則是一個基於 Nuxt.js 的網頁應用程式，提供直觀的使用者介面。

## 主要功能
*   **使用者管理**: 建立、查詢、更新使用者帳號。
*   **身份驗證與授權**:
    *   使用者登入 (JWT Token)。
    *   使用者登出 (Token 黑名單機制)。
    *   使用者註冊 (需綁定預先存在的學生資料)。
    *   基於角色的權限控制 (RBAC)。
    *   個人資料查詢。
*   **宿舍結構管理**:
    *   棟別 (Building) 管理。
    *   寢室 (Room) 管理，包含戶別、寢室號碼、房型等。
    *   床位 (Bed) 管理，包含床位號碼、床型、可用狀態等。
*   **學生資料管理**: 建立、查詢、更新學生詳細資料。
*   **檢查項目管理**: 定義宿舍檢查的各項物品。
*   **檢查紀錄**:
    *   建立新的宿舍檢查紀錄。
    *   查詢檢查紀錄 (可依權限查看所有或僅自己的紀錄)。
    *   更新檢查紀錄狀態。
*   **PDF 報表匯出**: 將檢查紀錄匯出為格式化的 PDF 檔案，包含簽名圖片。

## 技術棧

### 後端 (Backend)
*   **框架**: FastAPI (Python)
*   **ORM**: SQLAlchemy
*   **資料庫**: MySQL
*   **身份驗證**: JWT (JSON Web Tokens)
*   **密碼雜湊**: Passlib (bcrypt)
*   **資料驗證**: Pydantic
*   **PDF 產生**: ReportLab
*   **ASGI 伺服器**: Uvicorn

### 前端 (Frontend)
*   **框架**: Nuxt.js (Vue.js)
*   **UI 框架**: Vuetify
*   **套件管理**: npm

## 設定與安裝

### 前置條件
在啟動專案之前，請確保您的系統已安裝以下軟體：
*   **Python 3.8+**
*   **MySQL 資料庫**
*   **Node.js & npm**

### 後端設定

1.  **進入後端目錄**:
    ```bash
    cd backend
    ```

2.  **建立並啟用 Python 虛擬環境**:
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source ./.venv/bin/activate
    ```

3.  **安裝 Python 依賴套件**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **資料庫配置**:
    本專案使用 `.env` 檔案來管理敏感配置，例如資料庫連線字串和 JWT 密鑰。請在 `backend` 目錄下創建一個 `.env` 檔案。

    *   **建立 `.env` 檔案**:
        在 `backend` 資料夾中創建一個名為 `.env` 的檔案，並填入以下內容（根據您的選擇）。請務必將 `your_super_secret_key` 替換為一個強而安全的密鑰。

        **使用 SQLite (推薦用於開發)**:
        SQLite 是一個輕量級的檔案型資料庫，不需要額外的伺服器。
        ```
        SQLALCHEMY_DATABASE_URL="sqlite+aiosqlite:///./sql_app.db"
        SECRET_KEY="your_super_secret_key"
        ALGORITHM="HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```
        這將在 `backend` 目錄下創建一個 `sql_app.db` 檔案。

        **使用 MySQL**:
        如果您選擇使用 MySQL，請確保您已安裝 MySQL 伺服器並創建了一個資料庫。
        ```
        SQLALCHEMY_DATABASE_URL="mysql+aiomysql://user:password@host:port/dbname"
        SECRET_KEY="your_super_secret_key"
        ALGORITHM="HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        ```
        請將 `user`, `password`, `host`, `port`, `dbname` 替換為您的 MySQL 資料庫設定。

    *   **資料庫初始化**:
        首次啟動後端服務時，程式會自動根據 `SQLALCHEMY_DATABASE_URL` 建立所有必要的資料表，並載入初始資料 (請參考 `backend/app/crud.py` 中的 `seed_database` 函式)。

5.  **啟動後端服務 (開發)**:
    *   確保您已在 `backend` 目錄中，並已啟動虛擬環境。
    *   執行指令啟動服務：
    ```bash
    uvicorn main:app --reload
    ```
    *   服務將預設在 `http://127.0.0.1:8000` 啟動。

### 前端設定

1.  **進入前端目錄**:
    ```bash
    cd frontend
    ```

2.  **安裝 Node.js 依賴套件**:
    ```bash
    npm install
    ```

3.  **啟動前端開發伺服器**:
    ```bash
    npm run dev
    ```
    *   前端應用程式將預設在 `http://localhost:3000` 啟動。

## API 端點概覽 (部分)

後端 API 服務將在 `/api/v1` 路徑下提供以下主要功能：

*   `POST /api/v1/token`: 使用者登入，獲取 JWT Token。
*   `POST /api/v1/logout`: 使用者登出，使當前 JWT Token 失效。
*   `POST /api/v1/users/`: 註冊新使用者 (需提供學號綁定學生資料)。
*   `GET /api/v1/users/me/`: 獲取當前登入使用者的個人資料。
*   `POST /api/v1/buildings/`: 建立新的棟別。
*   `GET /api/v1/buildings/`: 查詢所有棟別。
*   `POST /api/v1/rooms/`: 建立新的寢室。
*   `GET /api/v1/rooms/`: 查詢所有寢室。
*   `POST /api/v1/beds/`: 建立新的床位。
*   `GET /api/v1/beds/`: 查詢所有床位。
*   `POST /api/v1/students/`: 建立新的學生資料。
*   `GET /api/v1/students/`: 查詢所有學生資料。
*   `POST /api/v1/inspections/`: 建立新的檢查紀錄。
*   `GET /api/v1/inspections/`: 查詢檢查紀錄。
*   `GET /api/v1/inspections/search`: 進階查詢檢查紀錄。
*   `GET /api/v1/inspections/{record_id}/pdf`: 匯出指定檢查紀錄的 PDF 報表。

### 建立初始管理員帳號 (選填)
首次啟動後端服務後，您可以透過以下 `curl` 指令創建一個管理員帳號。請將 `admin` 和 `admin` 替換為您想要的用戶名和密碼，並將 `B11111111` 替換為一個有效的學生學號（如果需要綁定）。
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin", "student_id_number": "B11111111"}'
```

## 郵件通知功能使用說明

此功能允許管理員直接從應用程式向各學生群組發送電子郵件通知。要使用此功能，您需要配置後端郵件設定，然後使用前端介面。

**1. 後端配置 (必填設定):**

在發送任何電子郵件之前，後端應用程式需要知道您的電子郵件伺服器詳細資訊。這是透過在 `backend/` 目錄中的 `.env` 檔案中設定環境變數來完成的。

*   **定位/建立 `.env` 檔案:** 在 `backend/` 目錄中，開啟 (`.env`) 檔案 (如果存在) 或建立一個新檔案。
*   **新增郵件伺服器詳細資訊:** 將以下行添加到您的 `.env` 檔案中，並將佔位符值替換為您的實際 SMTP 伺服器憑證和資訊：

    ```
    MAIL_USERNAME="your_email@example.com"      # 用於發送郵件的電子郵件地址
    MAIL_PASSWORD="your_email_password"        # 您的電子郵件帳戶密碼
    MAIL_FROM="your_email@example.com"         # 郵件的「寄件者」地址
    MAIL_SERVER="smtp.example.com"             # 您的 SMTP 伺服器主機 (例如：smtp.gmail.com)
    MAIL_PORT=587                              # 您的 SMTP 伺服器埠號 (常用：TLS 為 587，SSL 為 465)
    MAIL_TLS=True                              # 如果您的 SMTP 伺服器使用 TLS (推薦)，則設定為 True
    ```
*   **重啟後端:** 對 `.env` 檔案進行更改後，您**必須**重新啟動後端伺服器，更改才會生效。

**2. 前端使用 (發送郵件):**

後端配置完成後，您可以使用使用者介面撰寫和發送通知。

*   **存取頁面:** 導航到前端應用程式管理部分中的「郵件通知」頁面 (通常位於類似 `http://localhost:3000/admin/email-notifications` 的 URL)。
*   **選擇收件人:** 從「收件人」下拉選單中選擇以下選項之一：
    *   **所有學生:** 將電子郵件發送給系統中所有已連結使用者帳戶的註冊學生。
    *   **大樓內的學生:** 選擇此項，然後從出現的新下拉選單中選擇特定的大樓。
    *   **房間內的學生:** 選擇此項，然後從出現的新下拉選單中選擇特定的房間。
    *   **家庭內的學生:** 選擇此項，然後輸入特定的家庭識別碼 (例如：「A1201」)。
    *   **自訂收件人:** 選擇此項，然後在提供的文字欄位中輸入以逗號分隔的特定電子郵件地址列表 (例如：`email1@example.com, email2@example.com`)。
*   **撰寫郵件:**
    *   **主旨:** 在「主旨」欄位中輸入電子郵件的主旨行。
    *   **內容:** 在「訊息」文字區域中撰寫電子郵件的主要內容。
*   **發送:** 點擊「發送郵件」按鈕。系統將嘗試發送電子郵件。您將收到一條通知 (snackbar)，確認成功或指示任何錯誤。

**3. 權限:**

*   要使用此功能，發送郵件的使用者必須擁有其角色分配的 `manage_users` 權限。


---

## 部署 (Deployment)

將此專案部署到生產環境時，請遵循以下說明以確保安全性和效能。

### 1. 部署前注意事項

*   **資料庫**: 強烈建議將 `backend/.env` 檔案中的 `SQLALCHEMY_DATABASE_URL` 從開發用的 SQLite 更換為生產級資料庫，例如 MySQL 或 PostgreSQL。
*   **密鑰**: 請務必在 `backend/.env` 檔案中設定一個長且隨機的 `SECRET_KEY`，以保護使用者 Token 的安全。
*   **偵錯模式**: 為了安全和效能，應關閉偵錯模式。
    *   **後端**: 在 `backend/app/config.py` 中，可以透過環境變數將 `DEBUG` 設為 `False`。
    *   **前端**: `frontend/nuxt.config.ts` 已設定在生產環境建置時自動移除 `console` 和 `debugger` 指令。

### 2. 後端部署

後端服務應在沒有 `--reload` 選項的情況下啟動，並監聽所有網路介面 (`0.0.0.0`) 以便從外部存取。

**啟動指令:** 
```bash
# 進入後端目錄
cd backend

# 確保虛擬環境已啟用
# Windows: .\.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 使用 uvicorn 啟動生產服務
uvicorn main:app --host 0.0.0.0 --port 8000
```

為了獲得更好的穩定性和效能，建議使用 Gunicorn 來管理 Uvicorn 程序。
```bash
# 範例：使用 Gunicorn 啟動 4 個 worker
# 注意：若要使用 Gunicorn，需先執行 pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### 3. 前端部署

前端應用程式在開發時使用 Vite 代理 (proxy) 將 `/api` 請求轉發到後端。在生產環境中，推薦使用 Web 伺服器 (如 Nginx) 來提供靜態檔案並設定反向代理，這樣您就不需要修改任何前端程式碼。

1.  **建置前端應用程式**:
    ```bash
    # 進入前端目錄
    cd frontend

    # 安裝依賴
    npm install

    # 執行生產環境建置
    npm run build
    ```
    這會在 `frontend/.output/public` 目錄下產生優化過的靜態檔案。

2.  **設定 Web 伺服器 (Nginx 範例)**:
    您需要設定您的 Web 伺服器來提供這些靜態檔案，並將 API 請求反向代理到後端服務。

    以下是一個 Nginx 的設定檔範例：
    ```nginx
    server {
        listen 80;
        server_name your_domain.com; # 替換為您的域名或 IP

        # 提供前端靜態檔案
        location / {
            root /path/to/your/project/frontend/.output/public;
            try_files $uri $uri/ /index.html;
        }

        # 將 API 請求反向代理到後端 FastAPI 服務
        location /api/v1/ {
            proxy_pass http://127.0.0.1:8000/api/v1/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```
    *   請記得將 `your_domain.com` 和 `/path/to/your/project/` 替換為您專案的實際域名和路徑。
    *   此設定會讓前端應用程式在根目錄 (`/`) 提供服務，並將所有 `/api/v1/` 開頭的請求轉發給在本機 8000 port 運行的後端服務。

---

## 使用 Docker 部署 (Deployment with Docker)

本專案已設定好 Docker，讓您可以透過 `docker-compose` 快速啟動一個包含所有服務的完整環境。

### 前置條件
*   **Docker**: [安裝 Docker](https://docs.docker.com/get-docker/)
*   **Docker Compose**: (通常會跟 Docker 一起安裝)

### 1. 環境設定
Docker 環境的設定由 `docker-compose.yml` 檔案管理。後端服務的設定（如資料庫連線、JWT 密鑰）會從 `backend/.env` 檔案讀取。

*   請先確保 `backend/.env` 檔案已存在並包含正確的設定。
*   **重要**: 如果您想在 Docker 環境中也運行資料庫，您可以在 `docker-compose.yml` 中取消資料庫服務的註解，並將 `backend/.env` 中的 `SQLALCHEMY_DATABASE_URL` 的主機位址 (`host`) 改為資料庫服務的名稱 (例如 `db`)。
    *   `SQLALCHEMY_DATABASE_URL="mysql+aiomysql://user:password@db/dbname"`

### 2. 啟動應用程式
在專案的根目錄（與 `docker-compose.yml` 相同的目錄）執行以下指令：

```bash
# --build 會強制重新建置映像檔，確保程式碼的變更被應用
docker-compose up --build
```

這個指令會：
1.  為後端和前端分別建立 Docker 映像檔。
2.  啟動後端、前端和 Nginx 反向代理三個容器。
3.  Nginx 會監聽 `http://localhost:80`，並自動將請求轉發到對應的前端或後端服務。

### 3. 存取應用程式
啟動成功後，您可以直接在瀏覽器中開啟 `http://localhost` 來存取應用程式。

### 4. 停止應用程式
若要停止所有服務，請在同一個目錄下按 `Ctrl + C`，然後執行：

```bash
docker-compose down
```
這個指令會停止並移除所有相關的容器和網路。
