# 漣一設計 ｜ 材料庫系統

> A private material database system for Lian Yi Interior Design Studio.

## 這個專案是什麼

漣一設計(Lian Yi Design)的本地材料庫管理系統。讓設計師 Cleo Tseng 累積、查找、整理材料,並為每個案場產生「業主版材料書」(交付給屋主的材料說明書)。

## 為什麼存在這個系統

設計師 Cleo 的痛點:
1. **材料分散** — 樣品、規格、價格、廠商資訊散在 Excel / 紙本 / 手機 / Notion / 群組訊息
2. **同樣的材料用在不同案場** — 每次重新查資料浪費時間
3. **業主版說明每次重寫** — 客戶想知道「我家用了什麼材料、怎麼保養」,每次手動整理太累
4. **不想用雲端服務** — 不想被廠商鎖定、不想付月費、客戶資料外洩風險

## 解決方案

**完全在本機運作的網頁 App**:
- 後端:Python Flask + SQLite
- 前端:HTML + 原生 CSS / JS(無框架,無外部依賴)
- 啟動方式:雙擊 `START.bat` → 自動開瀏覽器
- 資料位置:`data/lianyi.db` + `data/photos/`

## 系統現況(v0.3)

### 已實作功能

**材料庫**
- 新增 / 編輯 / 複製 / 刪除材料
- 10 個預設分類(玻璃、板材、面材、磁磚、石材、塗料、金屬、五金、織品、燈具)
- 分類自定義 / 改名 / 刪除
- 自動編號(GL-001, WD-001...)
- 4 張照片(主圖 + 3 副圖)
- 4 種說明(業主版說明、業主版保養、施工注意、踩雷筆記)
- 搜尋(編號、品名、供應商、標籤)
- 分類篩選

**案場**
- 新增 / 編輯 / 刪除案場
- 加入材料(視覺勾選 picker)
- 行內編輯位置、數量、備註
- 業主版前言

**業主版材料書**
- 一鍵輸出 HTML
- 封面 + 致業主前言 + 材料目錄(可折疊)+ 後記
- 可用瀏覽器列印成 PDF
- 自動套用業主版說明、保養、安裝位置

### 技術架構

```
LianYi/
├── START.bat           # 啟動器 (純 ASCII + CRLF)
├── UPDATE.bat          # GitHub 自動更新工具 (with curl + SSL workaround)
├── README.txt          # 英文簡要說明
├── 說明.md             # 中文詳細說明
├── PROJECT.md          # 本檔案 - 專案總覽
├── CHANGELOG.md        # 版本變更紀錄
├── ROADMAP.md          # 未來功能計畫
├── DECISIONS.md        # 重大決定紀錄
├── STYLE.md            # 視覺風格指南
├── .gitignore          # Git 排除清單
│
├── app/                # 程式碼
│   ├── server.py       # Flask 後端 (~620 行)
│   ├── static/         # CSS, JS
│   │   ├── style.css   # 主樣式
│   │   ├── book.css    # 業主版材料書樣式
│   │   ├── admin.js    # 主介面 JS
│   │   ├── new.js      # 新增表單 JS
│   │   └── edit.js     # 編輯表單 JS
│   └── templates/      # HTML
│       ├── admin.html         # 材料庫主畫面
│       ├── new.html           # 新增材料
│       ├── edit.html          # 編輯材料
│       ├── projects.html      # 案場列表
│       ├── project_detail.html # 案場詳情
│       └── book.html          # 業主版材料書
│
├── data/               # 使用者資料(絕不上傳 GitHub)
│   ├── lianyi.db       # SQLite 資料庫
│   └── photos/         # 材料照片
│       └── {編號}/main.jpg, sub_1.jpg...
│
└── docs/               # 文件與紀錄
    ├── CLAUDE_BRIEFING.md  # 給未來 Claude 看的快速上手
    └── CONVERSATION_LOG.md # 開發對話紀錄摘要
```

## 資料庫結構

4 個表:

```sql
categories          -- 分類(玻璃、板材...)
├── id, name, code_prefix, sort_order

materials           -- 材料(主表)
├── id, code, category_id
├── name, name_en, spec, detail
├── unit, price_material, price_labor
├── supplier, supplier_contact, brand, model
├── status (常用/偶爾/已停用/觀望中)
├── client_about, client_care    -- 業主公開
├── internal_note, bug_note      -- 內部用
├── usage_locations, tags
├── photo_main, photo_subs

projects            -- 案場
├── id, code, name
├── client_name, client_type, area
├── completed_date, foreword

project_materials   -- 案場-材料關聯
├── id, project_id, material_id
├── location, quantity, note
```

## 維護資訊

- **使用者**: Cleo Tseng (漣一設計)
- **環境**: Windows 11 + Python 3.14.4
- **資料路徑**: `On Design Lab.ltd Dropbox/17-設計師資料夾/Cleo/02.材料庫/`
- **GitHub**: https://github.com/axdgcleo-design/material-lab
- **本地連接埠**: http://127.0.0.1:5005

## 給未來維護者的提示

1. **資料是命根子** — `data/lianyi.db` 和 `data/photos/` 是 Cleo 的核心資產,任何更新都不能動到。
2. **`.bat` 檔必須是純 ASCII + CRLF 換行** — Windows cmd 對中文 .bat 編碼極度敏感。
3. **Dropbox 同步環境** — 注意 LianYi 資料夾在 Dropbox 內,部分操作(尤其 PowerShell)會被干擾。
4. **企業網路 SSL 問題** — `curl` 必須加 `--ssl-no-revoke`,否則憑證撤銷檢查會失敗。
5. **不要斜體** — 全系統 CSS 都禁用 italic,Cleo 強烈偏好。

