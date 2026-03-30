# ECC Notes — Report Format Reference

這份參考檔保存匯入 skill 的報告格式要求，供需要輸出 lab meeting 報告 / `.docx` 時使用。

## 使用時機

在使用者**明確要求** Word / `.docx` / meeting 報告版式時讀這份檔；若只是一般章節筆記，先不要載入。

## 基本目標

輸出符合實驗室 weekly meeting 風格的報告文件：
- A4
- 封面頁 + 內容頁
- 內容頁以**多 row 表格**分節，不要把整份內容塞進單一 cell
- 中英混排：中文說明、英文術語

## 頁面設定

- A4（width: 11906, height: 16838 DXA）
- 邊距：上下左右各約 1200 DXA

## Header / Footer

### Header
- 左：`Meeting{N}`
- 右：`育民`
- 字體：Arial / 標楷體
- 18pt（size: 36）
- **不可粗體**

### Footer
- 左：`YYYY-MM-DD  T{N}`
- 右：`P{自動頁碼}`
- 字級：22pt（size: 44）
- 不粗體

## 封面頁格式

封面頁不放在內容大表格中，直接擺頁面元素。

典型內容：
- `壹、研究目的：研究 Error Control Code`
- `貳、研究方法：閱讀課本`
- `參、參考資料:`
- 目錄表

### 封面頁要求
- 「壹貳參」與後方文字：**12pt、不可粗體**
- 目錄表：**不要網底顏色 / shading**
- 表頭「內容」「頁碼」：**不可粗體**

## 內容頁主結構（最重要）

內容頁使用**一個大 Table**，每個大區塊各佔一個獨立 row：

1. Row 1：書名 + 章名（置中粗體）
2. Row 2：Section 4.3（或對應第一節）的完整內容
3. Row 3：Section 4.4 的完整內容
4. Row 4：Section 4.5 的完整內容
5. 依此類推

### 關鍵規則
- **每個 4.X / 5.X / 6.X 小節都要獨立成 row**
- 不要把所有節標題和內容都塞進同一個大 cell
- 用框線分隔各 section

## 表格樣式通則

所有表格（封面目錄表、內容大表格、內文中的小表格）一律：
- 無網底顏色
- 黑色細框線
- 黑色文字
- 不做灰底標頭、不做交替底色

## 字體規範（最重要）

### 四槽字體設定

所有一般 TextRun 都用：

```javascript
font: {
  ascii: "Times New Roman",
  eastAsia: "標楷體",
  hAnsi: "Times New Roman",
  cs: "Times New Roman"
}
```

理由：
- 英文走 Times New Roman
- 中文走標楷體
- 不要把四槽都設成標楷體
- 不要把 eastAsia 設成 Times New Roman
- 不要用 `DFKai-SB` 取代 `標楷體`

### 字級對照

| 用途 | 字級 | size | 粗體 |
|---|---:|---:|---|
| 封面頁（壹貳參） | 12pt | 24 | 否 |
| 內文段落 | 12pt | 24 | 否 |
| 書名 `Error Control Coding` | 18pt | 36 | 是 |
| 章名 `Chapter 4: Cyclic Codes` | 15pt | 30 | 是 |
| 節標題（如 `4.3 Encoding...`） | 16pt | 32 | 是 |
| 小節標題（如 `1. 非系統化編碼`） | 13pt | 26 | 是 |
| 數學公式 | 12pt | 24 | 否（可斜體） |
| Header `Meeting{N}` | 18pt | 36 | 否 |
| Footer 日期/頁碼 | 22pt | 44 | 否 |

### 數學公式字體

公式可用 Cambria Math，但 eastAsia 仍保留標楷體：

```javascript
font: {
  ascii: "Cambria Math",
  eastAsia: "標楷體",
  hAnsi: "Cambria Math",
  cs: "Cambria Math"
}
```

### Header 字體

```javascript
font: {
  ascii: "Arial",
  eastAsia: "標楷體",
  hAnsi: "Arial",
  cs: "Arial"
}
```

## 顏色與樣式

- 所有文字一律黑色：`000000`
- 粗體只用在：
  - 書名 / 章名
  - 節標題 / 小節標題
  - 定理結論
  - 最終答案
  - 重要概念
- 斜體可用在：
  - `Proof 概要：` 這類引導語
- **Header 與封面頁壹貳參不可粗體**

## 內容寫作規範

1. **中英夾雜**：專有名詞保留英文，說明用中文
2. **定理**：先寫結論，再補 `Proof 概要`
3. **範例**：完整列出計算過程，最終結果可粗體
4. **公式**：置中，並說明符號意義
5. **圖表**：若無法原樣重現，至少文字描述其功能與重點

## 驗證與輸出

原匯入 skill 假設可用：

```bash
python3 /mnt/skills/public/docx/scripts/office/validate.py output.docx
cp output.docx /mnt/user-data/outputs/[檔名].docx
```

但這個 workspace **不保證有上述 validator / docx helper**。

### 因此在 OpenClaw 的建議流程

- 若有可用 docx 工具鏈：照格式輸出 `.docx`
- 若沒有：先產出完整的 **docx-ready markdown / structured draft**
- 不要假裝 `.docx` 已經能穩定生出來

## 檔名命名規則

```text
Ch{章號}_{章節英文名}_Sec{起始節}-{結束節}_Notes.docx
```

例如：
- `Ch4_Cyclic_Codes_Sec4.3-4.5_Notes.docx`
- `Ch6_BCH_Codes_Sec6.1-6.2_Notes.docx`

## 原匯入 skill 的硬性提醒（保留）

- PDF 若是掃描版，必須先轉圖片再閱讀
- 範例計算過程不可省略
- 內文字級一律 12pt，不是 10.5pt
- 所有表格都不要網底顏色
- 內容頁的各小節必須拆成不同 table row
