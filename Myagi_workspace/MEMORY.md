# Memory

## 使用者
- 碩士班學生，研究方向：**MRAM 上實作 ECC**（STT-MRAM / SOT-MRAM / eMRAM）
- 時區：Asia/Taipei (UTC+8)
- 語言：繁體中文
- 回覆格式：先 3 行重點 + 短摘要，細節放附件/PDF
- 不再預設長任務一定走 sub-agent；依任務性質決定是否背景派工（若背景派工，偏好完成後一次通知）
- Token 策略：Codex 主力、Claude 備援；省額度優先降工具回合與上下文長度
- 偏好「踩坑自動提醒」流程：當我偵測到本次任務可能踩坑時，先主動詢問是否記錄；僅在使用者明確同意後寫入 pitfall-loop
- 若指定安裝某個 ClawHub skill，偏好完整安裝不要遺漏；若 `clawhub install` 受 rate limit 或其他限制，可接受改用手動下載/解包安裝

## Vega（我）
- 2026-02-17 命名為 Atlas 🛰️
- 2026-03-10 更名為 Vega 🌌
- 個性：理工感、直白、不囉唆

## 系統架構
- OpenClaw 已於 2026-03-14 升級至 `2026.3.11`（原先 2026-03-11 為 `2026.3.8`）
- Workspace 已採用 proactive-agent 的「中整合」：使用 `SESSION-STATE.md`、`notes/open-loops.md`、`notes/areas/recurring-patterns.md` 與輕量 heartbeat 維護；不啟用 full WAL、`memory/working-buffer.md`、full proactive tracking
- 預設模型：openai-codex/gpt-5.4
- 現行模型容災（方案 B）：`openai-codex/gpt-5.4` → `anthropic/claude-opus-4-6` → `anthropic/claude-sonnet-4-6` → `anthropic/claude-sonnet-4-5`
- 可切換模型：openai-codex/gpt-5.3-codex、openai-codex/gpt-5.4、anthropic/claude-opus-4-6、anthropic/claude-sonnet-4-5、anthropic/claude-sonnet-4-6
- Browser 功能已啟用；目前雲端主機未安裝 Chromium/Chrome，因此 `openclaw` 托管瀏覽器暫時無法直接啟動，可改走 Browser Relay 或 Remote CDP
- 通知通道：Telegram + LINE（Discord 備援待設定 target ID）
- Memory search 的 embedding API key 未設定，語意搜尋不可用
- 已建立自我迭代踩坑系統（`skills/pitfall-loop` + `memory/pitfalls.jsonl` + 每週回顧 cron）

## 定期任務（Cron）
- 每日 07:30 (UTC+8)：台北天氣提醒
- 天堂W BOSS/活動提醒：多個每日+每週排程，含 LINE 備援版
- MRAM ECC 文獻晨報曾建立，但目前暫停；若之後恢復，應先確認有穩定全文存取或更高研究價值的流程

## 研究相關
- 2026-02-17：下載整理 STT-MRAM FaECC 論文，筆記已轉繁中
- 2026-02-18：跑 bchtest repo（FFRAM02）RTL 模擬，BCH ECC 全部通過（4 phase、64 筆測試零失敗）
- GitHub repo：github.com/yuming920619-svg/Myclawagi

## 待辦 / 未完成
- Discord 備援通道尚缺有效 target ID
- MEMORY.md 定期維護（從日誌精煉重點）
