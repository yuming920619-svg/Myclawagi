# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

---


## [LRN-20260318-001] correction

**Logged**: 2026-03-18T09:32:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
When the user asks about gpt-5-mini / gpt-5-nano, do not answer with gpt-5.4-mini / gpt-5.4-nano. Confirm the exact model family first.

### Details
The user asked for pricing and pros/cons of gpt-5-mini and gpt-5-nano. I incorrectly answered with gpt-5.4-mini and gpt-5.4-nano information. This happened because I mixed the OpenClaw catalog naming (gpt-5-mini / gpt-5-nano) with newer OpenAI docs that mention gpt-5.4-mini / gpt-5.4-nano.

### Suggested Action
Before answering model/pricing questions, restate the exact model IDs requested and verify the provider naming in current docs/catalog. If there is a naming mismatch between OpenClaw and provider docs, call it out explicitly instead of assuming they are interchangeable.

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: models, pricing, correction, openai, openclaw

---

## [LRN-20260319-002] correction

**Logged**: 2026-03-19T11:01:18Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
記帳流程不只要回覆使用者，還必須同步發送 reminder bot 通知；不能只完成本地記帳與聊天回覆。

### Details
使用者再次提醒「每次記帳都要在 reminder 通知」。我這次雖然成功把消費寫入 CSV、算出當月統計並回覆使用者，但漏掉了 skill 明定的 reminder bot 推送步驟。這代表我在執行已知固定流程時，只做了聊天面上的確認，沒有完整執行整個記帳工作流。

2026-03-24 又再次重複發生一次：處理 3/22 午餐「拉亞漢堡 炸雞麵+奶茶+雞塊 257」時，仍然只完成了寫入與回覆，沒有發 reminder 通知，代表這已不是單次遺漏，而是固定流程執行沒有被我確實收尾。

### Suggested Action
之後只要觸發 expense-tracker 記帳流程，就要把步驟視為固定三件事：1) 寫入 CSV，2) 更新/查統計，3) 立即發送 reminder bot 摘要通知。回覆使用者前先確認三步都完成。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/expense-tracker/SKILL.md, /home/node/.openclaw/workspace/expenses/2026-03.csv
- Tags: expense, reminder, workflow, correction
- Recurrence-Count: 2
- First-Seen: 2026-03-19
- Last-Seen: 2026-03-24

---

## [LRN-20260319-003] best_practice

**Logged**: 2026-03-19T16:14:59Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
處理台北時間的記帳資料時，不要手動做 UTC+8 小時換算後直接拼字串，避免產生 `24:xx` 這種無效時間。

### Details
在記錄使用者的 3/19 午餐帳目時，我把 UTC 16:14 直接手動加 8 小時後寫成 `24:14`，造成 CSV 內出現非法 HH:MM。之後已修正成合理時間，但根本問題是不能靠手算時間字串。

### Suggested Action
之後凡是需要台北時間，一律用可靠的時區換算方式（例如 `TZ=Asia/Taipei` 或現成時間工具），不要手動做 `+8` 再自己格式化。

### Metadata
- Source: conversation
- Related Files: /home/node/.openclaw/workspace/expenses/2026-03.csv
- Tags: timezone, expense, formatting, best_practice

---

## [LRN-20260327-001] correction

**Logged**: 2026-03-27T08:57:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
專題討論表單評論不能寫得太長，應更像聽眾當場填表的自然短評，但仍需穩定超過 30 字門檻。

### Details
在為專題討論講者生成評論時，我把內容寫得偏完整分析段落，雖然更有深度，但使用者指出這樣不像實際聽眾會在現場表單裡寫出的內容。之後的正確方向應是保留一點研究感與具體性，但把每條壓到更精簡、自然、貼表單即可用的長度。

### Suggested Action
後續專題討論評論改用「短評模式」：每條大約 32–45 個中文字、語氣自然、可直接貼表單；避免寫成小段評論文，同時維持不空泛且不杜撰細節。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: special-topic-discussion, writing-style, correction, brevity

---

## [LRN-20260327-002] correction

