# Errors Log

Command failures, exceptions, and unexpected behaviors.

---

## [ERR-20260312-001] edit_tool_ambiguous_match

**Logged**: 2026-03-12T17:10:00Z
**Priority**: low
**Status**: pending
**Area**: docs

### Summary
`edit` on `AUTO_TASKS.md` failed because the target text appeared more than once.

### Error
```
Found 2 occurrences of the text in /home/node/.openclaw/workspace/AUTO_TASKS.md. The text must be unique. Please provide more context to make it unique.
```

### Context
- Operation attempted: update task status in `AUTO_TASKS.md`
- Initial target string was too short / generic: `- **狀態**: enabled`
- The file had at least two matching status lines, so the tool refused to guess

### Suggested Fix
Use a longer replacement block with nearby section context so the match is unique before editing.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/AUTO_TASKS.md

---

## [ERR-20260314-001] python_missing_in_runtime

**Logged**: 2026-03-14T11:05:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to use `python` for GitHub API release scraping, but this runtime does not have a `python` executable available.

### Error
```
/bin/sh: 1: python: not found
```

### Context
- Operation attempted: fetch OpenClaw release / issue metadata from GitHub API
- Runtime already had `node`, so switching to `node -e` / `node - <<'NODE'` was the working fallback

### Suggested Fix
When doing quick API/data scraping in this workspace runtime, prefer `node` first unless Python availability has been verified.

### Metadata
- Reproducible: yes
- Related Files: none

---
