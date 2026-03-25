# TOOLS.md - Local Notes

Keep this file practical. Put only environment-specific notes here.

## Browser
- Remote browser sandbox is available via profile `remote`
- Current CDP endpoint: `http://openclaw-sandbox-browser-posess:9222`
- Cloud host does **not** have local Chromium/Chrome; prefer Remote CDP / Browser Relay over expecting a local managed browser
- Direct CDP scripting gotcha: `/json/new` returns page `webSocketDebuggerUrl` with host `127.0.0.1`; when connecting from this workspace, rewrite it to `openclaw-sandbox-browser-posess:9222` or the socket will fail to open

## Messaging
- Active channels: Telegram + LINE
- Discord is backup-only for now; valid target ID still missing

## Self-Improvement
- Workspace root has `.learnings/` enabled:
  - `LEARNINGS.md`
  - `ERRORS.md`
  - `FEATURE_REQUESTS.md`
- `self-improvement` hook is installed and ready

