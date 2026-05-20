# 開發對話歷史摘要

> v0.1 → v0.3 的完整開發脈絡。下次接手時讀這份,知道一路上做了什麼決定。

---

## 第一階段:工具選型(對話初期)

**Cleo 的需求**:建立材料庫,可以累積、給案場、產出業主版材料書、未來銜接 Revit。

**評估過的工具**:
- Notion / Obsidian / Excel / Airtable / Filemaker / NocoDB

**最後選擇**:自製 Python Flask + SQLite + 網頁介面。
**關鍵原因**(Cleo 明確說的):
1. 完全本地不要雲端
2. 不要 Docker
3. 不花錢
4. 資料量大不會頓
5. Revit-friendly 欄位設計

---

## 第二階段:視覺設計(多次迭代)

做了 7 個 HTML mockup:
- 業主版材料書 v1 → v4
- 管理介面 v2 → v4
- 新增材料表單 v2 → v3

**Cleo 明確要求**:
- 全部移除斜體
- 品牌名「漣一設計 ｜ 材料庫」單行
- 所有控件高度統一 42px
- 所有 label 對齊
- 業主版材料書封面只佔上半部不要佔全螢幕
- 章節要可折疊不要全部攤開
- 案場標籤要橫向捲動

**最終設計風格**:
- 米白底(#f4f1ec / #faf8f4)
- 黑墨字、暖灰線條、紅色 accent(#c44536)、warm tone(#8b7355)
- Cormorant Garamond + Noto Serif TC + JetBrains Mono

---

## 第三階段:v0.1 開發

第一個能跑的版本,包含:
- Flask 後端 + SQLite
- 主介面、新增表單
- 自動編號、自動歸檔照片
- Windows 啟動腳本

**過程中解決的問題**:
1. Windows 解壓縮看不到中文檔名 → 改 START.bat 為英文檔名
2. .bat 中文編碼導致整個檔案變亂碼 → 純 ASCII + CRLF
3. py 啟動器跳互動式說明 → 加入 python / python3 / py -3 三段偵測
4. Cleo 裝的是 Python 3.14.4,不是 PATH 版本 → 透過 Microsoft Store 安裝後正常

---

## 第四階段:v0.2 開發

Cleo 反饋「不能編輯」,新增:
- 編輯材料(完整表單,所有欄位可改)
- 複製材料(自動產生新編號 + 「(副本)」)
- 刪除材料(二次確認 + 連照片一起刪)
- 照片換 / 刪功能

Cleo 提的選擇:「3+4 全部都能夠編輯」「以上全部都有可能」。
我直接做完所有功能,不再多問。

---

## 第五階段:v0.3 開發(一次做完)

Cleo 說「你一次做吧,我筆記好處理」,所以我把剩下的全部做完:

1. **案場管理**(新增 / 編輯 / 刪除)
2. **加入材料 picker**(視覺勾選 modal)
3. **行內編輯**(位置 / 數量 / 備註)
4. **業主版材料書一鍵輸出**

實際測試所有 API 通過,清理測試資料後打包。

---

## 第六階段:GitHub 自動更新機制

Cleo 問:「之後能夠你直接改好幫我上傳嗎,就不用我每一次都要下載再解壓縮」

評估了三個方案:
- 方法 1:差異更新檔(手動)
- 方法 2:GitHub + UPDATE.bat
- 方法 3:.exe + 自動更新

Cleo 一開始選方法 3(最完整),但聽到要程式碼簽章費用後改選「不花錢」的方法 2。

### GitHub 設定過程

1. Cleo 已有 GitHub 帳號 `axdgcleo-design`
2. 建了 repo 叫 `material-lab`(不是預設的 `lianyi-material-db`)
3. 設為 Public(避免 Personal Access Token 管理麻煩)
4. 上傳 v0.3 全部檔案

### UPDATE.bat 多次迭代

依序遇到的問題:
1. **第 1 版**:預設 `YOUR_USERNAME` 還沒改 → 失敗
2. **第 2 版**:改用 `axdgcleo-design/material-lab` → 還是 404
3. **第 3 版**:Cleo 用瀏覽器測試成功,代表 GitHub OK,但 PowerShell 在 Dropbox 環境抓不到 → 改用 curl
4. **第 4 版**:curl 報錯 `CRYPT_E_NO_REVOCATION_CHECK`(企業網路 SSL 問題)→ 加上 `--ssl-no-revoke`
5. **第 4 版測試成功** ✅

最終 UPDATE.bat:
- 優先 curl(`--ssl-no-revoke`)
- Fallback PowerShell(同樣關閉憑證撤銷檢查)
- 下載後檢查檔案大小 > 1KB
- 失敗時提供清楚診斷訊息

---

## 第七階段:專案管理建立(v0.3.1)

Cleo 問「之後要在哪裡開這些東西」「要做成專案管理嗎」。

決定建立完整文件系統:
- PROJECT.md(總覽)
- CHANGELOG.md(版本紀錄)
- ROADMAP.md(未來計畫)
- DECISIONS.md(重大決定理由)
- STYLE.md(視覺指南)
- docs/CLAUDE_BRIEFING.md(給未來 Claude 用)
- docs/CONVERSATION_LOG.md(本檔案)
- SKILL.md(註冊成 Claude Skill)

---

## 給下次接手者的提示

### 第一個任務:看完這份脈絡

不要重新提問已決定的事(雲端 vs 本地、Flask vs 別的、付費 vs 免費)。
DECISIONS.md 寫得很清楚為什麼這樣選。

### Cleo 已透露的下一步偏好

- 想要估價單(v0.4)
- 想要 Excel 匯入匯出(v0.5)
- 不想要 .exe 化(短期不要再提)
- 對 Skill / 自動化 / 文件化抱持開放態度
- 重視「未來不需要 Claude 也能繼續用」的可持續性

### 不能踩的雷

1. 動 data/ 資料夾
2. 推翻已決定的事而不解釋為什麼
3. 一次問太多選項
4. 介面加任何 AI 味、彩色、斜體、emoji 妝點
5. 建議付費服務
