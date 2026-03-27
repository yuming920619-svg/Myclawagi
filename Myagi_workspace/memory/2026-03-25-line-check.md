# 2026-03-25 — LINE recheck and docs review

## 版本再檢查
- source: chat + live probe
- tags: #line #version #upgrade
- note: 使用者表示已升級到 `2026.3.23-2`，但當時這個 workspace 看到的 runtime 仍顯示 `2026.3.23`；因此若在那個時間點重測 LINE，也只會驗證到舊版 runtime，不足以證明 `2026.3.23-2` 是否已真正套用。

## 對照官方文件後的判斷
- source: chat + docs review
- tags: #line #config #docs #webhook
- note: LINE 設定欄位本身看不出明顯拼錯；更像是 plugin 載入 crash 與 webhook 對外可達性問題。若未來重啟 LINE，需優先確認 `/line/webhook` 的 HTTPS 公網入口，以及群組模式下是否補齊 allowlist。

## 使用決策
- source: chat
- tags: #line #decision
- note: 使用者明確表示 LINE 目前不會用到，因此這份文件只保留為未來可能回頭排查時的背景，不視為當前待辦。
