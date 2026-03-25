# GitHub 協作工作流（Vega × 你）

## 目標
你不再用 Telegram 傳程式碼；改成我直接在共享 repo 讀檔、修改、測試、commit、push。

---

## 一次性設定
1. 建立/選定一個 **private GitHub repo**。
2. 在 OpenClaw 主機把 repo clone 到 workspace（例：`/home/node/.openclaw/workspace/<repo>`）。
3. 讓我有 push 權限（PAT / SSH key 其中之一）。
4. repo 內加這三個檔案（建議）：
   - `README.md`（專案說明）
   - `RUN_TESTS.md`（怎麼跑測試）
   - `AGENTS.md`（你希望我遵守的編碼/回報規則）

---

## 日常指令（你只要這樣說）
- 「去 repo `<name>` 修 `<issue>`，跑測試後 push。」
- 「幫我做 `<feature>`，開分支，完成後給我 commit hash。」
- 「只改 `<file/path>`，不要動其他檔案。」

---

## 分支策略（預設）
- 穩定分支：`main`
- 任務分支：
  - bug：`fix/<short-topic>`
  - feature：`feat/<short-topic>`
  - refactor：`refactor/<short-topic>`

範例：`fix/ecc-decode-overflow`

---

## Commit 規則（預設）
格式：`<type>: <summary>`
- `fix:` 修 bug
- `feat:` 新功能
- `refactor:` 重構
- `docs:` 文件
- `test:` 測試

範例：`fix: correct ECC syndrome index for double-bit detection`

---

## Vega 回報格式（固定精簡）
1. 改了哪些檔案
2. 測試結果（pass/fail + 關鍵輸出）
3. commit hash / push 分支

短摘要一句收尾。

---

## 安全與保護
- 預設不 force push。
- 預設不改 CI、release、deploy 腳本（除非你明確要求）。
- 大改動（>5 檔或刪除檔案）先告知再做。

---

## 省 token 模式（預設開啟）
- 長任務用 sub-agent 背景跑。
- 中途不輪詢細節，只在完成時回報。
- 只在必要時貼長 log，其餘放附件/檔案。

---

## 推薦升級（可選）
- 加 GitHub Actions：自動跑 lint/test。
- 用 PR 模式：我推 `fix/*`，你 review 後 merge。
- 加 `ISSUE_TEMPLATE`：你下任務更快更清楚。
