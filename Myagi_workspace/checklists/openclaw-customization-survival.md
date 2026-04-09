# Checklist: OpenClaw Customization Survival

目的：在做 OpenClaw 客製或升級借鑑前，先確認這件事是不是耐更新、值得維護。

## Pre-flight
- [ ] 先分清楚目標層級：workspace / docs / wrapper / skill / config / source patch
- [ ] 若是 source patch，先回答：版本更新後會不會直接被覆蓋？
- [ ] 若會被覆蓋，先找 durable 替代：workspace 規範、checklist、wrapper、skill、patch-ready doc
- [ ] 若仍想做 source patch，先明確指定維護策略：fork / patch queue / upstreamable diff；沒有就先不要做
- [ ] 檢查是否只是把一次性研究心得塞進 bootstrap 檔；若是，改寫到 `notes/` 或 `checklists/`

## Durable-first routing

### 適合先做的
- [ ] 工作區治理規則：只加真的會反覆用到的短規則
- [ ] `notes/` / `checklists/`：沉澱分析結論、升級路線、驗證步驟
- [ ] wrapper / skill：前提是不依賴 patch OpenClaw core
- [ ] config 層調整：前提是可重放、可驗證、可在升級後快速重套

### 應先延後或拒絕的
- [ ] 只在本版 OpenClaw 生效、下次更新就蒸發的 runtime patch
- [ ] 沒有維護者、沒有驗證清單、只有概念沒有落地點的 schema / overlay 幻想
- [ ] 為了看起來進階而增加 prompt 膨脹、多代理儀式或文件層平行 runtime

## Before editing bootstrap files
- [ ] 先看 `wc -c`，確認不是把核心檔越改越胖
- [ ] 問自己：這條內容是不是每次對話都該常駐？不是就不要放 bootstrap
- [ ] 同一件事是否已存在於其他核心檔？避免重複寫兩次
- [ ] 優先把細節留在 `notes/`，核心檔只留入口規則

## Verification
- [ ] 確認新 artifact 能在不 patch core 的前提下獨立存活
- [ ] 確認路徑、檔名、操作步驟足夠讓下次 session 直接接手
- [ ] 若涉及 source patch 提案，至少留下：目的、風險、驗證法、升級後如何重放
- [ ] 在 `SESSION-STATE.md` 記錄目前主線、下一步與明確不做的項目
- [ ] 在相關 iteration log 記錄 adopted / deferred / risks / next focus

## Exit criteria
- [ ] 有至少一個 durable artifact 留下來
- [ ] 沒有為了形式漂亮而膨脹 `AGENTS.md` / `SOUL.md` / `USER.md` / `MEMORY.md`
- [ ] 能清楚說明：做了什麼、刻意沒做什麼、下次最穩的續作路線是什麼
