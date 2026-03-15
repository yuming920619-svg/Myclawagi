---
name: memory-retrieval
description: Capture and retrieve prior conversation context from MEMORY.md and memory/*.md. Use when users ask to remember or recall prior context, especially natural-language cues like "記住這個", "幫我記一下", "把這件事記下來", "你還記得嗎", "之前有提過嗎", "幫我找之前聊過的". Also use when semantic memory_search is unavailable and lexical fallback retrieval is needed.
---

# Memory Retrieval

Store important context in local memory files and retrieve it with a reliable fallback search path.

## Core Workflow

1. **Capture memory when new durable info appears**
   - Use for: user preferences, decisions, recurring schedules, confirmed plans, important TODOs.
   - Write short notes to `memory/YYYY-MM-DD.md`.
   - Promote stable facts to `MEMORY.md`.
   - Use script helper when useful:
     - `node skills/memory-retrieval/scripts/memory_append.js --text "..." --title "..." --tags a,b`
     - `node skills/memory-retrieval/scripts/memory_append.js --scope longterm --text "..." --title "..."`

2. **Retrieve memory with semantic-first, lexical-fallback**
   - Run `memory_search` first.
   - If search is disabled/empty/low-confidence, run:
     - `node skills/memory-retrieval/scripts/memory_query.js "<query>" --top 8 --context 1`
   - Open best snippets with `memory_get` (preferred) or `read`.

3. **Respond with confidence and sources**
   - If evidence is strong, answer directly.
   - If evidence is weak, say you checked and ask a clarifying question.
   - Include source anchors when useful (`Source: memory/2026-03-10.md#L12`).

4. **Keep memory clean**
   - Keep daily files detailed but concise.
   - Keep `MEMORY.md` curated and stable.
   - Avoid storing secrets unless explicitly requested.

## Natural-Language Trigger Map

Use these intent phrases as routing cues.

- **Remember/capture intent** → append to daily memory (or long-term if clearly stable)
  - Examples: 「記住這個」、「幫我記一下」、「把這件事記下來」、「晚點提醒我這件事」
- **Recall/search intent** → retrieve memory snippets
  - Examples: 「你還記得嗎」、「之前有提過嗎」、「幫我找一下上次聊的」、「我們之前怎麼決定的」
- **Summarize prior thread intent** → retrieve then summarize
  - Examples: 「整理一下之前的重點」、「把前面討論濃縮成三點」

If intent is ambiguous, ask one short clarification question before writing to long-term memory.

## Retrieval Heuristics

- Search by intent terms first (e.g., “模型偏好”, “排程”, “選課提醒”, “BCH 測試結果”).
- Search by concrete anchors second (dates, project names, DOI/title fragments).
- Prefer newer daily notes for active work and `MEMORY.md` for stable preferences.

## Reference

- See `references/retrieval-playbook.md` for compact templates and promotion rules.
