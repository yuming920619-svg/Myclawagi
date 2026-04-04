# Errors Log

Command failures, exceptions, and unexpected behaviors.

---

## [ERR-20260331-001] exec_default_shell_pipefail

**Logged**: 2026-03-31T19:00:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
An `exec` script used `set -euo pipefail` without invoking bash, but the default shell was `/bin/sh`, which rejected `pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Operation attempted: cron-driven workspace sync script for GitHub backup
- Initial command assumed bash semantics in the default `exec` shell
- Immediate fix was to wrap the script with `bash -lc '...'

### Suggested Fix
When using bash-only shell options or syntax in `exec`, explicitly invoke `bash -lc` instead of assuming the default shell supports them.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md

---

## [ERR-20260403-001] todo_plugin_install_pipefail_again

**Logged**: 2026-04-03T11:29:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
While installing the `todo-api-tools` plugin, an `exec` command again assumed bash semantics in the default gateway shell and failed before running any install steps.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Operation attempted: extract tar, install local plugin, restart gateway, verify status
- Command started with `set -euo pipefail` directly under gateway `exec`
- The default shell was `/bin/sh`, so the script aborted before plugin installation

### Suggested Fix
When using bash-only options or syntax in gateway `exec`, wrap the whole script with `bash -lc '...'` or avoid `pipefail` and other bash-only features.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md, /home/node/.openclaw/workspace/TOOLS.md
- See Also: ERR-20260331-001

---

## [ERR-20260403-002] bash_printf_leading_dash_option

**Logged**: 2026-04-03T11:31:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
A follow-up gateway `exec` command switched to `bash`, but `printf "--- ..."` still failed because bash builtin `printf` treated the leading `--` in the format string as an option.

### Error
```
bash: line 6: printf: --: invalid option
printf: usage: printf [-v var] format [arguments]
```

### Context
- Operation attempted: extract and install `todo-api-tools`, restart gateway, verify status
- Script used `printf "--- extracted ---\n"`
- In bash builtin `printf`, a format string starting with `-` can be parsed as an option unless `--` or a safe format string is used

### Suggested Fix
Use `printf '%s\n' '--- extracted ---'` or `printf -- '--- extracted ---\n'` when the first format argument begins with `-`.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md
- See Also: ERR-20260403-001

---

## [ERR-20260329-001] telegram_commentary_trace_leak

**Logged**: 2026-03-29T16:47:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
During a Telegram live chat, internal commentary / tool-call traces (including raw exec JSON and planning text) were surfaced to the user while the agent was busy.

### Error
```
User saw a series of internal execution-command messages in Telegram that should have remained internal.
Session history showed commentary-phase assistant text/tool payloads interleaved into the live chat timeline.
```

### Context
- Operation attempted: create school-deadline reminders via docs lookup + `openclaw cron add`
- Observed behavior: user received multiple internal-looking command messages before the final human reply
- Impact: confusing UX and exposed implementation detail in a direct chat

### Suggested Fix
For Telegram live chats, keep commentary empty/minimal during tool work; prefer direct tool calls with a single final user-facing reply. If deeper platform investigation happens later, inspect why commentary-phase messages are being surfaced on this channel/session.

### Metadata
- Reproducible: unknown
- Related Files: /home/node/.openclaw/workspace/TOOLS.md

---

## [ERR-20260325-001] rg_missing_in_runtime

**Logged**: 2026-03-25T16:43:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to use `rg` for quick file discovery, but this runtime does not have ripgrep installed.

### Error
```
sh: 1: rg: not found
```

### Context
- Operation attempted: locate OpenClaw config / LINE-related files with `find ... | rg ...`
- Runtime fallback was to use `openclaw status --all` and direct file reads instead

### Suggested Fix
In this workspace runtime, prefer `grep` / `find` / direct known paths unless `rg` availability has been verified.

### Metadata
- Reproducible: yes
- Related Files: none

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

## [ERR-20260323-001] web_search_missing_brave_api_key

**Logged**: 2026-03-23T18:08:30Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to use `web_search`, but this OpenClaw environment does not currently have a Brave Search API key configured.

### Error
```
web_search (brave) needs a Brave Search API key. Run `openclaw configure --section web` to store it, or set BRAVE_API_KEY in the Gateway environment.
```

