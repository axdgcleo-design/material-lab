# 視覺風格指南

漣一設計材料庫的視覺與互動原則。任何新功能、新介面都應遵循。

---

## 設計關鍵字

**書本感、事務所感、克制、有溫度**

❌ 不要的:
- 紫色漸層
- 鮮豔的 emoji 妝點
- 卡通感、可愛風
- Material Design / iOS 系統感
- 任何「AI 工具」常見視覺特徵

✅ 要的:
- 印刷品的氣質
- 事務所信箋的氣質
- 老派出版社的氣質
- 雜誌排版的氣質

---

## 配色

### CSS 變數定義

```css
:root {
  /* 紙與背景 */
  --bg: #f4f1ec;          /* 米白 - 整體底色 */
  --paper: #faf8f4;       /* 淺米白 - 卡片與面板 */
  --paper-warm: #f0ebe2;  /* 微暖米白 - hover / 強調 */

  /* 文字 */
  --ink: #1a1a1a;         /* 墨黑 - 主文字 */
  --ink-soft: #4a4a4a;    /* 軟黑 - 次要文字 */
  --ink-faint: #9a9a9a;   /* 淡灰 - 提示、副標 */
  --ink-mute: #6a6a6a;    /* 中灰 - 中等資訊 */

  /* 線條 */
  --line: #d8d4cc;        /* 主線條 */
  --line-faint: #e8e5df;  /* 弱線條 */

  /* 強調 */
  --warm: #8b7355;        /* 暖灰 - 業主版相關 */
  --accent: #c44536;      /* 磚紅 - 警示 / 重要 */
  --success: #4a5d4a;     /* 軍綠 - 成功狀態 */
}
```

### 顏色用法

| 用途 | 顏色 | 範例 |
|---|---|---|
| 整體背景 | `--bg` | body |
| 卡片、面板、表單 | `--paper` | card, modal, sidebar |
| Hover / 強調區塊 | `--paper-warm` | row:hover, active state |
| 主標題、主按鈕 | `--ink` | h1, primary btn |
| 內文 | `--ink-soft` | p, label |
| 副標、輔助說明 | `--ink-faint` | small, hint, en label |
| 業主版專屬區塊 | `--warm` | client-only borders |
| 警告、刪除、踩雷 | `--accent` | delete btn, alert block |

---

## 字體

```css
font-family: "Noto Serif TC", serif;       /* 中文主字體 */
font-family: "Cormorant Garamond", serif;  /* 英文襯線、副標、裝飾性英文 */
font-family: "JetBrains Mono", monospace;  /* 編號、技術標籤、CODE */
```

### 用法

**Noto Serif TC**:
- 所有中文內容
- 中文標題、品名、說明、按鈕文字

**Cormorant Garamond**:
- 英文標題
- 中文標題的英文副標(例:「材料庫 / Materials Archive」)
- 大型數字(價格)
- 章節編號(I. II. III.)

**JetBrains Mono**:
- 材料編號(GL-001)
- 技術標籤(CATEGORY, SUPPLIER...)
- 統計數字(MATERIALS 23)
- 大寫小型導覽文字

---

## 排版

### 字級層級

```
36px - 頁面主標題(僅一次)
22-28px - 區塊標題
18-22px - 卡片標題、材料品名
14-15px - 內文
12-13px - 副標、輔助
10-11px - 標籤、提示
9-10px - 等寬大寫小標(letter-spacing 0.2em)
```

### 行距與字距

- 內文 line-height: 1.5 - 1.7
- 中文 letter-spacing: 0.02 - 0.05em
- 中文標題 letter-spacing: 0.08 - 0.15em(較鬆,有氣質)
- 等寬大寫 letter-spacing: 0.18 - 0.25em(刻意拉很開)

---

## 元件規範

### 按鈕

```css
.btn {
  height: 42px;            /* 跟所有 input 等高 */
  padding: 0 16px;
  border: 1px solid var(--ink);
  background: var(--ink);
  color: var(--paper);
  letter-spacing: 0.05em;
}

.btn-ghost {
  background: transparent;
  color: var(--ink);
}

.btn.danger-btn {
  border-color: var(--accent);
  color: var(--accent);
}
```

### 輸入框

```css
.input, .select {
  height: 42px;            /* 永遠 42px,跟按鈕等高 */
  padding: 0 14px;
  border: 1px solid var(--line);
  background: var(--paper);
}
.input:focus {
  border-color: var(--ink);
  background: white;
}
```

### 標籤

```css
.field-label {
  font-size: 12px;
  color: var(--ink-soft);
  white-space: nowrap;     /* 永遠不換行 */
}
.field-label .en {
  font-family: monospace;
  font-size: 9px;
  letter-spacing: 0.18em;
  color: var(--ink-faint);
  margin-left: 8px;
  text-transform: uppercase;
}
```

---

## 互動原則

### 過渡動畫
- 主要 transition: `all 0.2s`(快速、不拖泥帶水)
- hover 抬升:`translateY(-2px)`
- 不要 spring、不要彈跳

### Hover 狀態
- 邊框變深(line → ink-soft)
- 背景變暖(paper → paper-warm)
- 不要陰影爆炸、不要放大

### 卡片
- 預設淺邊框
- Hover 邊框變深
- Selected 黑邊框 + 0 0 0 1px var(--ink) shadow

---

## 圖示原則

**用文字符號 / Unicode,不用 SVG icon font**

- `+` 新增
- `✎` 編輯
- `⎘` 複製
- `🗑` 刪除(這個是少數的彩色 emoji 例外)
- `✕` 關閉
- `←` 返回
- `→` 前往
- `⌕` 搜尋
- `✓` 確認

理由:
1. 零依賴
2. 跨平台一致
3. 符合「書本感、印刷感」(不像 Web 2.0 圖示風)

---

## 嚴格禁止

1. **斜體**:任何地方都 `font-style: normal`
2. **emoji 妝點**:除了功能性按鈕,內文絕對不放 emoji
3. **紫色 / 漸層**:不論深淺
4. **圓角過大**:最多 50% 用在頭像 / 圓形按鈕,其餘都直角或 2px
5. **陰影過重**:`0 4px 12px rgba(0,0,0,0.04)` 是上限
6. **彩色內文**:除了 accent 紅、warm 灰、success 綠,內文不用顏色強調
7. **多種字體混用**:本系統只有三種字體,不要加 Roboto / Helvetica / 自體變化

