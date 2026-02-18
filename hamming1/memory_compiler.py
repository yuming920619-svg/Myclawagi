#!/usr/bin/env python3
"""
單檔 Memory Compiler (hamming1)
- 盡量重用 hamming1 現有檔案
- 透過互動式 CLI 讓使用者修改參數
- 一鍵輸出原本多檔案
"""

from __future__ import annotations

import math
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_FILES = [
    "Makefile",
    "run.f",
    "epl_Column_Access_sub.v",
    "epl_Column_Decode_sub.v",
    "epl_Control_Circuit_sub.v",
    "epl_FFRAM02_top_fi.v",
    "epl_Ffbit_n_sub.v",
    "epl_FiRdDist_sub.v",
    "epl_FiWrFail_sub.v",
    "epl_Memory_Array_sub.v",
    "epl_Read_Mux_sub.v",
    "epl_Row_Decode_sub.v",
    "epl_Row_Selection_sub.v",
    "epl_ecc_decoder.v",
    "epl_ecc_encoder.v",
    "epl_testbench_rtl_fi.v",
]

DEFAULTS = {
    "word": 16,
    "word_width": 4,
    "mux": 2,
    "fault": 1,
    "wf_word_mask": "0x0030",
    "rd_word_mask": "0x000C",
    "wf_bit_mask": "0b0000001",
    "rd_bit_mask": "0b0000001",
    "enable_ecc": True,
    "enable_wf": True,
    "enable_rd": True,
    "output_root": str(BASE_DIR / "build"),
    "subfolder": "",
}


def ask(prompt: str, default: str) -> str:
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw if raw else default


def ask_bool(prompt: str, default: bool) -> bool:
    d = "Y/n" if default else "y/N"
    raw = input(f"{prompt} ({d}): ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes", "1", "true", "t"}


def parse_mask(mask: str, width: int) -> int:
    txt = mask.strip().lower().replace("_", "")
    if txt.startswith("0x"):
        val = int(txt, 16)
    elif txt.startswith("0b"):
        val = int(txt, 2)
    else:
        val = int(txt, 10)
    if val < 0:
        raise ValueError("mask 不能是負數")
    maxv = (1 << width) - 1
    return val & maxv


def fmt_mask_hex(value: int, width: int) -> str:
    n_hex = max(1, math.ceil(width / 4))
    return f"{width}'h{value:0{n_hex}X}"


def fmt_mask_bin(value: int, width: int) -> str:
    return f"{width}'b{value:0{width}b}"


def calc_ecc_width(word_width: int, enable_ecc: bool) -> int:
    if not enable_ecc:
        return 0
    # hamming 條件：2^r >= m + r + 1
    r = 0
    while (1 << r) < (word_width + r + 1):
        r += 1
    return r


def build_spec(params: dict) -> str:
    word = params["word"]
    word_width = params["word_width"]
    mux = params["mux"]
    fault = params["fault"]
    ecc_width = params["ecc_width"]
    tword_width = word_width + ecc_width
    column = tword_width * mux
    row = word // mux
    total = row * column
    addr_width = int(math.log2(word))
    addr_ay = int(math.log2(mux))
    addr_ax = addr_width - addr_ay

    return "\n".join([
        "//EPLFFRAM02_spec.vh",
        f"`define WORD             {word}      // 總共有幾個 word",
        f"`define WORD_WIDTH       {word_width}       // 每個 word 寬度（bits）",
        f"`define TWORD_WIDTH      {tword_width}       // WORD_WIDTH + ECC_WIDTH",
        f"`define ECC_WIDTH        {ecc_width}       //所需要的給ECC的冗餘bits",
        f"`define MUX              {mux}       // 多工器",
        f"`define FAULT            {fault}      // 故障命令寬度",
        f"`define COLUMN           {column}      // TWORD_WIDTH * MUX",
        f"`define ROW              {row}      // WORD/MUX",
        f"`define TOTAL            {total}     // ROW*COLUMN",
        f"`define ADDR_WIDTH       {addr_width}       // log2(WORD)",
        f"`define ADDR_AX          {addr_ax}       // row address bits A[m-1:log2(mux)]",
        f"`define ADDR_AXO         {1 << addr_ax}      // 2^ADDR_AX",
        f"`define ADDR_AY          {addr_ay}       // column mux select bits Ay = A[log2(mux)-1:0]",
        f"`define ADDR_AYO         {1 << addr_ay}       // 2^ADDR_AY",
        "",
    ])


