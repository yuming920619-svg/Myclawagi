# hamming1 Memory Compiler

此目錄新增 `memory_compiler.py`，可用**單一 Python 檔**一鍵產生原本 `hamming1` 所需的多個 RTL/測試檔案。

## 使用方式

在 `hamming1/` 內執行：

```bash
python3 memory_compiler.py
```

依序輸入互動式參數：
- word 數
- word 寬度
- mux 數量
- FAULT 寬度
- WF word mask
- RD word mask
- WF bit mask
- RD bit mask
- 是否啟用 ECC
- 是否啟用 WF 故障注入模組
- 是否啟用 RD 故障注入模組
- 輸出根目錄
- 輸出子資料夾名稱（可留空）

## 輸出路徑規則

- 若有填「子資料夾名稱」：輸出到 `root/subfolder`
- 若子資料夾留空：直接輸出到 `root`

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

- 實作優先重用既有 `hamming1` 模板與流程，僅在 compiler 必要處理時改動。
- 當關閉 ECC / WF / RD 時，compiler 會輸出對應的 passthrough 版本模組，以保留整體介面與流程。