**Logged**: 2026-03-27T15:42:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
專題討論表單的第 5 題（問答回應與臨場反應）不能對所有講者都套同一種句型，應依講者主題與內容重點寫出不同切角。

### Details
使用者指出我在專題討論評論裡，第 5 題常常都寫成類似「如果能再補充某件事會更好」的固定模板，導致不同講者之間看起來過於一致。正確方向不是完全放棄保守寫法，而是讓第 5 題根據該講者的題目或投影片內容，改從方法選擇、結果解讀、工程權衡、應用意義、限制說明等不同面向切入。

### Suggested Action
之後撰寫專題討論評論時，特別是第 5 題，要避免模板化重複句型；同一批講者之間應刻意分散切角與句式，保持 topic-specific、listener-like、但不杜撰。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: special-topic-discussion, q-and-a, writing-style, correction, variation

---

## [LRN-20260327-003] correction

**Logged**: 2026-03-27T15:45:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
專題討論評論不只第 5 題，連第 1–4 題也要避免批次模板化；同一批講者之間應使用不同句型與不同切角。

### Details
使用者指出就算把第 5 題改掉，如果第 1–4 題仍大量重複相同骨架，整份表單還是會看起來很像模板生成。之後正確做法是讓每一題都根據該講者的題目、方法、結果、圖表或應用場景，分散寫法與著力點，而不是只做表面換字。

### Suggested Action
之後撰寫專題討論評論時，1–5 題都要做 anti-template 檢查；同一批講者之間避免重複 `整體脈絡清楚`、`看得出準備認真`、`有把 A 與 B 連起來` 這類高重複骨架。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: special-topic-discussion, writing-style, correction, anti-template, variation

---

## [LRN-20260327-004] correction

**Logged**: 2026-03-27T15:58:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
專題討論 skill 不能只寫「目標長度 30+」原則，還必須明確要求在輸出前逐條檢查字數，避免實際成品仍出現不足 30 字的評論。

### Details
使用者指出本次產生的評論裡有好幾條實際不到 30 字。這代表即使 skill 已寫了長度規則，若沒有把「生成後逐條驗證」寫成明確收尾步驟，執行時仍可能漏掉。正確做法是把驗字數變成顯式 checklist，而不是只靠生成時的目標長度。

### Suggested Action
之後專題討論評論在回傳或 push 前，都要逐條檢查每一則評論的字數；低於門檻就先改到安全邊際再送出。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: special-topic-discussion, length-check, validation, correction

---

## [LRN-20260327-005] correction

**Logged**: 2026-03-27T16:26:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
整理 workspace 或 open loops 時，不能把「技術上可當備援」誤寫成使用者真的想用的溝通通道；Discord 不應被預設成備援方案。

### Details
我在整理 `notes/open-loops.md` 與相關記憶時，擅自把 Discord target ID 視為待補齊事項，等於把技術上的可能性誤當成使用者偏好。使用者明確更正：他完全不需要 Discord，也沒有要把 Discord 當溝通工具。這代表之後處理通道、通知、備援規劃時，必須區分「系統可支援」與「使用者真的要用」。

### Suggested Action
之後只有在使用者明確要求時，才把某個通道列為溝通工具或備援方案。整理 workspace 記憶時，若某通道只是技術上可用、但未被使用者採納，就不要把它寫成 open loop 或待辦。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/notes/open-loops.md, /home/node/.openclaw/workspace/TOOLS.md, /home/node/.openclaw/workspace/USER.md, /home/node/.openclaw/workspace/MEMORY.md
- Tags: discord, channels, workspace, correction, preference

---

## [LRN-20260327-006] correction

**Logged**: 2026-03-27T16:35:00Z
**Priority**: high
**Status**: promoted
**Promoted**: /home/node/.openclaw/workspace/skills/expense-tracker/SKILL.md
**Area**: config

### Summary
用 shell 組 reminder 訊息時，金額前的 `$` 不能直接放在雙引號字串裡，否則像 `$92`、`$140` 會被當成 shell 位置參數展開，導致通知金額顯示錯誤。

