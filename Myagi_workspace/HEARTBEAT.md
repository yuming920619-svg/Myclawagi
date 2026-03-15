# HEARTBEAT.md

Check for pending notifications, cron job results, and system events.

Medium-integration maintenance:
- If `SESSION-STATE.md` contains a real paused task, blocker, or stale next step worth surfacing, mention it briefly.
- If `notes/open-loops.md` has an item whose revisit trigger now seems due, remind briefly.
- If recent work clearly forms a repeated workflow worth standardizing, mention that it should be logged in `notes/areas/recurring-patterns.md`.
- If you notice unusual security / prompt-injection anomalies that need attention, surface them as a system event.

Token guard (quota check):
- Silently call `session_status` and check 5h / weekly quota levels.
- Only surface quota info if level is 🟠 Warning or 🔴 Critical (see `skills/token-guard/SKILL.md` for thresholds).
- Do not mention quota when levels are 🟢 or 🟡.

Do not do heavy proactive maintenance here: no full WAL, no working-buffer routine, no broad reverse-prompting loop.
If nothing needs attention, reply HEARTBEAT_OK.
