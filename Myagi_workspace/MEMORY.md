# Memory

## 使用者
> 基本資料與偏好詳見 USER.md，此處僅記錄 USER.md 未涵蓋的補充規則。

- 回覆格式：先 3 行重點 + 短摘要，細節放附件/PDF
- 若指定安裝某個 ClawHub skill，偏好完整安裝不要遺漏；若 `clawhub install` 受 rate limit 或其他限制，可接受改用手動下載/解包安裝
- 專題討論輸入偏好：若希望評論更有深度，PPT 截圖比只有題目更有幫助；封面可作背景，但最好再附方法頁、結果頁或結論頁
- 主力個人電腦作業系統：Windows

## Vega（我）
- 2026-02-17 命名為 Atlas 🛰️
- 2026-03-10 更名為 Vega 🌌
- 個性：理工感、直白、不囉唆

## 系統架構
- OpenClaw 版本：`2026.3.24`（2026-03-27 確認；歷程：2026.3.8 → 2026.3.11 → 2026.3.13 → 2026.3.22 → 2026.3.23 → 2026.3.24）
- Workspace 已採用 proactive-agent 的「中整合」：使用 `SESSION-STATE.md`、`notes/open-loops.md`、`notes/areas/recurring-patterns.md` 與輕量 heartbeat 維護；不啟用 full WAL、`memory/working-buffer.md`、full proactive tracking
- 預設模型：openai-codex/gpt-5.4
- 現行模型容災：`openai-codex/gpt-5.4` → `anthropic/claude-opus-4-6`；使用者已決定 main fallback 不保留 `anthropic/claude-sonnet-4-6`，也不再把 `openai/gpt-5.4` 放進 main fallback，以避免 session 一旦滑到其他路線後不易切回 Codex。策略為訂閱優先，不再把 OpenAI API key 作為 main fallback。
- OpenClaw 可同時配置 `openai` API key 與 `openai-codex` OAuth / subscription，兩者不互斥；但 `openai-codex/*` 模型不會自動改吃 `openai` API key，若 Codex 認證失效需獨立重新登入
- 可切換模型：openai-codex/gpt-5.3-codex、openai-codex/gpt-5.4、openai/gpt-5-mini（alias: `gpt-mini`）、anthropic/claude-opus-4-6、anthropic/claude-sonnet-4-5、anthropic/claude-sonnet-4-6
- Browser 功能已啟用；目前雲端主機未安裝 Chromium/Chrome，因此 `openclaw` 托管瀏覽器暫時無法直接啟動，但 remote browser sandbox / Remote CDP 已實測可用
- 通知通道：Telegram 正常；LINE 目前仍維持停用，已知原因是 plugin crash（`Cannot redefine property: isSenderAllowed`；至少在 OpenClaw `2026.3.22`、`2026.3.23` 曾確認受影響）；Discord 不作為溝通工具或備援通道規劃
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
- 每日 08:40 (Asia/Taipei)：防曬提醒 → reminder bot
- 天堂W BOSS/活動提醒：多個每日+每週排程，含 LINE 備援版
- 記帳週報：每週日 21:00 (Asia/Taipei) → reminder bot
- 記帳月報：每月 1 號 09:00 (Asia/Taipei) → reminder bot
- 記帳資料同步 GitHub：每天 23:30 (Asia/Taipei)
- 晶片測試報告提醒：每週一 09:00 + 倒數密集提醒（至 2026-05-11）
- MRAM ECC 文獻晨報曾建立，但目前暫停；若之後恢復，應先確認有穩定全文存取或更高研究價值的流程

## 研究相關
- 2026-02-17：下載整理 STT-MRAM FaECC 論文，筆記已轉繁中
- 2026-02-18：跑 bchtest repo（FFRAM02）RTL 模擬，BCH ECC 全部通過（4 phase、64 筆測試零失敗）
- GitHub repo：github.com/yuming920619-svg/Myclawagi

