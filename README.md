# ECC Memory Design & Fault Injection Framework
本專案實作並驗證一套 **具 ECC 保護之記憶體模組**，目標是在 RTL 階段提供可重現、可參數化的錯誤情境（fault models），以評估不同 ECC 配置下的偵錯/更正能力與系統行為。

本專案包含：
- ECC encoder/decoder 的 RTL 實作
- fault injection 機制（可控制注入時機/位址/bit mask)

## Features
- [x] ECC scheme: [SEC/BCH]
- [x] Error injection: [single-bit / multi-bit]
- [x] Simulator: [iverilog] / [VCS] (optional)
- [x] Waveform support: VCD/FSDB (optional)

## Utility: PDF/Word 文字抽取
新增 `scripts/extract_text.py`，可把文件轉成純文字供後續分析。

### 支援格式
- `.pdf`（優先用 `pdftotext`，否則嘗試 `pypdf` / `PyPDF2`）
- `.docx`（內建解析，不需額外套件）
- `.doc`（需安裝 `antiword`）

### 用法
```bash
# 輸出到 stdout
python3 scripts/extract_text.py hamming1/hamming_rules.docx --stdout

# 產生同名 .txt
python3 scripts/extract_text.py hamming1/hamming.pdf

# 指定輸出檔名
python3 scripts/extract_text.py hamming1/hamming.pdf -o hamming1/hamming.txt
```

### 依賴提示（PDF/.doc）
若遇到工具缺失，可安裝：
- Ubuntu/Debian: `sudo apt-get install -y poppler-utils antiword`
- Python fallback: `pip install pypdf`
