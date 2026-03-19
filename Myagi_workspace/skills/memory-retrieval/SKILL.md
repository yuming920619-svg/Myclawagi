---
name: memory-retrieval
description: Capture and retrieve prior conversation context using OpenClaw local memory files and native memory tools. Use when users ask to remember or recall prior context, especially natural-language cues like "記住這個", "幫我記一下", "把這件事記下來", "你還記得嗎", "之前有提過嗎", "幫我找之前聊過的", or "我們之前怎麼決定的". Default to native `memory_search` + `memory_get`; if results are unavailable, empty, or low-confidence, use the bundled lexical fallback script.
---

# Memory Retrieval

Use this skill to write, retrieve, and promote local memory in the workspace.

## Core Workflow

1. **Capture durable memory**
   - Write short notes to `memory/YYYY-MM-DD.md` for preferences, decisions, recurring schedules, confirmed plans, and important TODOs.
   - Promote only stable facts to `MEMORY.md`.
   - Use script helpers when useful:
     - `node skills/memory-retrieval/scripts/memory_append.js --text "..." --title "..." --tags a,b`
     - `node skills/memory-retrieval/scripts/memory_append.js --scope longterm --text "..." --title "..."`
   - Do not store current-task state here when it belongs in `SESSION-STATE.md`, `notes/open-loops.md`, or `notes/areas/recurring-patterns.md`.

2. **Retrieve memory**
   - Run `memory_search` first.
   - Open the best hits with `memory_get`.
   - If `memory_search` is disabled, empty, or low-confidence, run lexical fallback:
     - `node skills/memory-retrieval/scripts/memory_query.js "<query>" --top 8 --context 1`
   - Prefer newer daily notes for active work and `MEMORY.md` for stable preferences or long-term decisions.

3. **Respond with confidence**
   - Answer directly when evidence is strong.
   - If evidence is weak, say you checked and ask one short clarifying question.
   - Include source anchors when useful (`Source: memory/2026-03-10.md#L12`).

## Trigger Map

- **Remember / capture intent** → append to daily memory (or long-term if clearly stable)
  - Examples: 「記住這個」、「幫我記一下」、「把這件事記下來」、「晚點提醒我這件事」
- **Recall / search intent** → retrieve memory snippets
  - Examples: 「你還記得嗎」、「之前有提過嗎」、「幫我找一下上次聊的」、「我們之前怎麼決定的」
- **Summarize prior thread intent** → retrieve then summarize
  - Examples: 「整理一下之前的重點」、「把前面討論濃縮成三點」

If intent is ambiguous, ask one short clarification question before writing to long-term memory.

## Notes

- Treat native memory tools as the primary path.
- Treat bundled scripts as fallback helpers, not the default retrieval engine.
- Keep long-term memory curated; avoid storing secrets unless explicitly requested.

## Reference

- See `references/retrieval-playbook.md` for the compact retrieval flow and promotion rules.
