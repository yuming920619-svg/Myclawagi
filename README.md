# ECC Memory Design & Fault Injection Framework

本專案實作並驗證一套**具 ECC 保護之記憶體模組**，目標是在 RTL 階段提供可重現、可參數化的錯誤情境（fault models），以評估不同 ECC 配置下的偵錯/更正能力與系統行為。

## Features

- [x] ECC scheme: Hamming SEC / BCH(15,5,t=3) SEC-DED
- [x] Error injection: single-bit / multi-bit（Write-Fail & Read-Disturb）
- [x] Simulator: iverilog / VCS (optional)
- [x] Waveform support: VCD / FSDB (optional)
- [x] Memory Compiler: GUI + CLI 參數化產生完整 RTL

## 目錄結構

| 目錄 | 說明 |
|------|------|
| `hamming1/` | **Hamming(7,4) SEC** — 第一版 ECC fault injection memory macro，附 Memory Compiler（GUI/CLI）可自動產生全套 RTL |
| `bchtest/` | **BCH(15,5,t=3)** — 進階 BCH ECC 實作，支援多 bit 糾錯，含 4-phase 測試（64 筆全通過） |
| `typeout1/` | 第二次下線 ECC Hamming(7,4) SEC fault injection memory macro |
| `scripts/` | 通用工具腳本 |

## Quick Start

### 模擬（以 hamming1 為例）

```bash
cd hamming1
make          # 使用 iverilog 編譯 + 執行 testbench
```

### Memory Compiler（hamming1）

可參數化產生整套 RTL，支援 GUI 與 CLI 兩種模式：

```bash
# GUI 模式（預設）
python3 hamming1/memory_compiler.py

# 強制 CLI（無圖形環境）
python3 hamming1/memory_compiler.py --cli
```

可調整參數：`word`、`word_width`、`mux`、`FAULT`、ECC/WF/RD 開關等。
詳見 [`hamming1/README.md`](hamming1/README.md)。

## ECC 方案比較

| 項目 | hamming1 | bchtest |
|------|----------|---------|
| ECC 類型 | Hamming(7,4) SEC | BCH(15,5,t=3) |
| 糾錯能力 | 1-bit | 最多 3-bit |
| Data width | 4-bit | 4-bit (shortened from 5-bit) |
| Codeword | 7-bit | 15-bit |
| Redundancy | 3-bit | 10-bit |

## License

Private repository — 請勿未經授權散佈。
