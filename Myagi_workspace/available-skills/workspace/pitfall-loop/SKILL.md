---
name: pitfall-loop
description: Build a self-iteration loop that captures mistakes, retrieves similar past pitfalls, and generates prevention checklists. Use when users say things like "記一下這個坑", "這個錯誤下次不要再犯", "查一下之前踩過什麼坑", "做一份本週踩坑回顧", when starting a task and needing preflight anti-regression checks, or when the assistant detects a likely pitfall and needs to proactively ask whether to log it.
---

# Pitfall Loop

Turn mistakes into reusable process improvements.

## Natural-language trigger map

- **Capture** intent
  - "記一下這個坑" / "這次錯誤幫我存起來" / "下次不要再犯"
  - Action: append a structured entry with root cause + prevention.
- **Recall** intent
  - "查一下之前踩過什麼坑" / "這種問題以前有遇過嗎"
  - Action: query pitfall history and return top matched items.
- **Review/iteration** intent
  - "做本週踩坑回顧" / "整理可執行的避免清單"
  - Action: generate weekly review + checklist.

## Confirmation handshake (required)

When a likely pitfall appears during normal work (even without explicit user request), ask first, then write only after explicit consent.

- Proactive prompt template:
  - 「我偵測到一個可記錄的坑，是否要記進自我迭代系統？」
  - 附上草稿欄位：`title/category/taskType/rootCause/prevention`。
- Write rule:
  - User says **yes/要/記住** → run `pitfall_add.js`.
  - User says **no/先不要** → do not write.
- Data quality rule:
  - If `rootCause` or `prevention` is missing, ask one short follow-up before writing.

## Core workflow

1. **Capture one pitfall immediately after fix**
   - Command:
     - `node skills/pitfall-loop/scripts/pitfall_add.js --title "..." --category code --taskType coding --symptom "..." --rootCause "..." --fix "..." --prevention "..." --severity medium --tags ecc,verilog`
   - Rule: always fill `rootCause` and `prevention`.

2. **Before similar tasks, run recall + checklist**
   - Command:
     - `node skills/pitfall-loop/scripts/pitfall_query.js "<task keyword>" --category code --top 8 --checklist`
   - Return:
     - Top matched pitfalls
     - Preflight checklist compiled from prior prevention notes

3. **Weekly self-iteration review**
   - Command:
     - `node skills/pitfall-loop/scripts/pitfall_review.js --days 7`
   - Output includes:
     - category/taskType/severity distribution
     - repeated root causes
     - next-week action list

## Files and outputs

- Source ledger: `memory/pitfalls.jsonl`
- Daily context log: `memory/YYYY-MM-DD.md` (auto-appended by `pitfall_add` unless `--skip-daily`)
- Weekly review output: `memory/pitfall-reviews/YYYY-MM-DD-review.md`

## Classification guidance

Use `references/taxonomy.md` for category and taskType values.

## Practical policy

- Prefer short, concrete entries over long narratives.
- If category is unclear, use `general`, then reclassify during weekly review.
- For recurring high-severity pitfalls, add a prevention checklist line to AGENTS.md or relevant workflow docs.
- Treat these as likely pitfall cues (ask for confirmation): repeated tool error, wrong-channel delivery, rework caused by unclear requirements, verification mismatch, avoidable analysis mistake.
