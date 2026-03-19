# Retrieval Playbook

## Purpose
Use this playbook when a user asks to remember or recall prior work, decisions, preferences, dates, or todos.

## Quick Workflow
1. Run native semantic retrieval first with `memory_search`.
2. Open the best source lines with `memory_get`.
3. If search is disabled, empty, or low-confidence, run lexical fallback:
   - `node skills/memory-retrieval/scripts/memory_query.js "<query>" --top 8 --context 1`
4. Reply with concise findings and mention source paths/lines when useful.
5. If the conversation adds a new durable fact, append it to daily memory before ending the task.

## Memory Routing
- **`memory/YYYY-MM-DD.md`** → daily raw capture
- **`MEMORY.md`** → stable long-term facts only
- **`SESSION-STATE.md`** → active task state / blockers / next step
- **`notes/open-loops.md`** → deferred follow-ups
- **`notes/areas/recurring-patterns.md`** → repeated workflows worth standardizing

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

Avoid dumping transient chatter or current-task scratch state into long-term memory.
