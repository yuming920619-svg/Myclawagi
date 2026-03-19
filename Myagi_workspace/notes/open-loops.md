# Open Loops

Use this file for unfinished items that should be revisited later.
Keep entries short.

## Template
- [ ] Item
  - Status:
  - Revisit trigger:

## Active
- [ ] 評估是否恢復「每日MRAM ECC文獻晨報」
  - Status: 已暫停；目前認為僅整理摘要、無全文權限時效益偏低
  - Revisit trigger: 若之後拿到穩定全文存取方式，或想改成更有研究價值的版本（例如每週精讀/主題式追蹤）

- [ ] ECCFI2 改版：基於 BCH 理論重新設計 encoder/decoder
  - Status: 暫緩；使用者確認目前先不用做。原因是 repo 內既有 BCH 實作有問題，不想直接沿用舊版
  - Revisit trigger: 之後有空、準備投入重設計時，提醒使用者重新啟動此任務

- [ ] 每日 20:00 提醒買洗衣精（直到使用者說買了）
  - Status: Cron 已啟用（jobId: 98fb4d87-adfa-48f6-afe2-492b2eee0e02），每日 20:00（Asia/Taipei）送 Telegram 提醒
  - Revisit trigger: 使用者回覆「買了洗衣精」→ 停用/刪除該 cron job

