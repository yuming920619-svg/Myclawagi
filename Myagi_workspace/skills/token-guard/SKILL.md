---
name: token-guard
description: Monitor model quota usage and provide threshold alerts with strategy hints. Use when users ask about remaining quota, token budget, usage status, or whether to switch models. Also used during heartbeat checks for silent quota monitoring. Triggers on phrases like "還剩多少額度", "token 夠不夠", "要不要切模型", "額度快用完了嗎", "quota", "usage left", "budget check".
---

# Token Guard

Monitor rolling quota usage, alert on threshold crossings, and suggest model-switching strategies.

## Data Source

Call `session_status` to get current quota info. The output contains:

```
📊 Usage: 5h XX% left ⏱Xh Xm · Week XX% left ⏱Xd Xh
```

Extract two numbers:
- **5h window remaining %**
- **Week remaining %**

## On-Demand Check

When the user asks about quota / remaining budget / whether to switch models:

1. Call `session_status`
2. Parse the `Usage` line
3. Report:
   - Current model
   - 5h window: remaining % + reset time
   - Week: remaining % + reset time
   - Alert level (see Thresholds below)
   - Strategy hint (see Strategy Hints below)

Keep the report short: 3–5 lines max unless the user asks for detail.

## Thresholds

### 5-hour window

| Remaining | Level | Action |
|-----------|-------|--------|
| >30% | 🟢 OK | No alert |
| 15–30% | 🟡 Low | Mention it briefly |
| 5–15% | 🟠 Warning | Suggest shorter responses or switching model |
| <5% | 🔴 Critical | Strongly recommend switching to backup model |

### Weekly quota

| Remaining | Level | Action |
|-----------|-------|--------|
| >25% | 🟢 OK | No alert |
| 15–25% | 🟡 Low | Mention days remaining vs quota |
| 5–15% | 🟠 Warning | Recommend switching to backup for non-critical tasks |
| <5% | 🔴 Critical | Recommend backup model as primary until reset |

## Strategy Hints

Based on the user's known token strategy (Codex primary, Claude backup):

### 🟢 OK
- No action needed.

### 🟡 Low
- 可以繼續用 Codex，但長任務考慮用 Claude
- 開新 session 可降低上下文成本

### 🟠 Warning
- 建議研究/分析類任務切 Claude
- Codex 只留給需要 Codex 特有能力的任務
- 縮短工具回合、減少多輪搜尋

### 🔴 Critical
- 建議暫時以 Claude 為主力
- Codex 只用於極短任務
- 等 reset 後再恢復正常使用

## Heartbeat Integration

During heartbeat checks, silently call `session_status` and check quota levels:

- **🟢/🟡**: Do not mention quota (keep heartbeat quiet).
- **🟠 Warning**: Add one line to heartbeat response: e.g. "⚠️ 週額度剩 XX%，非關鍵任務建議切 Claude"
- **🔴 Critical**: Surface as priority alert in heartbeat response.

Do NOT report quota every heartbeat. Only surface when level is 🟠 or worse.

## Cron Integration (optional)

If the user wants a daily quota summary, set up a cron job:

```bash
openclaw cron add \
  --name "daily-quota-check" \
  --cron "0 22 * * *" \
  --tz "Asia/Taipei" \
  --session isolated \
  --message "用 token-guard skill 檢查今天的額度使用狀況，簡短報告。" \
  --announce \
  --channel telegram \
  --to "<user-id>" \
  --model sonnet
```

Use a lightweight model for the cron check itself to avoid wasting quota.

## Anti-Spam Rules

- On-demand check: always respond when asked.
- Heartbeat: only surface at 🟠 or 🔴.
- Do not repeat the same alert level within the same session unless asked.
- After alerting once per level, only re-alert if the level worsens.
- Never auto-switch models. Only suggest.

## Quick Reference

```
User: "額度還夠嗎"
→ session_status → parse → "🟡 週額度剩 18%，還有 3 天重置。長任務建議切 Claude。"

User: "現在用什麼模型"
→ session_status → "目前 openai-codex/gpt-5.4，5h 剩 72%，週剩 14%。"

Heartbeat (week 8% left):
→ "⚠️ Codex 週額度剩 8%，建議非關鍵任務暫切 Claude，週四重置。"

Heartbeat (week 40% left):
→ (不提額度，正常回 HEARTBEAT_OK 或處理其他事項)
```
