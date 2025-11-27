# 專案動態更新與調整指南 (Adjustments Guide)

本文件將說明如何動態更新專案中特定內容，以及一些調整建議。

---

## 一、新增或修改訪客首頁 (Guest Home) 的 Features 卡片

訪客首頁 (`frontend/components/guest/Home.vue`) 中的特色卡片列表，現在可以透過修改 JSON 設定檔來管理，無需直接修改 Vue 程式碼。

### 1. 卡片資料來源

卡片資料目前儲存於 `frontend/data/guest-features.json`。
這個 JSON 檔案是一個陣列，每個物件代表一張卡片。

**JSON 檔案結構範例 (`guest-features.json`)**：
```json
[
  {
    "id": "easyInspection",
    "icon": "heroicons:clipboard-document-check",
    "color": "green",
    "title_zh": "輕鬆檢查",
    "description_zh": "透過我們直觀的數位檢查表，在幾分鐘內完成房間檢查。",
    "title_en": "Easy Inspection",
    "description_en": "Complete your room inspection in minutes with our intuitive digital checklist."
  },
  // ... 其他卡片
]
```

### 2. 如何增加/修改卡片

1.  **編輯 `frontend/data/guest-features.json` 檔案**：
    *   新增一個 JSON 物件到陣列中。
    *   修改現有卡片的屬性值。

2.  **屬性說明**：
    *   `id` (字串, 必填)：卡片的唯一識別符。
    *   `icon` (字串, 必填)：Icon 的名稱，例如 `heroicons:shield-check`。請參考 [Heroicons 官網](https://heroicons.com/) 或專案使用的 Icon 庫。
    *   `color` (字串, 必填)：卡片的顏色主題，例如 `green`, `blue`, `purple`, `red`。
    *   `title_zh` (字串, 必填)：中文標題。
    *   `description_zh` (字串, 必填)：中文描述。
    *   `title_en` (字串, 必填)：英文標題。
    *   `description_en` (字串, 必填)：英文描述。

3.  **儲存檔案**：前端應用程式通常會自動偵測 `guest-features.json` 的變更並熱更新。

---

## 二、圖示 (Icon) 如何尋找及選擇

本專案使用 Nuxt Icon 模組，其背後整合了 Iconify，提供龐大的圖示庫。
您可以前往以下網站尋找並複製 Icon 的名稱：

1.  **[Icones.js.org](https://icones.js.org/)**
2.  **[Iconify.design](https://icon-sets.iconify.design/)**

**尋找步驟：**
1.  在搜尋框輸入您想找的關鍵字 (例如：`user`, `home`, `check`, `shield`, `megaphone` 等)。
2.  在結果中，建議篩選或選擇 **Heroicons** 集合，因為專案目前的風格主要使用此系列圖示，保持視覺一致性。
3.  點擊您喜歡的圖示，它的名稱會以 `集合名稱:圖示名稱` 的格式顯示 (例如 `heroicons:arrow-right` 或 `heroicons:shield-check`)。
4.  複製此名稱，並填入您 JSON 設定檔 (如 `guest-features-zh.json`) 或 Vue 元件中 `<Icon name="..." />` 的 `name` 屬性即可。

---

## 三、隱私權政策內容調整

隱私權政策內容儲存於 `frontend/data/privacy.json` (中文版) 和 `frontend/data/privacy-en.json` (英文版)。

**JSON 檔案結構範例 (`privacy.json`)**：
```json
{
  "title": "隱私權及網站安全政策",
  "sections": [
    {
      "heading": "1. 隱私權保護政策的適用範圍",
      "content": "隱私權保護政策內容，包括本網站如何處理在您使用網站服務時收集到的個人識別資料..."
    },
    // ... 其他章節
  ]
}
```

### 如何修改政策內容

1.  **編輯 `frontend/data/privacy.json` 或 `frontend/data/privacy-en.json`**：
    *   修改 `title` 屬性更改整體標題。
    *   在 `sections` 陣列中新增、修改或刪除物件。每個物件包含 `heading` (章節標題) 和 `content` (章節內容)。
2.  **儲存檔案**。

---

## 四、圖表標題與配色調整

### 1. 管理員儀表板圖表標題 (`frontend/components/admin/Home.vue`)

圖表標題現在是多語系的，請修改 `frontend/i18n/locales/zh.json` 和 `frontend/i18n/locales/en.json` 中 `dashboard` 物件下的鍵值：
*   `dashboard.passRate`: "檢查通過率" / "Inspection Pass Rate"
*   `dashboard.topDamageTypes`: "常見損壞類型" / "Top Damage Types"

### 2. 圖表配色

您可以在 `frontend/components/admin/Home.vue` 中修改 `passRateData` 和 `damageRankingData` Computed Properties 內 `datasets` 的 `backgroundColor` 陣列。

**範例**：
```javascript
const passRateData = computed(() => {
  // ...
  return {
    // ...
    datasets: [
      {
        backgroundColor: ['#34D399', '#F87171', '#FBBF24'], // 綠、紅、黃
        data
      }
    ]
  };
});
```
您可以替換這些 Hex Code 值為您偏好的顏色。

---

## 五、導覽列項目調整

導覽列 (`frontend/components/layout/TheHeader.vue`) 的所有文字都是透過 `frontend/i18n/locales/zh.json` 和 `frontend/i18n/locales/en.json` 中的 `navigation` 或 `admin` 物件下的鍵值來動態載入的。

### 如何修改導覽列文字

1.  編輯 `frontend/i18n/locales/zh.json` 或 `frontend/i18n/locales/en.json`。
2.  找到對應的 `navigation.xxx` 或 `admin.xxx` 鍵值，修改其右側的翻譯文本。

---

## 六、訪客首頁 (Guest Home) 布局建議 (最大 3 列)

如果您希望訪客首頁 (`frontend/components/guest/Home.vue`) 的 Features 卡片 Grid 在大螢幕下最大顯示 3 列，而不是目前的 4 列（`lg:grid-cols-4`），這樣有 4 張卡片時，第四張卡片會自動換行到下一列，請修改以下 CSS Class：

**將：**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 text-left">
```

**修改為：**
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 text-left">
```
這表示在 `lg` 螢幕尺寸下，每行將最多顯示 3 張卡片。

---
