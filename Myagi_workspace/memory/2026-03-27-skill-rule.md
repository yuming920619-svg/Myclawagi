# 2026-03-27 — Special topic discussion rule hardening

## 規則補強
- source: chat + skill edit + git
- tags: #special-topic-discussion #skill #writing #validation
- note: 這輪 anti-template 重寫並推送後，回頭檢查發現仍有部分評論低於 30 字，因此 skill 進一步補上「回傳 / push 前逐條驗字數」的明確規則。新規則從下一輪開始視為固定流程。

## 當日處理決策
- source: chat
- tags: #special-topic-discussion #decision
- note: 使用者接受今天既有成品先不再補修，因此 3/27 當天 GitHub 上的版本維持現狀；重點是把規則補齊，避免下次再犯。

## Git 操作教訓
- source: chat + self-review
- tags: #git #workflow #pitfall
- note: 本輪也踩到一次 Git 操作順序問題：在 worktree 還有不相干未 staged 變更時，不應先做 `pull --rebase`。較穩的流程是先只提交目標檔案，再 fetch / rebase，最後 push。

## 備註
- canonical day summary 已整理進 `memory/2026-03-27.md`
