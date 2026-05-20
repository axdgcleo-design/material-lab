# 版本變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)。

## v0.3 — 2026.05.21

### 新增
- 案場管理(新增 / 編輯 / 刪除 / 列表)
- 材料 picker:視覺化勾選材料加入案場
- 行內編輯:案場內的材料位置 / 數量 / 備註可直接點欄位修改,自動儲存
- 業主版前言:每個案場可寫一段「致業主」文字
- 業主版材料書一鍵輸出:`/book/{案場ID}` 自動產出可列印的 HTML
- 業主版材料書:可折疊章節、封面、後記
- 側邊欄新增「案場」入口

### 變更
- 系統版本升級到 v0.3
- README.txt 與 說明.md 更新升級指引

## v0.2 — 2026.05.21

### 新增
- 編輯材料(完整表單,所有欄位可改)
- 複製材料(自動產生新編號 + 「(副本)」後綴,連照片一起複製)
- 刪除材料(二次確認,連照片資料夾一起刪)
- 照片管理:編輯時可換照片、刪除照片
- 右側細節面板的動作列:[ ✎ 編輯 ] [ ⎘ 複製 ] [ 🗑 刪除 ]

### 變更
- 系統版本升級到 v0.2

## v0.1.2 — 2026.05.21

### 修正
- START.bat 從 UTF-8 改為純 ASCII + CRLF(解決 Windows cmd 中文亂碼問題)
- 移除 `chcp 65001` 指令(在某些環境會搞砸後續指令)
- 改善 Python 偵測邏輯:python → python3 → py -3 三段 fallback,且 `py` 啟動器加上 `-3` 避免進入互動式說明畫面

## v0.1.1 — 2026.05.21

### 修正
- Python 偵測加上 `py -3` fallback,避免 Windows 內建 py 啟動器在沒裝 Python 時跳出互動式說明

## v0.1 — 2026.05.21

### 第一個能跑的版本
- Flask + SQLite 後端
- 材料庫管理頁(分類 + 卡片 + 細節面板)
- 新增材料表單(完整欄位 + 4 張照片 + 4 種說明)
- 分類管理(新增 / 改名 / 刪除)
- 搜尋與篩選
- 自動編號系統(GL-001, WD-001...)
- 自動歸檔照片到 `data/photos/{編號}/`
- Windows 啟動腳本 START.bat

### 技術選型決定
- 後端:Python Flask(原因見 DECISIONS.md)
- 資料庫:SQLite(原因見 DECISIONS.md)
- 前端:原生 HTML/CSS/JS,無框架
- 部署:本機 http://127.0.0.1:5005

---

## 預發版(尚未發布)

### v0.3.1 — 工具更新

- 新增 GitHub 自動更新機制 UPDATE.bat
- 加上 curl + SSL revocation workaround(解決企業網路憑證問題)
- 新增 .gitignore(保護 data/ 不上傳)
- 新增專案管理文件:PROJECT.md、CHANGELOG.md、ROADMAP.md、DECISIONS.md、STYLE.md
- 建立 GitHub repository: axdgcleo-design/material-lab
