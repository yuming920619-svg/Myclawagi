---
name: memory-hygiene
description: Audit and clean OpenClaw memory files. Use when comparing short-term daily memory (`memory/YYYY-MM-DD.md`) with long-term `MEMORY.md`, checking for stale or conflicting facts, deduplicating daily notes, tightening inaccurate long-term wording, or doing recurring memory housekeeping. Trigger on requests like 「整理記憶文件」, 「比對短期記憶和長期記憶」, 「去重 daily memory」, 「確保 long-term memory 精確」, 「整理記憶」, or weekly memory cleanup automation.
---

# Memory Hygiene

## Overview
Keep daily memory tidy and keep `MEMORY.md` accurate.

Prefer conservative edits:
- remove exact duplicates in daily notes
- fix verified long-term inaccuracies
- keep useful chronology and task detail in daily notes
- promote only durable, verified facts into `MEMORY.md`

Do not rewrite history just to make files shorter.

## Weekly workflow

### 1) Set the audit scope
For a routine cleanup, inspect:
- `MEMORY.md`
- recent daily files in `memory/` (default: the last 7 days worth of files)
- any directly related workspace files when verifying ground truth, such as `USER.md`, `TOOLS.md`, plugin manifests, or cron state

### 2) Scan daily memory for exact duplicates
Run `scripts/find_daily_memory_dupes.py` first.

Use it to detect:
- repeated `# YYYY-MM-DD` headers inside a single daily file
- exact repeated `## ...` sections inside a file

Treat the script output as a pointer list, not as a reason to mass-delete content without review.

### 3) Clean daily memory conservatively
When editing daily memory files:
- remove exact duplicate blocks
- keep the earliest intact copy unless a later copy is clearly the corrected one
- preserve distinct entries even if they look similar
- do not collapse multiple events into one unless they are clearly accidental duplicates

If a file has become messy but not duplicated, prefer minimal cleanup over full rewriting.

### 4) Audit long-term memory against recent evidence
Compare `MEMORY.md` with recent daily notes and current ground truth.

Common high-value checks:
- schedule / reminder facts → verify with `openclaw cron list --json`
- plugin versions / tool states → verify with local files such as `package.json`, `openclaw.plugin.json`, or config
- file existence / workflow docs → verify against the filesystem
- user facts → prefer `USER.md` as the main source unless the item truly belongs in long-term memory

If a long-term statement is directionally right but imprecise, tighten the wording instead of deleting the whole line.

### 5) Keep boundaries clean
Use these routing rules:
- `USER.md` → who the user is, preferences, workflow habits
- `MEMORY.md` → durable rules, stable schedules, verified recurring facts, important decisions
- `memory/YYYY-MM-DD.md` → daily events, task history, temporary diagnostics, one-off findings

Avoid copying the same fact into all three places unless there is a clear reason.

### 6) Verify after editing
After cleanup:
- rerun `scripts/find_daily_memory_dupes.py` on the touched daily files or recent files
- if you changed a long-term operational fact, re-check the authoritative source
- make sure no secret/token was written into any memory file

### 7) Report clearly
Default report format:
1. 3-line highlights
2. changed files
3. whether long-term memory was corrected
4. whether follow-up is needed

If no edits were needed, say so plainly.

## Guardrails
- Do not store secrets, tokens, private keys, or raw credentials in memory files.
- Do not promote uncertain facts into `MEMORY.md`.
- If daily notes and long-term memory conflict but you cannot verify the truth, keep the daily note, leave long-term memory untouched, and say the conflict needs human confirmation.
- Do not delete non-duplicate daily entries just because they feel verbose.

## Resources

### scripts/
- `scripts/find_daily_memory_dupes.py` — scan daily memory files for duplicate date headers and exact duplicate sections