def patch_top(top_text: str, params: dict) -> str:
    top_text = re.sub(r"`define FI_WF_WORD_MASK\s+[^\n]+", f"`define FI_WF_WORD_MASK {fmt_mask_hex(params['wf_word_mask_int'], params['word'])}", top_text)
    top_text = re.sub(r"`define FI_WF_BIT_MASK\s+[^\n]+", f"`define FI_WF_BIT_MASK  {fmt_mask_bin(params['wf_bit_mask_int'], params['tword_width'])}", top_text)
    top_text = re.sub(r"`define FI_RD_WORD_MASK\s+[^\n]+", f"`define FI_RD_WORD_MASK {fmt_mask_hex(params['rd_word_mask_int'], params['word'])}", top_text)
    top_text = re.sub(r"`define FI_RD_BIT_MASK\s+[^\n]+", f"`define FI_RD_BIT_MASK  {fmt_mask_bin(params['rd_bit_mask_int'], params['tword_width'])}", top_text)
    top_text = re.sub(r"`define FI_WF_FORCE_ZERO\s+[^\n]+", "`define FI_WF_FORCE_ZERO 1'b1", top_text)
    return top_text


def ecc_encoder_passthrough() -> str:
    return """// epl_ecc_encoder.v (generated passthrough when ECC disabled)
`include "EPLFFRAM02_spec.vh"

module epl_ecc_encoder (
    pDATA_i,
    pWRITE_i,
    pVALIDE_o,
    pCODEWORD_o,
    pCcodeword_o,
    pCLK_i,
    nRST_i
);

input  [`WORD_WIDTH-1:0] pDATA_i;
input                    pWRITE_i;
input                    pCLK_i;
input                    nRST_i;
output                   pVALIDE_o;
output [`TWORD_WIDTH-1:0] pCODEWORD_o;
output reg [6:0]         pCcodeword_o;

assign pVALIDE_o = pWRITE_i;
assign pCODEWORD_o = (pWRITE_i) ? pDATA_i[`TWORD_WIDTH-1:0] : {`TWORD_WIDTH{1'b0}};

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
        pCcodeword_o <= 7'b0;
    else if (pWRITE_i)
        pCcodeword_o <= { {(7-`TWORD_WIDTH){1'b0}}, pDATA_i[`TWORD_WIDTH-1:0] };
    else
        pCcodeword_o <= 7'b0;
end

endmodule
"""


def ecc_decoder_passthrough() -> str:
    return """// epl_ecc_decoder.v (generated passthrough when ECC disabled)
`include "EPLFFRAM02_spec.vh"

module epl_ecc_decoder (
    pPARITYDATA_i,
    pREAD_i,
    pDATA_o,
    pCLK_i,
    nRST_i,
    pERROR_o
);

input  [`TWORD_WIDTH-1:0] pPARITYDATA_i;
input                     pREAD_i;
input                     pCLK_i;
input                     nRST_i;
output reg [`WORD_WIDTH-1:0] pDATA_o;
output reg pERROR_o;

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
    begin
        pDATA_o <= {`WORD_WIDTH{1'b0}};
        pERROR_o <= 1'b0;
    end
    else if (pREAD_i)
    begin
        pDATA_o <= pPARITYDATA_i[`WORD_WIDTH-1:0];
        pERROR_o <= 1'b0;
    end
    else
    begin
        pDATA_o <= {`WORD_WIDTH{1'b0}};
        pERROR_o <= 1'b0;
    end
end

endmodule
"""


