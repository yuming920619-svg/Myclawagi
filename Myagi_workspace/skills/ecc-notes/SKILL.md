---
name: ecc-notes
description: "整理 Shu Lin《Error Control Coding: Fundamentals and Applications》教科書章節讀書筆記、weekly meeting 報告草稿，或處理 cyclic codes / BCH / Reed-Solomon / convolutional codes 等本書主題時使用。當使用者說『整理某章』、『繼續做筆記』、『幫我準備 meeting 報告』、『把這章做成中文筆記』，或要把掃描版課本內容轉成結構化筆記時，使用此 skill。"
---

# ECC Notes

把 Shu Lin《Error Control Coding》掃描版章節整理成**結構化繁中筆記**；若環境允許，再輸出成符合 lab meeting 格式的 `.docx`。

## 核心事實

- 原書頁碼與 PDF 頁碼偏移：**書本頁碼 + 19 = PDF 頁碼**
- 常用章節速查：
  - Ch1 Coding for Reliable Digital Transmission — p.1
  - Ch2 Introduction to Algebra — p.15
  - Ch3 Linear Block Codes — p.51
  - Ch4 Cyclic Codes — p.85
  - Ch5 Error-Trapping Decoding for Cyclic Codes — p.125
  - Ch6 BCH Codes — p.141
  - Ch7 Majority-Logic Decodable Codes — p.183
- 這本書常見來源是**掃描版 PDF**，通常沒有文字層；不要假設可以直接抽文字。

## 這個 workspace 的配置重點

- **不要依賴固定 PDF 路徑。** 匯入版本寫死 `/mnt/user-data/uploads/error-control-coding-by-shu-lin.pdf`，但此 workspace 不保證存在；把 PDF 路徑視為執行時輸入。
- **不要依賴 `view` tool。** 在 OpenClaw 這裡，優先用 `image` 工具分析轉出的頁面圖片；必要時也可用 `read` 開圖片。
- **不要預設 docx helper skill 已安裝。** 匯入版本引用 `/mnt/skills/public/docx/SKILL.md`，此 workspace 不保證存在。若使用者明確要求 `.docx`，先讀 `references/report-format.md`，再檢查是否有可用的 docx 產生流程；沒有就先交付完整 markdown/draft，並明講缺的依賴。

## 工作流程

### 1. 確認範圍與輸出

先確認：
- 要整理哪一章 / 哪幾節
- 是讀書筆記、meeting 報告，還是特定主題整理
- 是否需要 meeting 參數（Meeting 次數、日期、Tape-out 次數）
- 最終輸出是 markdown 還是 `.docx`

如果使用者只說「繼續下一章」或「整理下一節」，先從當前對話或已有檔案推定範圍；不夠明確再問。

### 2. 取得來源 PDF 或頁面圖片

優先順序：
1. 使用者本輪上傳的 PDF / 截圖
2. workspace 或近期附件中可定位到的書本 PDF
3. 若找不到，直接請使用者上傳 PDF 或目標頁面截圖

若使用者提供的是頁面截圖而非整本 PDF，可直接跳到閱讀步驟。

### 3. 決定頁面範圍

如果使用者提供的是**書本頁碼**，換算成 PDF 頁碼：
- `pdf_page = book_page + 19`

整理時記得保留：
- 章標題 / 節標題
- 起訖頁
- 重要定義、定理、推導、範例、圖表

### 4. 轉頁面成圖片（若來源是 PDF）

因為通常是掃描版 PDF，先把目標頁面轉成圖片，再逐頁閱讀。

原則：
- 先確認本機可用的 PDF→image 方法，再執行
- 不要把工具寫死成某個一定存在的 library
- 若本機無法可靠轉圖，就改請使用者提供頁面截圖

### 5. 逐頁閱讀，不能跳頁

每一頁都要實際看過，不可憑記憶補內容。

閱讀重點至少包含：
- 定義（Definition）
- 定理（Theorem）與 proof idea / proof sketch
- 重要公式與符號意義
- 範例（Example）的完整計算流程
- 表格中的代表性資訊
- 圖（Figure）與電路圖的重點描述

若 OCR / 視覺辨識有不確定處：
- 明確標示不確定
- 必要時交叉讀同頁上下文
- 不要硬猜公式或數字

### 6. 產出筆記

寫作要求：
- **繁中為主，術語保留英文**
- 用課本原本的節號（如 4.3, 4.4）做主結構
- 重要定理先寫結論，再補 proof idea
- 範例要保留計算步驟，不能只寫答案
- 公式需說明變數意義與用途
- 若圖表無法直接重製，至少文字描述它表達了什麼

### 7. 輸出模式

#### Markdown / 筆記草稿（預設）

優先產出完整、可讀、可直接拿去改的 markdown 筆記。

#### `.docx`（使用者明確要求時）

1. 先讀 `references/report-format.md`
2. 依格式需求組織內容
3. 若本機沒有現成 docx 產生工具鏈 / 模板 / 驗證器：
   - 不要假裝可以穩定輸出 `.docx`
   - 先產出 **docx-ready** 的 markdown / structured draft
   - 清楚告知缺少的依賴，再問是否要補模板或改走其他輸出

## 品質門檻

- 不可省略關鍵推導步驟
- 不可只寫空泛摘要，要保留技術內容
- 不可杜撰未實際讀到的公式、數值、例題步驟
- 若只讀到部分頁面，要明講整理範圍
- 若本章與 BCH / cyclic code 等主題有前後文依賴，可在前言補一小段銜接

## 參考檔

- 詳細報告格式與字體 / 表格規範：`references/report-format.md`
