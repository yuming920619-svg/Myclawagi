# Recurring Patterns

Use this file for repeated workflows that may deserve a template, checklist, script, or skill.
Only log stable patterns.

## Template
### Pattern
- Name:
- Trigger context:
- Occurrence count:
- Stable workflow:
- Possible automation direction:
- Status: observing / template-ready / checklist-ready / skill-ready

## Active

### Pattern
- Name: OpenClaw 升級後的通知遷移流程
- Trigger context: OpenClaw 升級後，需要確認 cron、通知通道、以及多 bot 分流是否正常
- Occurrence count: 1
- Stable workflow: 1) 先確認版本與 cron store 狀態 2) 盤點現有 cron delivery 3) 抽測重要通知 4) 若單一通道或 bot 有限制，改做多 bot / 多通道路由分流 5) 再次驗證代表性提醒
- Possible automation direction: 做成升級後 checklist，或做成半自動 audit / migration skill
- Status: observing