def fi_wf_passthrough() -> str:
    return """// epl_FiWrFail_sub.v (generated passthrough when WF FI disabled)
`include "EPLFFRAM02_spec.vh"

module epl_FiWrFail_sub (
    pA_i,
    pWRITE_i,
    pFS_i,
    pFiWordMask_i,
    pFiBitMask_i,
    pFiForceZero_i,
    pCODEWORD_i,
    pCODEWORD_o
);
input  [`ADDR_WIDTH-1:0]  pA_i;
input                     pWRITE_i;
input  [`FAULT-1:0]       pFS_i;
input  [`WORD-1:0]        pFiWordMask_i;
input  [`TWORD_WIDTH-1:0] pFiBitMask_i;
input                     pFiForceZero_i;
input  [`TWORD_WIDTH-1:0] pCODEWORD_i;
output [`TWORD_WIDTH-1:0] pCODEWORD_o;
assign pCODEWORD_o = pCODEWORD_i;
endmodule
"""


def fi_rd_passthrough() -> str:
    return """// epl_FiRdDist_sub.v (generated passthrough when RD FI disabled)
`include "EPLFFRAM02_spec.vh"

module epl_FiRdDist_sub (
    pA_i,
    pREAD_i,
    pFIEN_i,
    pFiWordMask_i,
    pFiBitMask_i,
    pPARITYDATA_i,
    pPARITYDATA_o
);
input  [`ADDR_WIDTH-1:0]  pA_i;
input                     pREAD_i;
input                     pFIEN_i;
input  [`WORD-1:0]        pFiWordMask_i;
input  [`TWORD_WIDTH-1:0] pFiBitMask_i;
input  [`TWORD_WIDTH-1:0] pPARITYDATA_i;
output [`TWORD_WIDTH-1:0] pPARITYDATA_o;
assign pPARITYDATA_o = pPARITYDATA_i;
endmodule
"""


def compile_output(params: dict) -> Path:
    out_root = Path(params["output_root"]).expanduser().resolve()
    out_dir = out_root / params["subfolder"] if params["subfolder"].strip() else out_root
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in TEMPLATE_FILES:
        shutil.copy2(BASE_DIR / name, out_dir / name)

    # Derived mask with module enable switches
    wf_word = params["wf_word_mask_int"] if params["enable_wf"] else 0
    wf_bit = params["wf_bit_mask_int"] if params["enable_wf"] else 0
    rd_word = params["rd_word_mask_int"] if params["enable_rd"] else 0
    rd_bit = params["rd_bit_mask_int"] if params["enable_rd"] else 0

    params = dict(params)
    params["wf_word_mask_int"] = wf_word
    params["wf_bit_mask_int"] = wf_bit
    params["rd_word_mask_int"] = rd_word
    params["rd_bit_mask_int"] = rd_bit

    # 1) spec
    (out_dir / "EPLFFRAM02_spec.vh").write_text(build_spec(params), encoding="utf-8")

    # 2) top: only patch FI mask define defaults
    top_src = (BASE_DIR / "epl_FFRAM02_top_fi.v").read_text(encoding="utf-8")
    (out_dir / "epl_FFRAM02_top_fi.v").write_text(patch_top(top_src, params), encoding="utf-8")

    # 3) module switches
    if not params["enable_wf"]:
        (out_dir / "epl_FiWrFail_sub.v").write_text(fi_wf_passthrough(), encoding="utf-8")
    if not params["enable_rd"]:
        (out_dir / "epl_FiRdDist_sub.v").write_text(fi_rd_passthrough(), encoding="utf-8")
    if not params["enable_ecc"]:
        (out_dir / "epl_ecc_encoder.v").write_text(ecc_encoder_passthrough(), encoding="utf-8")
        (out_dir / "epl_ecc_decoder.v").write_text(ecc_decoder_passthrough(), encoding="utf-8")

    return out_dir