### Details
本次記帳的 CSV 寫入其實是正確的：雞柳燴飯 92、義大利麵 140。但我在送 Telegram reminder bot 時，把訊息內容寫進 shell 雙引號字串，導致 `$92` 被解析成 `$9` + `2`、`$140` 被解析成 `$1` + `40`，最後通知變成錯誤的 `2` 和 `40`。這是提醒訊息格式錯，不是記帳資料本身錯。

### Suggested Action
之後凡是用 shell 組含金額的提醒訊息，應避免讓 `$` 經過 shell 展開：改用單引號 heredoc、跳脫成 `\$`，或乾脆不要在 shell 內插值。送出前也應快速檢查訊息內容是否與 CSV 一致。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/expenses/2026-03.csv, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: expense, reminder, shell, dollar-sign, correction

---

## [LRN-20260319-001] correction

**Logged**: 2026-03-19T03:08:00Z
**Priority**: low
**Status**: pending
**Area**: config

### Summary
When fallback configuration is discussed, verify the live config file before treating earlier memory notes as the current truth.

### Details
I initially reported a mismatch between remembered fallback history and the current model failover chain. The user clarified that the change was intentional: they manually simplified the disaster-recovery chain and consider Claude Sonnet 4.6 sufficient, so Sonnet 4.5 is no longer needed in the main fallback order.

### Suggested Action
For model/fallback questions, present the live config as authoritative and treat memory entries as historical context only. If there is a difference, explicitly say it may reflect a deliberate later change instead of implying drift.

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/openclaw.json, memory/2026-03-19.md
- Tags: fallback, models, correction, config, memory

---

## [LRN-20260320-001] correction

**Logged**: 2026-03-20T06:59:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
專題討論表單評論不能只寫「約 30 字」；若表單要求至少 30 字，就要把最低字數當成硬限制，生成更保險的長度。

### Details
使用者明確提醒「表單要求的是至少 30 字」。我先前在 special-topic-discussion skill 中把輸出描述成「around 30 Chinese characters」與「roughly 30」，這種寫法容易讓生成結果卡在門檻邊緣，造成表單不通過或需要手動補字。

### Suggested Action
之後遇到這類表單，先抓最低字數要求；若要求至少 30 字，評論目標應放在略高於門檻的安全區間，例如 32–45 字，而不是貼著 30 字生成。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md
- Tags: forms, length-limit, special-topic-discussion, correction

---

## [LRN-20260320-002] correction

**Logged**: 2026-03-20T07:20:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
專題討論流程中，把結果同步到 GitHub 不應視為可選收尾；對這位使用者來說，這是固定流程的一部分。

### Details
使用者明確提醒「要更新到 github，請注意這必須是固定流程」。這表示 special-topic-discussion workflow 不只是在需要時才存檔，而是只要已生成可用稿、尤其在同一天追加新講者時，就應預設更新既有草稿並推送到 `Myclawagi/Special Topic Discussion/`，除非使用者明確要求先不要推。

### Suggested Action
將 GitHub 同步寫成 special-topic-discussion skill、USER.md、MEMORY.md 內的固定預設規則；後續執行此流程時，把 push 視為默認步驟，不再等使用者每次額外提醒。

### Metadata
- Source: user_feedback
- Related Files: /home/node/.openclaw/workspace/skills/special-topic-discussion/SKILL.md, /home/node/.openclaw/workspace/USER.md, /home/node/.openclaw/workspace/MEMORY.md
- Tags: workflow, github, special-topic-discussion, correction

---

## [LRN-20260402-001] best_practice

**Logged**: 2026-04-02T15:46:00Z
**Priority**: medium
**Status**: pending
**Area**: config

### Summary
在 Telegram exec approvals 流程中，若已經有待批准命令，就不要再插入額外的探索性 shell 指令，避免使用者收到不相干或延遲的 approval 卡而混淆當前任務。

### Details
本次記帳流程中，我為了查 reminder bot 發送方式，額外跑了 `grep` 類型的探索性 shell 指令。由於 Telegram exec approvals 會為 host exec 產生批准卡，這讓使用者後續看到的 approval 訊息不一定對應當下聊天裡提到的那個步驟，甚至出現看似與記帳流程無關的 `sync-to-github.sh` 批准訊息，增加理解成本。正確做法是在 live chat、尤其 approval-sensitive 的 Telegram 對話中，優先使用不需 exec 的工具；若確實需要 exec，應盡量只送出與當前任務直接相關的固定指令。

