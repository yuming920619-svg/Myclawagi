# TOOLS.md - Local Notes

Keep this file practical. Put only environment-specific notes here.

## Browser
- Remote browser sandbox is available via profile `remote`
- Current CDP endpoint: `http://openclaw-sandbox-browser-posess:9222`
- Cloud host does **not** have local Chromium/Chrome; prefer Remote CDP / Browser Relay over expecting a local managed browser
- Direct CDP scripting gotcha: `/json/new` returns page `webSocketDebuggerUrl` with host `127.0.0.1`; when connecting from this workspace, rewrite it to `openclaw-sandbox-browser-posess:9222` or the socket will fail to open

## Shell / Exec
- Gateway `exec` 預設 shell 是 `/bin/sh`，不是 bash；若要用 `set -o pipefail`、`[[ ... ]]`、arrays 或其他 bash-only 語法，必須顯式包成 `bash -lc '...'`
- 只把 Telegram `channels.telegram.accounts.default.execApprovals.enabled` 關掉，**不代表 host exec 真的免批准**；若要回到完全不跳手動批准，還要同步放寬 `~/.openclaw/openclaw.json` 的 `tools.exec`（目前設為 `host=gateway`, `security=full`, `ask=off`）以及 `~/.openclaw/exec-approvals.json`（目前 `defaults/agents.main` 皆為 `security=full`, `ask=off`, `askFallback=full`）

## OpenClaw CLI / Cron
- 在目前 OpenClaw `2026.4.1`，`openclaw cron disable <id>` 實測可能回 `invalid cron.update params`；若要停用 job，改用 `openclaw cron edit <id> --disable` 比較穩

## Plugins
- 本地外掛若放在 `~/.openclaw/extensions/`，檔案權限太寬（例如 `666` / world-writable）會被 OpenClaw 直接 block；可用 `chmod -R go-w <plugin-dir>` 修正
- 要讓已安裝 plugin 真正被 Gateway 接受，核心 allowlist 看的是 `plugins.allow`，不是 `tools.allow`
- plugin / tool 配置修好後，**新 session** 才會拿到更新後的工具清單；舊 session 不會熱更新出新工具

## Messaging
- Active channels: Telegram
- Reminder bot accountId: `reminder`（自動通知預設走這個）
- Telegram `accounts.default` 的 exec approvals 已於 2026-04-04 關閉；目前恢復為一般 `exec` 不走 Telegram 手動批准流程
- `reminder` 與 `8562448721` 這兩個 Telegram account 目前也未啟用 exec approvals
- 若 cron / 自動任務內層還會再觸發 `exec` approval，要讓批准卡正常浮到使用者，就不能走 `reminder`；需改走 Telegram `default` account
- 工作區 sync job 已收斂成固定腳本 `scripts/sync-workspace-to-github.sh`；預期回報只保留兩種：`無變更，跳過` 或 `已同步：<commit> <message>`
- LINE is temporarily disabled after upgrading to OpenClaw `2026.3.22` because the bundled LINE plugin crashes on load (`Cannot redefine property: isSenderAllowed`)
- Old user-installed LINE plugin was moved to `~/.openclaw/plugin-backups/_disabled-line-20260325-160946`
- Discord is not used as a communication channel for this workspace
- Telegram 直聊中，commentary / tool-trace 內容曾在忙碌期間被直接顯示到聊天；處理 live chat 時要盡量避免輸出任何非必要 commentary，優先直接呼叫工具，最後再一次性用人話回覆

## Self-Improvement
- Workspace root has `.learnings/` enabled:
  - `LEARNINGS.md`
  - `ERRORS.md`
  - `FEATURE_REQUESTS.md`
- `self-improvement` hook is installed and ready

