# ECC Memory Design & Fault Injection Framework
本專案實作並驗證一套 **具 ECC 保護之記憶體模組**，目標是在 RTL 階段提供可重現、可參數化的錯誤情境（fault models），以評估不同 ECC 配置下的偵錯/更正能力與系統行為。

本專案包含：
- ECC encoder/decoder 的 RTL 實作
- fault injection 機制（可控制注入時機/位址/bit mask)

## Features
- [x] ECC scheme: [SEC/BCH/]
- [x] Error injection: [single-bit / multi-bit]
- [x] Simulator: [iverilog] / [VCS] (optional)
- [x] Waveform support: VCD/FSDB (optional)
