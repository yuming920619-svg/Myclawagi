# Myclawagi Repository

這個 repo 現在比較接近一個**個人研究 / 工具 / 工作流的 monorepo**，不再只是單一的 ECC memory framework。

核心主軸仍然是 **ECC memory design、fault injection、RTL simulation 與研究整理**，但目前也已納入一些日常工作流與個人自動化內容，例如記帳資料、專題討論草稿，以及 AI workspace 設定與技能。

## 目前包含的內容

- **ECC Memory Design / Verification**
  - Hamming 相關 RTL、testbench、fault injection 模組
  - 以 RTL simulation 驗證錯誤偵測 / 更正行為
- **Research / Workflow Assets**
  - 專題討論草稿
  - 記帳資料與摘要
  - AI workspace 與 skills

## Repository Structure

| 目錄 | 說明 |
|------|------|
| `hamming1/` | **Hamming(7,4) SEC** fault injection memory macro |
| `typeout1/` | 第二版 / 第二次下線的 Hamming-based ECC memory macro 相關檔案 |
| `Expense tracking/` | 個人記帳資料（CSV）與統計摘要 |
| `Special Topic Discussion/` | 專題討論 / 評分表 / 草稿存放區 |
| `Myagi_workspace/` | AI workspace 相關設定、記憶、skills 與維護檔案 |
| `scripts/` | 雜項工具腳本 |

## Notes

- 這個 repo 目前是**混合型工作倉庫**，所以不是所有資料夾都屬於同一個研究主題。
- 若只關注 RTL / ECC 設計，請優先閱讀 `hamming1/`、`typeout1/`。
- `Expense tracking/`、`Special Topic Discussion/`、`Myagi_workspace/` 屬於個人工作流內容，與 ECC 主線不同。

## License / Access

Private repository — 內含研究檔案、個人工作流資料與部分私人內容，請勿未經授權散佈。