def read_params_from_cli() -> dict:
    print("=== hamming1 Memory Compiler ===")
    print("提示：目前模板原始版本是 WORD=16, WORD_WIDTH=4, MUX=2。")

    word = int(ask("word 數", str(DEFAULTS["word"])))
    word_width = int(ask("word 寬度", str(DEFAULTS["word_width"])))
    mux = int(ask("mux 數量", str(DEFAULTS["mux"])))
    fault = int(ask("FAULT 寬度", str(DEFAULTS["fault"])))

    wf_word_mask = ask("WF word mask (支援 0x/0b/十進位)", DEFAULTS["wf_word_mask"])
    rd_word_mask = ask("RD word mask (支援 0x/0b/十進位)", DEFAULTS["rd_word_mask"])
    wf_bit_mask = ask("WF bit mask (支援 0x/0b/十進位)", DEFAULTS["wf_bit_mask"])
    rd_bit_mask = ask("RD bit mask (支援 0x/0b/十進位)", DEFAULTS["rd_bit_mask"])

    enable_ecc = ask_bool("是否啟用 ECC", DEFAULTS["enable_ecc"])
    enable_wf = ask_bool("是否啟用 WF 故障注入模組", DEFAULTS["enable_wf"])
    enable_rd = ask_bool("是否啟用 RD 故障注入模組", DEFAULTS["enable_rd"])

    output_root = ask("輸出根目錄", DEFAULTS["output_root"])
    subfolder = ask("輸出子資料夾名稱（留空代表不使用）", DEFAULTS["subfolder"])

    if word <= 0 or word & (word - 1):
        raise ValueError("word 必須是 2 的次方")
    if mux <= 0 or mux & (mux - 1):
        raise ValueError("mux 必須是 2 的次方")
    if word % mux != 0:
        raise ValueError("word 必須可被 mux 整除")
    if word_width <= 0:
        raise ValueError("word_width 必須 > 0")
    if fault <= 0:
        raise ValueError("FAULT 必須 > 0")

    ecc_width = calc_ecc_width(word_width, enable_ecc)
    tword_width = word_width + ecc_width

    if enable_ecc and word_width != 4:
        print("[警告] 現有 ECC RTL 是針對 4-bit data；已保留原寫法，非 4-bit 可能需自行擴充 ECC 模組。")

    return {
        "word": word,
        "word_width": word_width,
        "mux": mux,
        "fault": fault,
        "ecc_width": ecc_width,
        "tword_width": tword_width,
        "wf_word_mask_int": parse_mask(wf_word_mask, word),
        "rd_word_mask_int": parse_mask(rd_word_mask, word),
        "wf_bit_mask_int": parse_mask(wf_bit_mask, tword_width),
        "rd_bit_mask_int": parse_mask(rd_bit_mask, tword_width),
        "enable_ecc": enable_ecc,
        "enable_wf": enable_wf,
        "enable_rd": enable_rd,
        "output_root": output_root,
        "subfolder": subfolder.strip(),
    }


def main() -> None:
    try:
        params = read_params_from_cli()
        out_dir = compile_output(params)
    except Exception as exc:
        print(f"[失敗] {exc}")
        raise SystemExit(1)

    print("\n[完成] 已輸出到:", out_dir)
    print("主要設定：")
    print(f"- WORD={params['word']}, WORD_WIDTH={params['word_width']}, MUX={params['mux']}, FAULT={params['fault']}")
    print(f"- ECC={'ON' if params['enable_ecc'] else 'OFF'}, WF={'ON' if params['enable_wf'] else 'OFF'}, RD={'ON' if params['enable_rd'] else 'OFF'}")
    print(f"- WF word mask={fmt_mask_hex(params['wf_word_mask_int'], params['word'])}")
    print(f"- RD word mask={fmt_mask_hex(params['rd_word_mask_int'], params['word'])}")
    print(f"- WF bit mask={fmt_mask_bin(params['wf_bit_mask_int'], params['tword_width'])}")
    print(f"- RD bit mask={fmt_mask_bin(params['rd_bit_mask_int'], params['tword_width'])}")


if __name__ == "__main__":
    main()