### Context
- Operation attempted: verify current public docs / web info for Claude Code product differences
- Tool call failed before returning any search results because Brave API credentials were missing
- Fallback for lightweight doc lookup can be direct `web_fetch` on known URLs when search is unnecessary

### Suggested Fix
If web search is needed again in this environment, configure Brave Search (`openclaw configure --section web`) or set `BRAVE_API_KEY`; otherwise prefer direct `web_fetch` when the target docs URL is already known.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/TOOLS.md

---

## [ERR-20260324-002] remote_browser_target_ws_uses_loopback_host

**Logged**: 2026-03-24T11:33:30Z
**Priority**: low
**Status**: resolved
**Area**: infra

### Summary
Direct CDP page-target connections to the remote browser sandbox failed because `/json/new` returned a loopback `webSocketDebuggerUrl` (`ws://127.0.0.1/...`) that is not reachable from this workspace.

### Error
```
Error: websocket open failed
```

### Context
- Operation attempted: perform a real browser action test against the configured remote browser sandbox
- Initial approach used the page target's `webSocketDebuggerUrl` exactly as returned by the sandbox
- The target metadata used `127.0.0.1`, which points at the browser container itself instead of the service hostname visible from this workspace

### Suggested Fix
When scripting CDP directly against this sandbox, rewrite the target websocket host from `127.0.0.1` to `openclaw-sandbox-browser-posess:9222` before opening the socket.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/TOOLS.md

### Resolution
- **Resolved**: 2026-03-24T11:35:00Z
- **Notes**: Rewriting the target websocket host to `openclaw-sandbox-browser-posess:9222` allowed successful navigation to `https://example.com`, title extraction, and screenshot capture.

---

## [ERR-20260325-001] sh_pipefail_not_supported

**Logged**: 2026-03-25T03:00:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to run a shell script with `set -euo pipefail` via `exec`, but the default `/bin/sh` in this runtime does not support `pipefail`.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Operation attempted: cron-driven workspace sync script executed through `exec`
- Assumed bash-style shell options were available under `/bin/sh`
- The fix is to invoke `bash -lc '...'` explicitly when `pipefail` is needed

### Suggested Fix
For multi-step scripts run through `exec`, use `bash -lc` (or avoid `pipefail`) instead of assuming `/bin/sh` supports bash options.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md

---

## [ERR-20260325-003] bundled_line_plugin_crashes_on_2026_3_22

**Logged**: 2026-03-25T16:10:30Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
After upgrading OpenClaw to 2026.3.22, the LINE plugin still fails to load with `TypeError: Cannot redefine property: isSenderAllowed` even after removing the old user-installed `~/.openclaw/extensions/line` copy.

### Error
```
[plugins] line failed to load from /app/extensions/line/index.ts: TypeError: Cannot redefine property: isSenderAllowed
[openclaw] Failed to start CLI: PluginLoadFailureError: plugin load failed: line: TypeError: Cannot redefine property: isSenderAllowed
```

### Context
- Initial suspicion was duplicate LINE plugin versions (`~/.openclaw/extensions/line` 2026.2.15 vs `/app/extensions/line` 2026.3.22)
- Moved the old user-installed LINE plugin out of `~/.openclaw/extensions/` into `/home/node/.openclaw/plugin-backups/_disabled-line-20260325-160946`
- Retest still failed, which shows the bundled 2026.3.22 LINE plugin itself crashes in this environment
- Temporary workaround works: create a temp config with `plugins.entries.line.enabled=false`, then CLI/status and Telegram reminder sends succeed normally

### Suggested Fix
Treat this as an upstream/bundled LINE plugin compatibility issue on 2026.3.22. Temporary local workaround is to disable the LINE plugin in config when CLI access is needed, but that also disables the LINE channel until the plugin is repaired.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/openclaw.json, /app/extensions/line, /home/node/.openclaw/plugin-backups/_disabled-line-20260325-160946

---

## [ERR-20260326-001] git_push_non_fast_forward_recurred

**Logged**: 2026-03-26T06:21:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Another GitHub push to `Myclawagi` was rejected because remote `main` had advanced beyond the local branch.

### Error
```
To https://github.com/yuming920619-svg/Myclawagi.git
 ! [rejected]        HEAD -> main (fetch first)
error: failed to push some refs to 'https://github.com/yuming920619-svg/Myclawagi.git'
```