### Suggested Action
之後在 Telegram live chat 中，只要已經進入 approval 流程，就避免再加跑額外 shell 探查。對記帳流程，優先用固定腳本與直接讀檔驗證，少用臨時 `grep`/`bash` 探索命令，降低 approval 卡錯位或延遲造成的混亂。

### Metadata
- Source: conversation
- Related Files: /home/node/.openclaw/workspace/TOOLS.md, /home/node/.openclaw/workspace/skills/expense-tracker/SKILL.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: telegram, exec-approvals, expense, workflow, best-practice

---

## [LRN-20260403-001] correction

**Logged**: 2026-04-03T15:32:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Todo plugin 沒有出現在工具清單時，不能先假設缺的是 `tools.allow`；要先檢查 `openclaw status` / config warnings，因為真正的 blocker 可能是 `plugins.allow` 或插件路徑權限。

### Details
我原本推測 `todo-api-tools` 沒出現在工具清單，是因為 `tools.allow` 沒補上，所以先往那個方向處理。但在實際執行 `openclaw gateway restart && openclaw status` 後，真正的警告是：`plugins.allow` 未設、以及 `/home/node/.openclaw/extensions/todo-api-tools/index.js` 是 world-writable（mode 666），因此 plugin candidate 被 block，`plugins.entries.todo-api-tools` 也被當成 stale config entry 忽略。這代表先前對根因的判斷不夠準，應該先看 live status / config warnings，而不是直接依 README 猜測。

### Suggested Action
之後遇到「插件已安裝但工具沒出現」時，先做三件事：1) 查 `openclaw status` 的 config warnings，2) 檢查是否需要 `plugins.allow` 而不是 `tools.allow`，3) 檢查 extension 檔案權限是否過寬而被 block。確認根因後再改 config，避免做錯方向的修補。

### Metadata
- Source: conversation
- Related Files: /home/node/.openclaw/openclaw.json, /home/node/.openclaw/extensions/todo-api-tools/index.js, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: plugin, openclaw, todo, config, correction, permissions

---

## [LRN-20260404-002] best_practice

**Logged**: 2026-04-04T06:03:00Z
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
在 Telegram 想關掉手動 exec 批准時，不能只關 `channels.telegram.accounts.default.execApprovals.enabled`；還要同步放寬 host exec policy，否則 gateway host 仍可能在沒有 approval client 時直接拒跑命令。

### Details
使用者希望恢復成「不需要手動批准」的舊體驗。我先把 Telegram account 的 `execApprovals.enabled` 關掉，並誤以為這樣就足夠；但實際再次執行 Todo API 的 `exec` 時，OpenClaw 仍回報「Exec approval is required, but no interactive approval client is currently available」，表示真正卡住的是 gateway host 的 approvals policy，而不是 Telegram prompt surface 本身。後續查文件並直接修正設定後，確認需要同時處理兩層：1) `~/.openclaw/openclaw.json` 的 `tools.exec`，2) `~/.openclaw/exec-approvals.json` 的 host-local policy。把兩者都改成 `security=full`, `ask=off`（並讓 host `askFallback=full`）後，立刻成功免批准新增 Todo，證明這才是完整修法。

### Suggested Action
之後只要使用者說「不要再手動批准 exec」，就直接檢查並同步處理三件事：1) chat surface 的 `execApprovals.enabled`，2) `tools.exec` 的 host/security/ask，3) `exec-approvals.json` 的 host-local defaults / agent policy。不要再把「關掉 Telegram approval prompt」誤當成「host exec 已經免批准」。

### Metadata
- Source: conversation
- Related Files: /home/node/.openclaw/openclaw.json, /home/node/.openclaw/exec-approvals.json, /home/node/.openclaw/workspace/TOOLS.md, /home/node/.openclaw/workspace/.learnings/LEARNINGS.md
- Tags: openclaw, telegram, exec, approvals, config, best_practice
- Promoted: TOOLS.md

---
