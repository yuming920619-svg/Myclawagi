# TOKEN_STRATEGY.md

## 低消耗執行策略（Codex + Claude）

1. **模型分工**
   - Primary: `openai-codex/gpt-5.4`
   - Fallback: `anthropic/claude-opus-4-6` → `anthropic/claude-sonnet-4-6` → `anthropic/claude-sonnet-4-5`
   - 只在主模型失敗（額度/認證/限流/逾時）時切到 Claude。

2. **長任務一律背景化**
   - 使用 sub-agent 執行長時間任務。
   - 主對話不做高頻進度輪詢。
   - 只在「完成 / 明確失敗」時回報結果。

3. **工具回合限制**
   - 研究類任務預設：最多 1 次搜尋 + 1 次內容抓取（必要再擴充）。
   - 先回最小可用答案，再由使用者決定是否加深。

4. **上下文控管**
   - 任務切段處理，避免單一 session 過長。
   - 任務收尾後可用 `/new` 開新 session 以降低後續輸入 token。

5. **回覆格式節流**
   - 預設「3 行重點 + 短摘要」；大段細節改檔案/附件。

## 觸發條件（何時升級）
- 僅當使用者要求「完整報告 / 深度分析 / 全量檢索」時，才放寬工具次數與輸出長度。
