# Retrieval Playbook

## Purpose
Use this playbook when a user asks to remember or recall prior work, decisions, preferences, dates, or todos.

## Quick Workflow
1. Run semantic memory search first (`memory_search`).
2. If semantic search is disabled or low-confidence, run lexical fallback:
   - `node skills/memory-retrieval/scripts/memory_query.js "<query>" --top 8 --context 1`
3. Open the best source lines with `memory_get` (preferred) or `read`.
4. Reply with concise findings and mention source paths/lines when useful.

## Capture Template (daily memory)
Use this structure when appending to `memory/YYYY-MM-DD.md`:

- What happened (1 line)
- Why it matters (1 line)
- Next action / owner / deadline (if any)

## Promote to Long-Term Memory (MEMORY.md)
Promote only stable facts:
- enduring preferences
- repeated workflows
- major decisions
- recurring schedules

Avoid dumping transient chatter into long-term memory.
