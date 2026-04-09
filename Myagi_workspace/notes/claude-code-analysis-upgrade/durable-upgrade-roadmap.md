# Durable Upgrade Roadmap

## 目的
把 `tmp/claude-code-analysis` 帶來的洞察，收斂成升級後仍活得下來的工作路線。

## 核心判準
1. **先選耐更新落點，再選技術做法。**
2. **workspace bootstrap 只放常駐規則，不放研究垃圾。**
3. **source patch 若無維護策略，就視為高折舊資產。**

## Tier 1：優先做，且最耐更新

### A. 治理與恢復 artifact
- `notes/claude-code-analysis-upgrade/`
- `checklists/openclaw-customization-survival.md`
- `SESSION-STATE.md`

適用情境：
- 剛做完分析，需要把結論沉澱成可恢復、可重用的 artifact
- 想減少下次從頭研究的成本

價值：
- 幾乎不受 OpenClaw 升級覆蓋影響
- 可以作為之後任何 source / config 變更的前置守門

### B. 核心工作區檔的小幅校正
- 只在真的會反覆命中時，更新 `AGENTS.md` / `TOOLS.md` / `USER.md` / `MEMORY.md`
- 原則：一句抵十句；沒有高 payback 就不要加

適用情境：
- 發現重複踩坑規則已很穩定
- 使用者偏好已明確，且會影響未來多數任務

## Tier 2：可做，但要保持薄

### A. Wrapper / skill / script
前提：
- 不 patch OpenClaw core
- 升級後仍能直接用，或只需低成本重接
- 目標是減少重複操作，而不是模擬平行 runtime

候選方向：
- 升級前後檢查腳本
- workspace token hygiene / bootstrap size audit
- 針對高風險 config 變更的 verification checklist

### B. Config-level customization
前提：
- 設定可匯出、可比對、可在升級後快速重放
- 有對應驗證步驟，不只改檔不驗證

## Tier 3：只有在明確承諾維護時才做

### Source-side runtime patch
例：
- tool metadata sidecar
- shell classifier
- declarative overlay / dispatch hints

只有以下條件成立才值得做：
- 有 fork、patch queue 或清楚的重放流程
- 有驗證清單，知道升級後怎麼確認沒壞
- 確認 payoff 高於每次版本更新的重做成本

否則：
- 先停在 patch-ready design doc / verification checklist 即可

## 建議續作順序
1. 先守住 workspace / notes / checklist 的邊界
2. 若 recurring pattern 明確，再補 wrapper / script
3. 若某 source patch 的收益反覆被證明夠高，再考慮進入維護路線

## 明確不建議
- 為了模仿 Claude Code 而在 workspace 文件內自造一套 runtime 架構
- 把分析過程大量升格到 `MEMORY.md`
- 在沒有維護計畫下，持續投入會被版本更新洗掉的 patch

## 下次續接時先讀
1. `notes/claude-code-analysis-upgrade/final-synthesis.md`
2. `notes/claude-code-analysis-upgrade/iteration-log.md`
3. `checklists/openclaw-customization-survival.md`
4. `SESSION-STATE.md`
