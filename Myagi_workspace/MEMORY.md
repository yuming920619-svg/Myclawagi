# Memory

## 使用者
- 碩士班學生，研究方向：**MRAM 上實作 ECC**（STT-MRAM / SOT-MRAM / eMRAM）
- 時區：Asia/Taipei (UTC+8)
- 語言：繁體中文
- 回覆格式：先 3 行重點 + 短摘要，細節放附件/PDF
- 不再預設長任務一定走 sub-agent；依任務性質決定是否背景派工。對背景派工有品質顧慮；若任務需要大量上下文、策略討論或研究判斷，偏好前景直接處理（若背景派工，偏好完成後一次通知）
- Token 策略：偏好訂閱優先（GPT 訂閱 → Claude 訂閱），兩邊都受限時再退回 OpenAI API key；省額度優先降工具回合與上下文長度
- 偏好「踩坑自動提醒」流程：當我偵測到本次任務可能踩坑時，先主動詢問是否記錄；僅在使用者明確同意後寫入 pitfall-loop
- 若指定安裝某個 ClawHub skill，偏好完整安裝不要遺漏；若 `clawhub install` 受 rate limit 或其他限制，可接受改用手動下載/解包安裝
- 對「專題討論」評分草稿流程，GitHub 同步屬於固定流程：生成可用稿後，預設更新 `Myclawagi/Special Topic Discussion/` 並推送，除非使用者明確要求先不要 push
- 若同一天的專題討論草稿需要提供給不同人或做不同措辭版本，偏好另存為獨立檔案（如「第二版」），不要覆蓋原稿

## Vega（我）
- 2026-02-17 命名為 Atlas 🛰️
- 2026-03-10 更名為 Vega 🌌
- 個性：理工感、直白、不囉唆

## 系統架構
- OpenClaw 版本：`2026.3.13`（2026-03-16 確認；歷程：2026.3.8 → 2026.3.11 → 2026.3.13）
- Workspace 已採用 proactive-agent 的「中整合」：使用 `SESSION-STATE.md`、`notes/open-loops.md`、`notes/areas/recurring-patterns.md` 與輕量 heartbeat 維護；不啟用 full WAL、`memory/working-buffer.md`、full proactive tracking
- 預設模型：openai-codex/gpt-5.4
- 現行模型容災：`openai-codex/gpt-5.4` → `anthropic/claude-opus-4-6` → `anthropic/claude-sonnet-4-6` → `openai/gpt-5.4`；使用者已明確決定 **`sonnet-4-6` 就夠，不需要把 `sonnet-4-5` 放進 main fallback**。策略為訂閱優先，API key 最後 fallback
- OpenClaw 可同時配置 `openai` API key 與 `openai-codex` OAuth / subscription，兩者不互斥；但 `openai-codex/*` 模型不會自動改吃 `openai` API key，若 Codex 認證失效需獨立重新登入
- 可切換模型：openai-codex/gpt-5.3-codex、openai-codex/gpt-5.4、openai/gpt-5-mini（alias: `gpt-mini`）、anthropic/claude-opus-4-6、anthropic/claude-sonnet-4-5、anthropic/claude-sonnet-4-6
- Browser 功能已啟用；目前雲端主機未安裝 Chromium/Chrome，因此 `openclaw` 托管瀏覽器暫時無法直接啟動，可改走 Browser Relay 或 Remote CDP
- 通知通道：Telegram + LINE（Discord 備援待設定 target ID）
- Memory search 已可用（2026-03-19 實測可回傳結果）；若結果弱、空白或暫時不可用，仍可由 `skills/memory-retrieval` 的 lexical fallback 補強
- 已建立自我迭代踩坑系統（`skills/pitfall-loop` + `memory/pitfalls.jsonl` + 每週回顧 cron）

## 記帳系統
- 架構：CSV 月檔（`expenses/YYYY-MM.csv`）+ 統計腳本 + 摘要 CSV（`summary.csv`）
- 已封裝為 skill：`skills/expense-tracker/`
- 每筆記帳後即時推送摘要到 Telegram reminder bot（account: reminder）
- 每天 23:30 自動同步 CSV 到 GitHub `Myclawagi/Expense tracking/`（原始月檔 + `summary.csv`，不再產生 Excel）
- 分類：餐飲、飲料、交通、日用品、娛樂、學費、服飾、醫療、其他

## 重要截止日
- **2026-05-11**：晶片測試報告繳交（T18-114D-E0068，教育性晶片，梯次 114D）
  - 已設定提醒：每週一 → 截止前兩週每三天 → 最後一週每天

## 定期任務（Cron）
- 每日 07:30 (UTC+8)：台北天氣提醒
- 天堂W BOSS/活動提醒：多個每日+每週排程，含 LINE 備援版
- 記帳週報：每週日 21:00 (Asia/Taipei) → reminder bot
- 記帳月報：每月 1 號 09:00 (Asia/Taipei) → reminder bot
- 記帳 Excel 同步 GitHub：每天 23:30 (Asia/Taipei)
- 晶片測試報告提醒：每週一 09:00 + 倒數密集提醒（至 2026-05-11）
- MRAM ECC 文獻晨報曾建立，但目前暫停；若之後恢復，應先確認有穩定全文存取或更高研究價值的流程

## 研究相關
- 2026-02-17：下載整理 STT-MRAM FaECC 論文，筆記已轉繁中
- 2026-02-18：跑 bchtest repo（FFRAM02）RTL 模擬，BCH ECC 全部通過（4 phase、64 筆測試零失敗）
- GitHub repo：github.com/yuming920619-svg/Myclawagi

## 待辦 / 未完成
- Discord 備援通道尚缺有效 target ID
- MEMORY.md 定期維護（從日誌精煉重點）
