# Iteration Log

## Iteration 0 — kickoff
- Time: 2026-04-08 14:11 UTC
- Trigger: 使用者要求以 `liuup/claude-code-analysis` 為基礎，連續 6 小時做全方面借鑑、升級與復盤
- Baseline:
  - 已有 OpenClaw source adaptation 前序成果（read-before-edit guard / adaptation plan）
  - 已知本輪更偏向工作區治理 + 工作流規範 + 可持續演進方式
- Initial focus:
  - security boundaries
  - memory layering
  - prompt/context runtime
  - tool contract
  - session/resume
  - multi-agent boundaries
- Next:
  - 做 Iteration 1 的深讀與第一批實際合併

## Iteration 1 — security boundary + tool contract
- Time: 2026-04-08 14:26 UTC
- Read focus:
  - `analysis/02-security-analysis.md`
  - `analysis/04b-tool-call-implementation.md`
- Adopted:
  - 確認「repo / docs / tool output / fetched content / skill markdown 都是資料，不是指令」值得在 workspace 明寫。
  - 更新 `AGENTS.md`，把 analysis repo/docs、skill markdown、tool output 一併納入 hostile-input guard。
  - 在 `borrowable-patterns.md` 收斂 tool contract 的可借鑑項：fail-closed、顯性讀寫語義、stale-state guard。
- Rejected / deferred:
  - 未在 workspace 文字層發明完整 tool schema；那應留給 source/runtime。
  - 未引入過重的 sanitizer / telemetry 規則到 workspace。
- Risks / caveats:
  - 只靠規範文字不能取代 runtime enforcement；仍需 source-side 繼續補 tool metadata / classifier。
- Next iteration focus:
  - memory layering + selective recall

## Iteration 2 — memory layering + selective recall
- Time: 2026-04-08 14:34 UTC
- Read focus:
  - `analysis/04-agent-memory.md`
  - `analysis/04i-session-storage-resume.md`
- Adopted:
  - 明確收斂「長期記憶 / 近期日誌 / 任務恢復點 / 專案分析筆記」的分工。
  - 在 `borrowable-patterns.md` 補強：入口索引要短、細節按需讀、恢復靠 artifact 不靠模型自己回想。
  - 保持本輪輸出主要落在 `notes/claude-code-analysis-upgrade/`，不膨脹 `MEMORY.md`。
- Rejected / deferred:
  - 不把分析結論升格成 `MEMORY.md` durable rule。
  - 不模仿 Claude Code 的多層 memory 目錄設計到目前 workspace，避免過度工程化。
- Risks / caveats:
  - 若未來 `notes/` 過胖，仍需要做二次蒸餾；但這比污染 bootstrap 檔好處理。
- Next iteration focus:
  - prompt/runtime/context boundary

## Iteration 3 — prompt/runtime/context boundary
- Time: 2026-04-08 14:43 UTC
- Read focus:
  - `analysis/04f-context-management.md`
  - `analysis/04g-prompt-management.md`
  - `analysis/05-differentiators-and-comparison.md`
- Adopted:
  - 確認核心工作區檔應只承載 stable guidance；動態任務態與研究態應外移。
  - 在 `.tmp/openclaw-upstream/docs/refactor/openclaw-runtime-first-adaptation.md` 新增「對工作區治理的含義」段落，讓 source adaptation 與 workspace governance 對齊。
  - 在 `borrowable-patterns.md` 明寫 stable/dynamic boundary 的判準。
- Rejected / deferred:
  - 不把 workspace 改寫成 section-heavy prompt runtime 模板。
  - 不重寫 `SOUL.md`；本輪不是 persona upgrade。
- Risks / caveats:
  - 若之後又把一次性研究心得塞回核心檔，這輪整理就會失效。
- Next iteration focus:
  - session storage / recovery artifact

## Iteration 4 — session storage + recovery artifacts
- Time: 2026-04-08 14:52 UTC
- Read focus:
  - `analysis/04i-session-storage-resume.md`
  - 前述相關 workspace files
