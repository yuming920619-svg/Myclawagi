# hamming1 Memory Compiler

此目錄提供 `memory_compiler.py`，可用**單一 Python 檔**產生原本 `hamming1` 所需的多個 RTL/測試檔案。

## 功能重點

- 內建 **Tkinter GUI**（可直接打字、勾選開關、填輸出路徑、按按鈕生成）
- 保留 **CLI fallback**（在無 GUI 環境可照常使用）
- 可顯示「**當前記憶體容量**」（Bytes / KB / MB / GB 自動換算）
- `word_width` 不再限制 4-bit，支援 **1~1024**
- 盡量維持原本模板與生成流程相容

## 使用方式

在 `hamming1/` 內執行：

```bash
python3 memory_compiler.py
```

- 預設會先嘗試啟動 GUI。
- 若環境沒有圖形介面（例如無 DISPLAY / 無 tkinter），會自動 fallback 到 CLI。

### 強制模式

```bash
# 強制 CLI
python3 memory_compiler.py --cli

# 強制 GUI（若啟動失敗會直接報錯）
python3 memory_compiler.py --gui
```

## GUI 介面說明

GUI 主要欄位：
- 數值參數：`word`、`word_width`、`mux`、`FAULT`
- mask 參數：`WF word mask`、`RD word mask`、`WF bit mask`、`RD bit mask`
- 開關：`Enable ECC`、`Enable WF`、`Enable RD`
- 輸出：`output_root`、`subfolder`

按鈕：
- **更新容量**：依目前參數重新計算容量
- **生成**：輸出 RTL 檔案

容量顯示：
- 會依 `WORD * TWORD_WIDTH` 計算總 bit 數，再換算為 Bytes / KB / MB / GB 顯示
- 例如顯示：`總容量：64 KB`

## 參數限制

- `word`：必須是 2 的次方，且可被 `mux` 整除
- `mux`：必須是 2 的次方
- `word_width`：必須是 1~1024 的整數
- `FAULT`：必須 > 0

## 輸出路徑規則

- 若有填 `subfolder`：輸出到 `output_root/subfolder`
- 若 `subfolder` 留空：直接輸出到 `output_root`

## 產出內容

會產生/複製原本 `hamming1` 需要的主要檔案：
- `EPLFFRAM02_spec.vh`
- `epl_FFRAM02_top_fi.v`
- `epl_FiWrFail_sub.v`
- `epl_FiRdDist_sub.v`
- `epl_ecc_encoder.v`
- `epl_ecc_decoder.v`
- 其他既有子模組、`run.f`、`Makefile`、`epl_testbench_rtl_fi.v`

## 備註

- 當關閉 ECC / WF / RD 時，compiler 會輸出對應 passthrough 版本模組，以保留整體介面與流程。
- 若啟用 ECC 且 `word_width != 4`，會提示：既有 ECC RTL 原始設計是針對 4-bit data，非 4-bit 可能需自行擴充 ECC 模組。
