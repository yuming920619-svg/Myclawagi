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

### Pattern
- Name: 專題討論表單評論與 GitHub 歸檔流程
- Trigger context: 使用者提供專題討論講者姓名與報告主題，要求生成 Google 表單必答評論，並同步歸檔到 GitHub
- Occurrence count: 2
- Stable workflow: 1) 若有表單網址先整理必填題目 2) 解析講者與主題 3) 針對每位講者生成五個必答面向的短評與建議分數，且每條滿足最低字數門檻 4) 更新同日 markdown 草稿 5) 固定同步到 `Myclawagi/Special Topic Discussion/` 並 commit/push，除非使用者明確說先不要推
- Possible automation direction: 已固化為 `skills/special-topic-discussion/` skill，可持續迭代評論模板、字數檢查與 GitHub 歸檔規則
- Status: skill-ready