### Context
- Operation attempted: push deletion of `Myagi_workspace/TOKEN_STRATEGY.md`
- Local commit was `12dfab8` (`sync: remove obsolete TOKEN_STRATEGY.md`)
- Remote had advanced from `d8663f5` to `27ba316`
- Safe recovery path is still `git fetch` / `git pull --rebase origin main` and then push again

### Suggested Fix
Before pushing to `github.com/yuming920619-svg/Myclawagi`, fetch or rebase first when another device/session may have updated `main`.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/Myclawagi/Myagi_workspace/TOKEN_STRATEGY.md
- See Also: ERR-20260320-001

---

## [ERR-20260326-002] cron_one_shot_name_match_missing_job

**Logged**: 2026-03-26T15:31:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to retime three one-shot reminder jobs by matching expected names, but one "前一天" job no longer existed because the earlier one-shot reminder had already disappeared after its prior schedule.

### Error
```
Error: Job not found for 前一天
```

### Context
- Operation attempted: move the "與主任有約" reminder set from 3/27 to 4/10
- Initial approach assumed all three original one-shot jobs still existed in cron storage
- Actual state: only the "當天早上" and "出門前" jobs remained; the "前一天" job had to be recreated instead of edited

### Suggested Fix
When editing old one-shot reminders, first inspect current cron jobs and do not assume every original reminder still exists; be ready to recreate missing ones.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md
- See Also: ERR-20260326-001

---

## [ERR-20260327-001] git_pull_rebase_with_unstaged_changes

**Logged**: 2026-03-27T15:47:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Tried to run `git pull --rebase` before staging/committing the rewritten discussion drafts, and Git refused because the working tree had unstaged changes.

### Error
```
error: cannot pull with rebase: You have unstaged changes.
error: please commit or stash them.
```

### Context
- Operation attempted: sync remote `main` before pushing rewritten `2026-03-27` audience evaluation drafts
- Local repo had modified tracked files in `Special Topic Discussion/`
- Correct flow here is: stage target files → commit → push; only fetch/rebase after commit if push is rejected

### Suggested Fix
For focused document updates, do not call `git pull --rebase` with unstaged tracked edits; either commit first or use an explicit autostash/rebase flow.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/workspace/Myclawagi/Special Topic Discussion/2026-03-27_觀眾評分表草稿.md, /home/node/.openclaw/workspace/Myclawagi/Special Topic Discussion/2026-03-27_觀眾評分表草稿_第二版.md
- See Also: ERR-20260326-001


## [ERR-20260328-001] openclaw_cli_parallel_gateway_closure

**Logged**: 2026-03-28T11:25:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
Running several `openclaw` CLI calls in parallel against the local loopback gateway caused some commands to fail with normal WebSocket closure (`1000`).

### Error
```
gateway connect failed: Error: gateway closed (1000): 
Error: gateway closed (1000 normal closure): no close reason
Gateway target: ws://127.0.0.1:18789
Source: local loopback
Config: /home/node/.openclaw/openclaw.json
Bind: loopback
```

### Context
- Operation attempted: parallel `openclaw cron runs --id ...` checks during cron health inspection
- Some concurrent calls succeeded, while others exited with gateway closure
- Re-running the same checks serially / in smaller batches worked

### Suggested Fix
When inspecting many cron jobs, avoid spawning too many concurrent `openclaw` CLI processes against the same local gateway. Prefer serial checks or small batches.

### Metadata
- Reproducible: unknown
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md

---

## [ERR-20260329-001] openclaw_cron_at_tz_interpretation

**Logged**: 2026-03-29T04:05:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
`openclaw cron add --at 'YYYY-MM-DD HH:MM' --tz Asia/Taipei` was interpreted as a UTC timestamp in this environment, creating a one-shot reminder 8 hours late.

### Error
```
Requested: 2026-03-29 16:00 @ Asia/Taipei
Created job schedule.at: 2026-03-29T16:00:00.000Z
```

### Context
- Operation attempted: create one-shot reminder for today at 16:00 Taipei time
- Command used `--at '2026-03-29 16:00' --tz Asia/Taipei`
- Resulting job was scheduled at 16:00 UTC instead of 16:00 UTC+8
- Fixed by editing the job to an explicit offset timestamp: `2026-03-29T16:00:00+08:00`

