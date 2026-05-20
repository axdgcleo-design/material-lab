# Briefing for Claude — 漣一材料庫專案

> 給未來 Claude 看的 60 秒快速上手文件。
> 當 Cleo 提到「漣一材料庫」「lianyi」「material-lab」就讀這份。

---

## 你正在面對的人

**Cleo Tseng** — 室內設計師,品牌「漣一設計」(Lian Yi Design),IG: `@cleo.o8o8`

工作環境:
- Windows 11
- Python 3.14.4
- 工作資料夾在 Dropbox 同步路徑下
- 用 Skill 系統(已有 cleo-design-positioning / construction-report / vlog-script-generator)

---

## 她的偏好(必讀)

1. **不要斜體**
2. **不要花錢的方案**
3. **介面要乾淨克制**,書本感、事務所感,不要 AI 味
4. **偏好直接動手做完**,不要太多選項詢問
5. **配色**:米白底 + 黑墨字 + 紅色 accent
6. **字體**:Cormorant Garamond + Noto Serif TC + JetBrains Mono
7. **中文當主、英文當副標**

詳細見 `STYLE.md`。

---

## 專案現況

- **版本**: v0.3
- **GitHub**: https://github.com/axdgcleo-design/material-lab (Public)
- **本地路徑**: `On Design Lab.ltd Dropbox/17-設計師資料夾/Cleo/02.材料庫/LianYi_v0.3_github_ready/`

### 已完成
- 材料庫(新增/編輯/複製/刪除)
- 案場管理
- 業主版材料書一鍵輸出
- GitHub 自動更新機制(UPDATE.bat)

### 接下來預定做
- v0.4 估價單
- v0.5 Excel 匯入匯出
- v0.6 案場照片整合

詳細見 `ROADMAP.md`。

---

## 技術骨架

```
LianYi/
├── START.bat           # 雙擊啟動
├── UPDATE.bat          # GitHub 自動更新(已加 --ssl-no-revoke)
├── app/
│   ├── server.py       # Flask 後端,單一檔案
│   ├── templates/      # 6 個 HTML 頁面
│   └── static/         # CSS, JS
└── data/               # SQLite + 照片(從不上傳 GitHub)
```

**啟動**: `python app/server.py` → http://127.0.0.1:5005
**資料庫**: SQLite,4 個表(categories / materials / projects / project_materials)
**前端**: 原生 HTML/CSS/JS,無框架

---

## 已知的環境特殊問題

1. **Dropbox 干擾 PowerShell**:UPDATE.bat 改用 curl 解決
2. **企業網路 SSL revocation 失敗**:curl 加 `--ssl-no-revoke` 解決
3. **Windows cmd 中文 .bat 亂碼**:所有 .bat 必須純 ASCII + CRLF 換行
4. **Python 啟動器 py 在沒裝 Python 時跳互動式說明**:必須加 `-3` 參數

---

## 工作流程

### Cleo 要改東西時
1. 她跟你說「漣一材料庫想 XX」
2. 你修改 `app/` 內的程式碼
3. 打包成更新包 zip 給她
4. 她上傳到 GitHub
5. 她雙擊 UPDATE.bat
6. 完成

### 重要原則
- **絕對不能動 `data/`** — Cleo 的核心資產
- **修改前先看 CHANGELOG.md** — 確認你不會重做已做過的事
- **重大決定查 DECISIONS.md** — 不要推翻已決定的事(除非有新理由)
- **新功能上 ROADMAP.md** — 排好優先順序再做

---

## 溝通風格

- 用繁體中文(台灣用語)
- 簡潔、直接、不要堆砌客套話
- 給選項時最多 3-4 個
- 避免「我建議你應該也許可以...」這種廢話開頭
- 該直接做的就動手做,不要每次都問

---

## 緊急聯絡(技術問題)

1. 中文 .bat 亂碼 → 純 ASCII + CRLF + 不要 `chcp 65001`
2. UPDATE.bat 抓不到 → 檢查 curl 有沒有 `--ssl-no-revoke`、檢查 repo 是否 public
3. Python 找不到 → START.bat 三段 fallback: python → python3 → py -3
4. 資料庫遷移 → SQLite,直接 ALTER TABLE,不要重建

