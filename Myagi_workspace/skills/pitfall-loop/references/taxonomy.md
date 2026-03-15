# Pitfall Taxonomy (v1)

Use concise, reusable categories so weekly review can aggregate patterns.

## Recommended category values
- `code` — RTL/Verilog/腳本/程式邏輯錯誤
- `analysis` — 研究解讀、比較、推論、數據分析偏差
- `messaging` — 提醒、通知、跨渠道投遞錯誤
- `automation` — cron/sub-agent/流程自動化失誤
- `ops` — 環境、依賴、工具鏈、權限、部署問題
- `workflow` — 任務切分、時間管理、流程策略失誤
- `general` — 不好分類時暫放（每週回顧時再整理）

## Recommended taskType values
- `coding`
- `verification`
- `paper-review`
- `summary`
- `reminder`
- `cron`
- `config`
- `chat`

## Entry quality checklist
For each pitfall entry, fill at least:
1. `symptom` — 看到的現象
2. `rootCause` — 根因（不是現象）
3. `fix` — 當次修法
4. `prevention` — 下次如何避免

Without `rootCause` + `prevention`, iterative value is low.