### Suggested Fix
For one-shot reminders, prefer explicit ISO timestamps with numeric offset (for example `2026-03-29T16:00:00+08:00`) instead of relying on `--tz` to reinterpret an offset-less `--at` value.

### Metadata
- Reproducible: unknown
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md

---

## [ERR-20260330-001] duckduckgo_exact_query_bot_challenge

**Logged**: 2026-03-30T05:44:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
A `web_search` follow-up query for an exact STT-MRAM ECC paper title triggered DuckDuckGo bot detection instead of returning results.

### Error
```
DuckDuckGo returned a bot-detection challenge.
```

### Context
- Operation attempted: refine a prior successful broad STT-MRAM ECC search into an exact-title / PDF lookup
- Initial broad search worked, but the narrower follow-up query was blocked
- Working fallback was to use the already-returned arXiv result and fetch the abstract directly from `https://arxiv.org/abs/1509.08806`

### Suggested Fix
When `web_search` hits DuckDuckGo bot detection on narrower follow-up queries, avoid retry loops; reuse prior search results, broaden the query, or fetch the candidate source URL directly.

### Metadata
- Reproducible: unknown
- Related Files: /home/node/.openclaw/workspace/.learnings/ERRORS.md

---

## [ERR-20260330-002] expense_tracker_shell_quoting_bash_lc

**Logged**: 2026-03-30T15:31:00Z
**Priority**: low
**Status**: pending
**Area**: infra

### Summary
A complex `bash -lc` command for expense logging failed with shell parsing errors before completion.

### Error
```
sh: 42: Syntax error: "(" unexpected
```

### Context
- Operation attempted: append two expense rows, compute monthly summary, and send reminder bot message in one shell command
- The nested quoting/heredoc structure broke under the exec shell wrapper
- Working fallback was to move the logic into a single Node script and call `openclaw message send` via `execFileSync`

### Suggested Fix
For multi-step expense logging flows that mix dynamic strings and message sending, prefer a small Node script over deeply nested `bash -lc` quoting.

### Metadata
- Reproducible: unknown
- Related Files: /home/node/.openclaw/workspace/skills/expense-tracker/SKILL.md, /home/node/.openclaw/workspace/.learnings/ERRORS.md

---
## [ERR-20260404-001] openclaw_plugin_install_archive_conflicts_existing_id

**Logged**: 2026-04-04T05:08:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Trying to install a local plugin archive over an already-installed plugin with the same manifest id fails immediately; OpenClaw requires removing the existing install first.

### Error
```
plugin already exists: /home/node/.openclaw/extensions/todo-api-tools (delete it first)
Also not a valid hook pack: Error: package.json missing openclaw.hooks
```

### Context
- Operation attempted: install updated `todo-api-tools` from a `.tar` archive with `openclaw plugins install <archive>`
- Existing plugin id `todo-api-tools` was already installed under `/home/node/.openclaw/extensions/todo-api-tools`
- OpenClaw did not treat this as an in-place upgrade and aborted before restart/verification
- Safe recovery path is: back up current `plugins.entries.todo-api-tools` config, uninstall old plugin, install new archive, then restore config/allowlists and restart gateway

### Suggested Fix
For local plugin archive upgrades, do not assume `openclaw plugins install <archive>` overwrites an existing install. First preserve config, uninstall the existing plugin id, then install the new archive and restore the config.

### Metadata
- Reproducible: yes
- Related Files: /home/node/.openclaw/openclaw.json, /home/node/.openclaw/extensions/todo-api-tools, /home/node/.openclaw/workspace/.learnings/ERRORS.md

---
## [ERR-20260330-001] exec-shell-pipefail

**Logged**: 2026-03-30T19:00:31Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
OpenClaw exec default shell rejected `set -o pipefail` because the command ran under `/bin/sh`, not bash.

### Error
```
sh: 1: set: Illegal option -o pipefail
```

### Context
- Command/operation attempted: workspace sync cron shell script via `exec`
- Input or parameters used: script started with `set -euo pipefail`
- Environment details: OpenClaw `exec` default shell appears to be `/bin/sh`

### Suggested Fix
When a script needs `pipefail` or other bash features, invoke `bash -lc '...'` explicitly instead of assuming the default shell is bash.

### Metadata
- Reproducible: yes
- Related Files: TOOLS.md

---
