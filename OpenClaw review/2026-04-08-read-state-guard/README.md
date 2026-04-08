# OpenClaw review — read-state guard landing

## Summary

這批內容是把使用者提供的 `openclaw_impl_spec`，先以 **runtime-first** 方式落到目前 OpenClaw upstream 骨架中的第一個增量實作。

核心 commit：`73a039d`  
Subject：`feat(agents): guard edits with prior full reads`

## What changed

### New files
- `src/agents/tool-path-resolution.ts`
- `src/agents/tool-read-state.ts`
- `src/agents/tool-read-state.test.ts`
- `docs/refactor/openclaw-runtime-first-adaptation.md`

### Modified files
- `src/agents/pi-tools.ts`
- `src/agents/pi-tools.read.ts`

## Behavior landed

- `read` 會在單次 run 內追蹤完整讀過的檔案狀態
- `edit` 前若沒有完整讀過檔案，會直接擋下
- `edit` 前若只做過 partial read（例如 `offset` / `limit` / truncated），也會擋下
- `edit` 前若檔案在讀完之後被外部改動，會擋下
- host / sandbox 兩條工具路徑都有接上

## Why this slice first

這一塊最容易和現有 OpenClaw 架構整合，而且價值高：

- 它補上現有 edit recovery 缺的安全語義
- 不需要先重寫整個 tool runtime
- 不會和現有 session / skills / compaction 系統正面衝突

## Verification

已完成：
- wrapper-level smoke check
- `pi-tools.ts` import smoke check
- `createOpenClawCodingTools()` 建構 smoke check

尚未完成：
- 完整 vitest suite

原因：目前操作環境是 build artifact + source clone 的混合狀態，不是完整 dev install。

## Review guide

建議先看：
1. `73a039d-read-state-guard.patch`
2. `docs/refactor/openclaw-runtime-first-adaptation.md`

若你只想抓主線，優先注意：
- `tool-read-state.ts` 的狀態模型是不是太保守/太鬆
- `pi-tools.ts` 的整合點會不會和現有 wrapper 疊太多層
- run-scoped state 是否足夠，或未來是否要 session-scoped
