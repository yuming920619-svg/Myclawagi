---
name: expense-tracker
description: "個人記帳系統：記錄消費、查詢統計、產生報表。Use when: 使用者提到消費、花費、記帳、支出，例如「午餐拉麵 180」「今天花了多少」「這週消費統計」「這個月花最多在什麼」「記一下買了 XXX」「幫我記帳」。Also triggers on: 吃了、買了、搭了、喝了 + 金額，或任何「東西+數字」的消費描述。NOT for: 預算規劃、投資理財、帳單拆分。"
---

# Expense Tracker

## 系統架構

```
expenses/
├── YYYY-MM.csv       ← 月檔（每月一份）
├── stats.sh          ← 統計腳本
├── build-summary.js  ← 產生 GitHub 用摘要 CSV
└── sync-to-github.sh ← 同步到 GitHub
```

- 資料目錄：`/home/node/.openclaw/workspace/expenses/`
- GitHub 目標：`Myclawagi/Expense tracking/`
- GitHub 同步內容：原始月檔 CSV + `summary.csv`（不再產生 Excel）

## CSV 格式

```csv
date,time,category,item,amount,note
2026-03-18,13:14,餐飲,滷味,120,午餐
```

欄位：`date`（YYYY-MM-DD）、`time`（HH:MM，台北時間）、`category`、`item`、`amount`（整數，新台幣）、`note`（可空）

## 工作流程

### 1. 記帳（使用者報消費時）

1. 解析使用者輸入，提取：品項、金額、分類、備註
   - 分類判斷：見 `references/categories.md`
   - 日期預設今天（台北時間），使用者指定則從其指定
   - 時間用當前台北時間
2. Append 到 `expenses/YYYY-MM.csv`（若檔案不存在，先建立含 header 的新檔）
3. 執行 `bash <skill_dir>/scripts/stats.sh monthly YYYY-MM` 取得當月累計
4. 用固定腳本推送摘要到 Reminder Bot（優先，避免每次重新組 shell 訊息）：

```bash
bash /home/node/.openclaw/workspace/skills/expense-tracker/scripts/send-reminder.sh \
  --item "<品項>" \
  --amount <金額> \
  --category "<分類>" \
  --note "<備註，可空>" \
  --month YYYY-MM
```

此腳本會直接從對應月份 CSV 計算：
- 當月總額
- 當月筆數
- 分類摘要（例如 `餐飲 $903 | 交通 $50`）

摘要格式：
```
📝 記帳更新
<emoji> <品項> $<金額>（<分類>）
...

📊 N月累計：$<total>（N筆）
  <分類1> $X | <分類2> $X | ...
```

若只想先驗證格式、不實際送出，可加 `--dry-run`。

5. 回覆使用者確認（簡短，含本筆紀錄 + 當月累計）

### 2. 查詢統計（使用者問花費時）

使用統計腳本：

```bash
# 今天
bash <skill_dir>/scripts/stats.sh daily [YYYY-MM-DD]

# 本週
bash <skill_dir>/scripts/stats.sh weekly [YYYY-MM-DD]

# 本月
bash <skill_dir>/scripts/stats.sh monthly [YYYY-MM]

# 自訂區間
bash <skill_dir>/scripts/stats.sh range YYYY-MM-DD YYYY-MM-DD
```

將結果整理後回覆使用者。若使用者問的是趨勢或比較（如「這個月比上個月多嗎」），跑兩次腳本比對。

### 3. 手動觸發同步（使用者要求時）

```bash
bash <skill_dir>/scripts/sync-to-github.sh
```

注意：每日 23:30 台北時間有 cron 自動同步，通常不需手動觸發。

## 多筆解析規則

使用者可能一次報多筆，例如：
- 「午餐滷味 120，飲料紅茶 25」→ 拆成 2 行
- 「早餐 蛋餅 35 + 豆漿 20」→ 拆成 2 行
- 「交通：捷運 35」→ 1 行，分類用使用者指定的「交通」

## Emoji 對應

| 分類 | Emoji |
|------|-------|
| 餐飲 | 🍱 |
| 飲料 | 🧋 |
| 交通 | 🚇 |
| 日用品 | 🛒 |
| 娛樂 | 🎮 |
| 學費 | 📚 |
| 服飾 | 👕 |
| 醫療 | 💊 |
| 其他 | 📦 |

## 注意事項

- 金額一律為新台幣整數，不需要幣別符號
- 若使用者說「大概」「約」，取最接近的整數
- 不確定分類時歸「其他」，不要猜
- 優先使用 `scripts/send-reminder.sh`（內部再呼叫 `send-reminder.js`）送 reminder，避免每次手組 `openclaw message send` 字串造成 quoting 與 approval churn
- 若不得不用 shell 組 reminder 訊息且內容含 `$金額`，不要把 `$92`、`$140` 這類字樣直接放進會經過 shell 展開的雙引號字串；應改用單引號 heredoc、跳脫成 `\$`，或其他不會被 shell 吃掉 `$` 的方式
- 送出 reminder bot 前，快速檢查一次訊息內容是否與剛寫入的 CSV 金額一致
- `<skill_dir>` 指本 skill 目錄：resolve relative to this SKILL.md's location
