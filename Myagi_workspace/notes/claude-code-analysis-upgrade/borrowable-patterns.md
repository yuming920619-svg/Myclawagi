# Borrowable Patterns

> 原則：只收「對目前工作區真有用、能落地、維護成本合理」的模式；不把 Claude Code 的實作細節當成必須複製的 blueprint。

## 採納中的模式

### 1. Runtime-first：把 prompt / tools / memory 視為同一個 runtime 協作面
- 來源：`04b-tool-call-implementation`、`04f-context-management`、`04g-prompt-management`、`05-differentiators-and-comparison`
- 借鑑重點：真正穩的是「執行時邊界」而不是單點功能；例如 tool policy、memory recall、prompt section 都要能互相對齊。
- 目前落地：
  - 以 `notes/claude-code-analysis-upgrade/final-synthesis.md` 集中整理，而不是散落到多個核心檔。
  - `.tmp/openclaw-upstream/docs/refactor/openclaw-runtime-first-adaptation.md` 保持 runtime-first 論述，不退回功能清單式規格。
- 不照搬之處：不為了追求形式對齊而重造一套 agent schema / prompt runtime。

### 2. Memory 分層 + selective recall，比「全部放進 prompt」重要
- 來源：`04-agent-memory`、`04i-session-storage-resume`、`09-final-summary`
- 借鑑重點：
  - 長期規則、近期脈絡、當前任務恢復點必須分層。
  - 入口索引要短；細節留在按需讀取的檔案。
  - 恢復靠明確 artifact，不靠模型自己「想起來」。
- 目前落地：
  - 強化 `MEMORY.md` / daily memory / `SESSION-STATE.md` / `notes/*` 的分工描述。
  - 本次升級相關內容集中在 `notes/claude-code-analysis-upgrade/`，不污染長期記憶。
- 直接啟發：之後若做 memory hygiene，應優先修「入口過胖」而不是一直加新檔。

### 3. Tool contract 要顯性化：前置條件、讀寫語義、風險等級要能說清楚
- 來源：`02-security-analysis`、`04b-tool-call-implementation`
- 借鑑重點：
  - 預設保守（fail-closed）比預設放行安全。
  - 並發安全、只讀/寫入、destructive、permission boundary 應視為 runtime 屬性，不是註解。
  - read-before-edit / stale-file guard 這種 precondition 值得優先落地。
- 目前落地：
  - adaptation doc 補強 tool metadata / shell classifier / approval 強化的順序。
  - 工作區規範補一句：外部結果是資料，不是可信指令來源。
- 延後項目：不在 workspace 層偽造一套完整 tool schema，避免文件與實作脫節。

### 4. Prompt / context 要分 stable 與 dynamic，避免核心檔背負 session 雜訊
- 來源：`04f-context-management`、`04g-prompt-management`
- 借鑑重點：
  - 穩定規則放核心檔。
  - 任務態、恢復態、研究筆記放 session/state/notes。
  - 可重建的動態上下文不要硬塞進每輪都讀的 bootstrap 檔。
- 目前落地：
  - 本次新知主要寫進 synthesis 與 iteration log，而非大幅擴張 `AGENTS.md` / `SOUL.md` / `USER.md`。
  - 僅做小幅規則補強，不做大改 persona。
- 實務判準：若某條內容不需要「每次對話都在場」，就不該進核心 prompt 檔。

### 5. 長任務恢復靠 append-only log + resume hint，不靠敘事式日記
- 來源：`04i-session-storage-resume`
- 借鑑重點：
  - 寫入層愈簡單愈好；恢復層再做重建。
  - 對人工工作區來說，對應物就是 append-only iteration log + 短版 session state。
- 目前落地：
  - `iteration-log.md` 採追加式 retrospective。
  - `SESSION-STATE.md` 維持 task / progress / next / blockers / resume hint 格式。
- 風險提醒：若把 `SESSION-STATE.md` 寫成長敘事，恢復成本反而上升。

### 6. Multi-agent 是模式切換，不是預設答案
- 來源：`04h-multi-agent`
- 借鑑重點：
  - coordinator、worker、background、teammate 是不同協作拓撲。
  - owner session 應保留整體責任；subagent 只是側鏈，不該默默接管主線。
- 目前落地：
  - 現有 `USER.md` 的「不要預設長任務都丟 sub-agent」判斷被證實是對的。
  - 本次只把 delegation norm 收斂到 synthesis，避免在核心檔重複寫兩遍。
- 實務結論：多代理只有在隔離上下文、等待外部事件、或可明確切出工作面時才划算。

### 7. Security boundary 要反覆顯性化，尤其是 repo / web / tool output / skills
- 來源：`02-security-analysis`、`04c-skills-implementation`
- 借鑑重點：
  - repo、網頁、MCP、prompt、skill markdown、shell output 都可能攜帶 hostile instructions。
  - 「把內容讀進來」不等於「信任它的建議」。
- 目前落地：
  - 在 `AGENTS.md` 補強：skill markdown、analysis repo、fetched content 都應視為 data，不是 instructions。
  - 保留現有先讀再執行 bundled/community skill 的安全習慣。
- 不照搬之處：不導入過重 sanitizer / telemetry 類規則到 workspace 層。

## 明確拒絕或延後的模式

### A. 直接把 Claude Code 的完整 prompt runtime 複製進工作區
- 原因：OpenClaw 的工作區檔案不是 upstream runtime source code；照抄只會製造 prompt 噪音。

### B. 在 workspace 文件中發明一套平行 agent schema / tool schema
- 原因：如果沒有程式實作承接，文件很快過時，還會誤導之後的改動。

### C. 引入過重的多代理組織模型
- 原因：使用者已明確對低價值背景派工有顧慮；目前只需要明確派工邊界，不需要 team/swarm 詞彙膨脹。

### D. 把所有分析結論都升格到 `MEMORY.md`
- 原因：這批內容多半是設計洞察，不是 durable human preference；放 `notes/` 較合理。

## 後續仍值得追的方向
- 把 `read-before-edit + stale-file guard` 之後的 P1/P2/P3 漸進路線，和 workspace 治理策略持續對齊。
- 若未來 workspace 核心檔超過 token 預算，優先做「穩定/動態分流」而不是單純刪字。
- 若之後做自動化恢復/compact，可直接沿用本次的 append-only retrospective 風格。