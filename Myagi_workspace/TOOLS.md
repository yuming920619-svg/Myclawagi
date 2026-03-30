# TOOLS.md - Local Notes

Keep this file practical. Put only environment-specific notes here.

## Browser
- Remote browser sandbox is available via profile `remote`
- Current CDP endpoint: `http://openclaw-sandbox-browser-posess:9222`
- Cloud host does **not** have local Chromium/Chrome; prefer Remote CDP / Browser Relay over expecting a local managed browser
- Direct CDP scripting gotcha: `/json/new` returns page `webSocketDebuggerUrl` with host `127.0.0.1`; when connecting from this workspace, rewrite it to `openclaw-sandbox-browser-posess:9222` or the socket will fail to open

## Messaging
- Active channels: Telegram
- Reminder bot accountId: `reminder`（自動通知預設走這個）
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

