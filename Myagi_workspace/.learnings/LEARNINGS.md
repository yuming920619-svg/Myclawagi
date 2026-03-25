# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

---


## [LRN-20260318-001] correction

**Logged**: 2026-03-18T09:32:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
When the user asks about gpt-5-mini / gpt-5-nano, do not answer with gpt-5.4-mini / gpt-5.4-nano. Confirm the exact model family first.

### Details
The user asked for pricing and pros/cons of gpt-5-mini and gpt-5-nano. I incorrectly answered with gpt-5.4-mini and gpt-5.4-nano information. This happened because I mixed the OpenClaw catalog naming (gpt-5-mini / gpt-5-nano) with newer OpenAI docs that mention gpt-5.4-mini / gpt-5.4-nano.

### Suggested Action
Before answering model/pricing questions, restate the exact model IDs requested and verify the provider naming in current docs/catalog. If there is a naming mismatch between OpenClaw and provider docs, call it out explicitly instead of assuming they are interchangeable.

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: models, pricing, correction, openai, openclaw

---

## [LRN-20260319-002] correction

**Logged**: 2026-03-19T11:01:18Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
記帳流程不只要回覆使用者，還必須同步發送 reminder bot 通知；不能只完成本地記帳與聊天回覆。

### Details
使用者再次提醒「每次記帳都要在 reminder 通知」。我這次雖然成功把消費寫入 CSV、算出當月統計並回覆使用者，但漏掉了 skill 明定的 reminder bot 推送步驟。這代表我在執行已知固定流程時，只做了聊天面上的確認，沒有完整執行整個記帳工作流。

2026-03-24 又再次重複發生一次：處理 3/22 午餐「拉亞漢堡 炸雞麵+奶茶+雞塊 257」時，仍然只完成了寫入與回覆，沒有發 reminder 通知，代表這已不是單次遺漏，而是固定流程執行沒有被我確實收尾。

### Suggested Action
之後只要觸發 expense-tracker 記帳流程，就要把步驟視為固定三件事：1) 寫入 CSV，2) 更新/查統計，3) 立即發送 reminder bot 摘要通知。回覆使用者前先確認三步都完成。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/expense-tracker/SKILL.md, /home/node/.openclaw/workspace/expenses/2026-03.csv
- Tags: expense, reminder, workflow, correction
- Recurrence-Count: 2
- First-Seen: 2026-03-19
- Last-Seen: 2026-03-24

---

## [LRN-20260319-003] best_practice

**Logged**: 2026-03-19T16:14:59Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
處理台北時間的記帳資料時，不要手動做 UTC+8 小時換算後直接拼字串，避免產生 `24:xx` 這種無效時間。

### Details
在記錄使用者的 3/19 午餐帳目時，我把 UTC 16:14 直接手動加 8 小時後寫成 `24:14`，造成 CSV 內出現非法 HH:MM。之後已修正成合理時間，但根本問題是不能靠手算時間字串。

### Suggested Action
之後凡是需要台北時間，一律用可靠的時區換算方式（例如 `TZ=Asia/Taipei` 或現成時間工具），不要手動做 `+8` 再自己格式化。

### Metadata
- Source: conversation
- Related Files: /home/node/.openclaw/workspace/expenses/2026-03.csv
- Tags: timezone, expense, formatting, best_practice

---

## [LRN-20260319-001] correction

**Logged**: 2026-03-19T03:08:00Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
When fallback configuration is discussed, verify the live config file before treating earlier memory notes as the current truth.

### Details
I initially reported a mismatch between remembered fallback history and the current model failover chain. The user clarified that the change was intentional: they manually simplified the disaster-recovery chain and consider Claude Sonnet 4.6 sufficient, so Sonnet 4.5 is no longer needed in the main fallback order.

### Suggested Action
For model/fallback questions, present the live config as authoritative and treat memory entries as historical context only. If there is a difference, explicitly say it may reflect a deliberate later change instead of implying drift.

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/openclaw.json, memory/2026-03-19.md
- Tags: fallback, models, correction, config, memory

---

## [LRN-20260320-001] correction

**Logged**: 2026-03-20T06:59:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
專題討論表單評論不能只寫「約 30 字」；若表單要求至少 30 字，就要把最低字數當成硬限制，生成更保險的長度。

### Details
使用者明確提醒「表單要求的是至少 30 字」。我先前在 special-topic-discussion skill 中把輸出描述成「around 30 Chinese characters」與「roughly 30」，這種寫法容易讓生成結果卡在門檻邊緣，造成表單不通過或需要手動補字。

### Suggested Action
之後遇到這類表單，先抓最低字數要求；若要求至少 30 字，評論目標應放在略高於門檻的安全區間，例如 32–45 字，而不是貼著 30 字生成。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md
- Tags: forms, length-limit, special-topic-discussion, correction

---

## [LRN-20260320-002] correction

**Logged**: 2026-03-20T07:20:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
專題討論流程中，把結果同步到 GitHub 不應視為可選收尾；對這位使用者來說，這是固定流程的一部分。

### Details
使用者明確提醒「要更新到 github，請注意這必須是固定流程」。這表示 special-topic-discussion workflow 不只是在需要時才存檔，而是只要已生成可用稿、尤其在同一天追加新講者時，就應預設更新既有草稿並推送到 `Myclawagi/Special Topic Discussion/`，除非使用者明確要求先不要推。

### Suggested Action
將 GitHub 同步寫成 special-topic-discussion skill、USER.md、MEMORY.md 內的固定預設規則；後續執行此流程時，把 push 視為默認步驟，不再等使用者每次額外提醒。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/USER.md, /home/node/.openclaw/workspace/MEMORY.md
- Tags: workflow, github, special-topic-discussion, correction

---
