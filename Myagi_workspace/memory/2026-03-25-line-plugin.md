# 2026-03-25 — LINE plugin crash isolation

## 重要結論
- source: chat + live probe
- tags: #line #plugin #crash #workaround
- note: 把舊的 user-installed LINE plugin 移出 `~/.openclaw/extensions/line` 後，問題仍未消失；真正會炸的是 bundled LINE plugin，錯誤仍指向 `/app/extensions/line/index.ts`，並報 `TypeError: Cannot redefine property: isSenderAllowed`。

## Workaround 驗證
- source: chat + live probe
- tags: #line #config #telegram #verification
- note: 只要在臨時 config 中把 `plugins.entries.line.enabled=false`，`openclaw status --deep` 就可正常跑完，Telegram 也恢復正常。這確認目前穩定 workaround 就是停用 LINE plugin。

## 備註
- canonical summary 已整理進 `memory/2026-03-25.md`
- 舊 plugin 備份位置：`~/.openclaw/plugin-backups/_disabled-line-20260325-160946`