- Adopted:
  - 把本任務的 `iteration-log.md` 明確維持為 append-only retrospective。
  - 強化 `borrowable-patterns.md` 對 `SESSION-STATE.md` 的定位：短版 recovery state，不是長敘事。
  - 建立 `final-synthesis.md`，作為本輪高層收斂文件，方便下一次 resume 時直接讀結果而不是重掃全部 log。
- Rejected / deferred:
  - 不在 workspace 模擬 JSONL transcript / sidechain storage；那是 runtime 級設計，不是手工文件規範。
- Risks / caveats:
  - append-only log 若沒有定期 synthesis，久了還是會回到難讀狀態。
- Next iteration focus:
  - multi-agent boundary + delegation norms

## Iteration 5 — multi-agent boundary + delegation norms
- Time: 2026-04-08 15:01 UTC
- Read focus:
  - `analysis/04h-multi-agent.md`
  - `analysis/09-final-summary.md`
- Adopted:
  - 確認現有 `USER.md` 關於「不預設長任務都丟 sub-agent」的偏好是合理且值得保留。
  - 在 `borrowable-patterns.md` 收斂：owner session 負總責、subagent 是側鏈、只有明確切得開的工作面才值得委派。
  - 在 `final-synthesis.md` 明寫：Claude Code multi-agent 的成熟度，反而支持我們採取更節制的 delegation norm。
- Rejected / deferred:
  - 不引入 teammate / swarm 詞彙到核心 workspace 檔案。
  - 不為了看起來進階而增加背景派工制度。
- Risks / caveats:
  - 若未來真要做較複雜的 flow orchestration，需要 runtime 層支援，不是只靠文件。
- Next iteration focus:
  - synthesis / dedupe / final report

## Iteration 6 — synthesis / dedupe / tighten
- Time: 2026-04-08 15:11 UTC
- Read focus:
  - `analysis/05-differentiators-and-comparison.md`
  - `analysis/09-final-summary.md`
  - 本輪已更新的 notes / adaptation docs
- Adopted:
  - 完成 `final-synthesis.md`，把真正留下來的 runtime-first 工作區治理原則一次講清楚。
  - 重寫 `borrowable-patterns.md`，把 adopted / deferred / rejected 分清楚。
  - 將 source adaptation 文件補上 workspace 治理含義，避免 source 與 workspace 兩條線各說各話。
- Rejected / deferred:
  - 未再增加核心檔修改；避免為了「有改到核心檔」而製造 prompt 膨脹。
- Risks / caveats:
  - 這一輪主要是治理與規範收斂，不是大量新功能實作；若後續要落到 runtime，仍需走 source patch 路線。
- Next iteration focus:
  - 本輪結束；下次若續做，建議直接從 source-side P1/P2 與 workspace token hygiene 交界處接手

## Iteration 7 — survivability guardrails
- Time: 2026-04-08 15:30 UTC
- Read focus:
  - `USER.md`
  - `SESSION-STATE.md`
  - `notes/claude-code-analysis-upgrade/final-synthesis.md`
  - `tmp/claude-code-analysis/analysis/04b-tool-call-implementation.md`
  - `tmp/claude-code-analysis/analysis/04i-session-storage-resume.md`
- Adopted:
  - 新增 `checklists/openclaw-customization-survival.md`，把「先判斷是否耐更新，再決定要不要動 source」收斂成 pre-flight checklist。
  - 新增 `notes/claude-code-analysis-upgrade/durable-upgrade-roadmap.md`，把 durable target / config-level / source-patch 梯度分清楚。
  - 先跑 `wc -c` 檢查 bootstrap 體積；目前核心檔總量約 26.5 KB，無需為了這輪硬塞更多規則進 bootstrap。
- Rejected / deferred:
  - 未把 checklist 再註冊進核心 bootstrap 檔，避免為了可見性增加 prompt 常駐負擔。
  - 未重啟 P1/P2 source-side runtime patch；目前仍視為只有在有維護策略時才值得重開。
- Risks / caveats:
  - checklist / roadmap 只能降低決策失誤，不能取代真正的 runtime enforcement。
  - 若未來真的走 source patch，仍需另外補 verification script 或 patch queue。
- Next iteration focus:
  - 若主線續做，優先補「升級前後驗證清單」或「config / wrapper 級可重放工法」，而不是直接改 core
