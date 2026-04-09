# Claude Code Analysis → Workspace Upgrade

## Goal
用 `liuup/claude-code-analysis` 倉庫作為參照，提煉對目前 OpenClaw 工作區、工作流與 OpenClaw 落地方案真正有幫助的內容，避免照抄與文件膨脹。

## Scope
- 工作區規範：`AGENTS.md` / `TOOLS.md` / `SOUL.md` / `MEMORY.md` / `USER.md`
- 任務恢復與追蹤：`SESSION-STATE.md` / `notes/open-loops.md`
- 專題分析筆記：本目錄下文件
- 前序 OpenClaw source adaptation 脈絡：`.tmp/openclaw-upstream/docs/refactor/openclaw-runtime-first-adaptation.md`

## Non-goals
- 不直接複製 Claude Code 實作細節進 workspace 規範
- 不因為「看起來先進」就引入過重系統
- 不未經使用者要求就對外 push / 發佈

## 6-hour iteration loop
每輪包含：
1. 聚焦一組主題章節
2. 提煉 borrowable patterns
3. 比對現有工作區 / adaptation plan
4. 做最小但實質的落地修改
5. 寫 retrospective：保留、放棄、風險、下一輪焦點

## Main outputs
- `borrowable-patterns.md`
- `iteration-log.md`
- 必要時更新核心 workspace 文件
- 必要時補充 OpenClaw adaptation docs
