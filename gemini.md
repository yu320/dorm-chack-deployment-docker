# 前端更新報告 (Frontend Update Report)

## 1. 功能增強 (Feature Enhancements)

### 多語言支援 (i18n) 擴充

*   **檔案:**
    *   `frontend/i18n/locales/en.json`
    *   `frontend/i18n/locales/zh.json`
*   **內容:**
    *   擴充了中英文語系檔案，為多個新功能頁面提供了完整的翻譯。
    *   新增了 PDF 報告、房務與學生管理、資料備份與匯入等模組的相關詞條。
    *   為所有新的使用者操作提示 (Snackbar notifications) 增加了對應的翻譯。

# 專案修改與新增功能統整報告

本文件詳細列出了針對 **忘記密碼功能**、**註冊流程優化 (學號自動產生 Email)** 以及 **介面美化** 所進行的程式碼變更。

---

## 🟢 後端 (Backend - FastAPI)

後端主要修改集中在資料模型擴充、Token 安全機制以及認證 API 的實作。

### 1. 資料模型 (`backend/app/models.py`)
* **修改類別**: `User`
* **變更內容**:
    * 新增 `email` 欄位：用於接收驗證信與重設密碼連結。設定為 `unique=True` 以確保唯一性。

### 2. 資料驗證 Schema (`backend/app/schemas.py`)
* **修改類別**: `UserCreate`
    * 新增 `email: EmailStr` 欄位，確保註冊時包含信箱資訊。
* **新增類別**:
    * `PasswordRecoveryRequest`: 定義「請求重設密碼」時前端需傳送的資料 (僅需 email)。
    * `PasswordResetRequest`: 定義「執行重設密碼」時前端需傳送的資料 (token 與 new_password)。

### 3. 安全工具 (`backend/app/utils/security.py`)
* **新增方法**: `create_password_reset_token(email, expires_delta)`
    * 產生專用於密碼重設的 JWT Token，包含 `type: "password_reset"` 標記，預設時效 15 分鐘。
* **新增方法**: `verify_password_reset_token(token)`
    * 驗證重設 Token 的有效性與類型，解碼成功後回傳 Email，否則回傳 `None`。

### 4. CRUD 操作 (`backend/app/crud/crud_user.py`)
* **新增方法**: `get_by_email(db, email)`
    * 透過 Email 查詢使用者，用於忘記密碼流程確認帳號是否存在。
* **修改方法**: `create(db, obj_in)`
    * 在建立使用者時，將 `obj_in.email` 寫入資料庫。

### 5. 認證 API (`backend/app/api/endpoints/auth.py`)
* **新增路由**: `POST /password-recovery`
    * 接收 Email，檢查使用者是否存在。若存在，產生重設 Token 並發送郵件 (目前為開發模式，會將連結印在 Console)。
* **新增路由**: `POST /reset-password`
    * 接收 Token 與新密碼。驗證 Token 有效性後，更新使用者的密碼雜湊值。
* **修改路由**: `POST /register`
    * 加入 Email 重複註冊檢查 (`get_user_by_email`)。

---

## 🔵 前端 (Frontend - Nuxt 3)

前端主要涉及頁面流程的新增、現有頁面的邏輯調整以及 i18n 國際化支援。

### 1. 註冊頁面 (`frontend/pages/register.vue`)
* **UI 優化**: 改用 **Glassmorphism (毛玻璃)** 風格設計，加入背景動態光暈。
* **邏輯變更**:
    * **移除手動輸入 Email**: 改為自動產生。
    * **自動組合 Email**: 根據輸入的 `student_id_number` 自動加上預設網域 (如 `@school.edu.tw`)。
    * **API 整合**: 將組合後的 Email 包含在 Payload 中發送至後端 `/register` 接口。

### 2. 登入頁面 (`frontend/pages/login.vue`)
* **UI 優化**: 統一使用毛玻璃風格。
* **新增功能**:
    * 加入 **「忘記密碼？」** 連結，導向至 `/forgot-password`。
    * 登入按鈕加入 **Loading 狀態**，防止重複提交。

### 3. [NEW] 忘記密碼頁面 (`frontend/pages/forgot-password.vue`)
* **檔案用途**: 提供使用者輸入 Email 以請求重設連結的介面。
* **主要功能**:
    * 呼叫後端 `/api/v1/auth/password-recovery`。
    * 顯示發送成功或失敗的 Snackbar 提示。

### 4. [NEW] 重設密碼頁面 (`frontend/pages/reset-password.vue`)
* **檔案用途**: 使用者點擊 Email 連結後抵達的頁面，用於設定新密碼。
* **主要功能**:
    * **URL Token 解析**: 在 `onMounted` 時從網址參數 (`route.query.token`) 獲取 Token。
    * **密碼確認**: 驗證兩次輸入的密碼是否一致。
    * **API 整合**: 呼叫 `/api/v1/auth/reset-password` 進行密碼更新。
    * **自動導轉**: 成功後自動導向回登入頁面。

### 5. 國際化設定 (`frontend/i18n/locales/zh.json`)
* **新增翻譯**:
    * `register`: 包含學號、處理中、已有帳號等文字。
    * `login`: 包含忘記密碼、重設連結、返回登入等文字。
    * `snackbar`: 包含各種成功與錯誤訊息 (如：連結已發送、密碼不一致)。
    * 修正 `@` 符號在 JSON 中的語法錯誤 (改為 `{'@'}`)。

### 6. 全域元件與工具優化
* **`frontend/components/common/Snackbar.vue`**:
    * 加入 **手動關閉按鈕 (X)**。
* **`frontend/composables/useSnackbar.ts`**:
    * 修復 **Race Condition**：使用全域 `timer` 狀態，防止多個 Snackbar 連續觸發時提早消失。
* **`frontend/composables/api/useInspectionApi.ts`**:
    * (若有使用) 封裝了 API 請求邏輯，保持頁面程式碼整潔。

---

## 📝 執行注意事項

1.  **資料庫遷移**: 由於後端 `User` 模型新增了 `email` 欄位，請務必執行 Alembic 遷移指令：
    ```bash
    alembic revision --autogenerate -m "Add email to users"
    alembic upgrade head
    ```
2.  **網域設定**: 在 `frontend/pages/register.vue` 中，請確認 `const emailDomain` 已設定為正確的學校網域。
3.  **郵件發送**: 目前後端僅會在 Console 印出重設連結，若需實際發信，請實作 `backend/app/utils/email.py`。
    *   `frontend/i18n/locales/zh.json`
*   **內容:**
    *   擴充了中英文語系檔案，為多個新功能頁面提供了完整的翻譯。
    *   新增了 PDF 報告、房務與學生管理、資料備份與匯入等模組的相關詞條。
    *   為所有新的使用者操作提示 (Snackbar notifications) 增加了對應的翻譯。
