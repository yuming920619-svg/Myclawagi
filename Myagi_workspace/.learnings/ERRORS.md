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

## [ERR-20260319-001] openclaw_cron_run_force_removed

**Logged**: 2026-03-19T03:27:03Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to manually trigger a cron job with `openclaw cron run <id> --force`, but this OpenClaw version no longer supports the `--force` flag.

### Error
```
error: unknown option '--force'
```

### Context
- Operation attempted: manually run a cron job immediately for delivery testing
- Command used: `openclaw cron run 84679a51-7304-43ed-b702-52b4b0d4eed1 --force`
- Correct current usage is `openclaw cron run <id>` (optionally with `--expect-final`)

### Suggested Fix
Before manually testing cron jobs, check `openclaw cron run --help` when relying on older command memory; use `openclaw cron run <id> --expect-final` for immediate debug runs.

### Metadata
- Reproducible: yes
- Related Files: none

---

## [ERR-20260320-001] git_push_non_fast_forward

**Logged**: 2026-03-20T06:51:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to push a new GitHub commit, but remote `main` had a newer commit and rejected the push as non-fast-forward.

### Error
```
To https://github.com/yuming920619-svg/Myclawagi.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/yuming920619-svg/Myclawagi.git'
```

### Context
- Operation attempted: push `Special Topic Discussion/2026-03-20_觀眾評分表草稿.md` to `github.com/yuming920619-svg/Myclawagi`
- Local branch had commit `9deab90`
- Remote had advanced from `6fccef2` to `21f7ee4`
- Resolved by `git fetch` + `git pull --rebase origin main` + `git push origin main`

### Suggested Fix
Before pushing to this repo, do a quick `git fetch` or be ready to `pull --rebase` if the remote may have changed from another device/session.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/Myclawagi/Special Topic Discussion/2026-03-20_觀眾評分表草稿.md

---

## [ERR-20260320-002] exec_default_shell_pipefail

**Logged**: 2026-03-20T08:02:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
A multiline `exec` command failed because the default shell was `/bin/sh`, which does not support `set -o pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Operation attempted: append expense rows and run monthly stats in one `exec` call
- Initial command started with `set -euo pipefail` directly
- Re-running via `bash -lc '...'` worked as expected

### Suggested Fix
When a command relies on Bash features (`pipefail`, arrays, stricter shell semantics), wrap it with `bash -lc '...'` instead of assuming the default `exec` shell is Bash.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/skills/expense-tracker/scripts/stats.sh

---

## [ERR-20260320-003] expense_sync_rebase_after_stage

**Logged**: 2026-03-20T11:46:00Z
**Priority**: medium
**Status**: resolved
**Area**: infra

### Summary
The expense sync script staged changes before `git pull --rebase`, causing Git to reject the rebase when `Expense tracking/` had pending modifications.

### Error
```
error: cannot pull with rebase: Your index contains uncommitted changes.
error: please commit or stash them.
```

### Context
- Operation attempted: push updated expense CSVs to `github.com/yuming920619-svg/Myclawagi`
- Old script order was: `git fetch` → `git add` → `git pull --rebase`
- Working recovery path was: `git pull --rebase --autostash origin main` → `git add` → `git commit` → `git push`

### Suggested Fix
In sync scripts, rebase first (or use `--autostash`) before staging/committing generated files.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/expenses/sync-to-github.sh, /home/node/.openclaw/workspace/skills/expense-tracker/scripts/sync-to-github.sh

### Resolution
- **Resolved**: 2026-03-20T11:46:00Z
- **Notes**: Updated both sync scripts to use `git pull --rebase --autostash origin main` before `git add`, then commit/push.

---

## [ERR-20260320-004] cron_no_deliver_requires_isolated

**Logged**: 2026-03-20T12:05:00Z
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
Tried to create reminder cron jobs with `--no-deliver` while not using an isolated session, and OpenClaw rejected the command.

### Error
```
Error: --announce/--no-deliver require --session isolated.
```

### Context
- Operation attempted: create one-shot reminder cron jobs for the user's 2026-04-28 meeting reminders
- Initial command mixed delivery flags in a way OpenClaw does not allow for non-isolated jobs
- Working pattern was: `--session isolated --message ... --announce --channel telegram --account reminder --to ...`

### Suggested Fix
For reminder-bot cron notifications, use isolated jobs with `--message` + `--announce` and explicit delivery routing instead of mixing `--no-deliver` into non-isolated reminder jobs.

### Metadata
- Reproducible: yes
- Related Files: none

### Resolution
- **Resolved**: 2026-03-20T12:05:00Z
- **Notes**: Recreated all three reminder jobs using isolated announce delivery to Telegram reminder bot.

---
