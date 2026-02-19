#!/usr/bin/env python3
"""
單檔 Memory Compiler (hamming1)
- 完全自包含：不依賴外部 .v/.vh 模板檔
- 提供 Tkinter GUI（可直接打字）
- 保留 CLI fallback（互動式問答）

【硬性約束】
- 產出的 ECC 編碼器/解碼器 Verilog 寫法盡量貼近原始 hamming1/ 既有實作風格
- 使用 explicit assign / case，不使用 for-loop 泛化寫法
- 僅允許為了做成 memory compiler 的必要最小改動
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

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
    r = 0
    while (1 << r) < (word_width + r + 1):
        r += 1
    return r


def human_readable_bytes(size_bytes: int) -> str:
    units = ["Bytes", "KB", "MB", "GB"]
    size = float(size_bytes)
    idx = 0
    while size >= 1024 and idx < len(units) - 1:
        size /= 1024
        idx += 1
    if idx == 0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.2f} {units[idx]}"


def calc_capacity_bytes(word: int, tword_width: int) -> int:
    total_bits = word * tword_width
    return (total_bits + 7) // 8


# ---------------------------------------------------------------------------
# Hamming position helpers
# ---------------------------------------------------------------------------

def hamming_data_positions(word_width: int, ecc_width: int) -> list[int]:
    """Return 0-based codeword indices where data bits go (non-power-of-2 positions)."""
    n = word_width + ecc_width
    return [i for i in range(n) if (i + 1) & i != 0]  # pos1 & (pos1-1) != 0


def hamming_parity_positions(ecc_width: int) -> list[int]:
    """Return 0-based codeword indices where parity bits go (power-of-2 positions)."""
    return [(1 << k) - 1 for k in range(ecc_width)]


def hamming_parity_cover(pk_idx: int, n: int) -> list[int]:
    """Return 0-based codeword indices covered by parity bit pk_idx."""
    bit_val = 1 << pk_idx
    return [i for i in range(n) if (i + 1) & bit_val]


# ---------------------------------------------------------------------------
# Parameter building
# ---------------------------------------------------------------------------

def build_params(
    *,
    word: int,
    word_width: int,
    mux: int,
    fault: int,
    wf_word_mask: str,
    rd_word_mask: str,
    wf_bit_mask: str,
    rd_bit_mask: str,
    enable_ecc: bool,
    enable_wf: bool,
    enable_rd: bool,
    output_root: str,
    subfolder: str,
) -> dict:
    if word <= 0 or word & (word - 1):
        raise ValueError("word 必須是 2 的次方")
    if mux <= 0 or mux & (mux - 1):
        raise ValueError("mux 必須是 2 的次方")
    if word % mux != 0:
        raise ValueError("word 必須可被 mux 整除")
    if not (1 <= word_width <= 1024):
        raise ValueError("word_width 必須是 1~1024 的整數")
    if fault <= 0:
        raise ValueError("FAULT 必須 > 0")

    ecc_width = calc_ecc_width(word_width, enable_ecc)
    tword_width = word_width + ecc_width

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
        "capacity_bytes": calc_capacity_bytes(word, tword_width),
    }


# ===========================================================================
# Verilog generators (explicit assign/case style — matching original hamming1)
# ===========================================================================

def gen_spec(p: dict) -> str:
    word = p["word"]
    word_width = p["word_width"]
    mux = p["mux"]
    fault = p["fault"]
    ecc_width = p["ecc_width"]
    tw = word_width + ecc_width
    col = tw * mux
    row = word // mux
    total = row * col
    aw = int(math.log2(word))
    ay = int(math.log2(mux))
    ax = aw - ay
    return "\n".join([
        "//EPLFFRAM02_spec.vh",
        f"`define WORD             {word}      // 總共有幾個 word",
        f"`define WORD_WIDTH       {word_width}       // 每個 word 寬度（bits）",
        f"`define TWORD_WIDTH      {tw}       // WORD_WIDTH + ECC_WIDTH",
        f"`define ECC_WIDTH        {ecc_width}       //所需要的給ECC的冗餘bits",
        f"`define MUX              {mux}       // 多工器",
        f"`define FAULT            {fault}      // 故障命令寬度",
        f"`define COLUMN           {col}      // TWORD_WIDTH * MUX",
        f"`define ROW              {row}      // WORD/MUX",
        f"`define TOTAL            {total}     // ROW*COLUMN",
        f"`define ADDR_WIDTH       {aw}       // log2(WORD)",
        f"`define ADDR_AX          {ax}       // row address bits A[m-1:log2(mux)]",
        f"`define ADDR_AXO         {1 << ax}      // 2^ADDR_AX",
        f"`define ADDR_AY          {ay}       // column mux select bits Ay = A[log2(mux)-1:0]",
        f"`define ADDR_AYO         {1 << ay}       // 2^ADDR_AY",
        "",
    ])


# ---------------------------------------------------------------------------
# ECC Encoder — explicit assign per bit (matches original style)
# ---------------------------------------------------------------------------

def gen_ecc_encoder(p: dict) -> str:
    ww = p["word_width"]
    ew = p["ecc_width"]
    tw = p["tword_width"]
    data_pos = hamming_data_positions(ww, ew)
    parity_pos = hamming_parity_positions(ew)

    lines = []
    lines.append("// epl_ecc_encoder.v")
    lines.append("module epl_ecc_encoder (")
    lines.append("           // Global Ports")
    lines.append("           input         pCLK_i,")
    lines.append("           input         nRST_i,")
    lines.append("           input         pWRITE_i,")
    lines.append("           // Data Ports")
    lines.append(f"           input  [{ww-1}:0]  pDATA_i,")
    lines.append(f"           output [{tw-1}:0] pCODEWORD_o,")
    lines.append(f"           output reg [{tw-1}:0] pCcodeword_o,")
    lines.append("           output pVALIDE_o")
    lines.append("       );")
    lines.append("")
    lines.append(f"wire [{tw-1}:0] pCcodeword_w;")
    lines.append("")
    lines.append("")
    lines.append("// Codeword generation (combinational logic)")

    # Generate assigns from high index to low (matching original order)
    for idx in range(tw - 1, -1, -1):
        if idx in data_pos:
            di = data_pos.index(idx)
            lines.append(f"assign pCODEWORD_o[{idx}] = (pWRITE_i) ? pDATA_i[{di}] : 1'b0;")
        else:
            pk = parity_pos.index(idx)
            covered = hamming_parity_cover(pk, tw)
            # XOR only the data bits in the covered set
            data_in_cover = []
            for ci in covered:
                if ci in data_pos:
                    di = data_pos.index(ci)
                    data_in_cover.append(f"pDATA_i[{di}]")
            xor_expr = " ^ ".join(data_in_cover + ["1'b1"])
            lines.append(f"assign pCODEWORD_o[{idx}] = (pWRITE_i) ? {{{xor_expr}}} : 1'b0;")

    lines.append("")
    lines.append("// The codeword is only valid when pWRITE_i is high.")
    lines.append("assign pVALIDE_o = pWRITE_i;")
    lines.append("assign pCcodeword_w = pCODEWORD_o;")
    lines.append("")
    lines.append("always @(posedge pCLK_i or negedge nRST_i)")
    lines.append("begin")
    lines.append("    if (!nRST_i)")
    lines.append("    begin")
    lines.append(f"        pCcodeword_o <= {tw}'b0;")
    lines.append("    end")
    lines.append("    else  if (pVALIDE_o)")
    lines.append("    begin")
    lines.append("        pCcodeword_o <= pCcodeword_w;")
    lines.append("    end")
    lines.append("    else")
    lines.append("    begin")
    lines.append("        // Clear outputs when read is not valid to avoid stale data/error.")
    lines.append(f"        pCcodeword_o <= {tw}'b0;")
    lines.append("    end")
    lines.append("end")
    lines.append("")
    lines.append("endmodule")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# ECC Decoder — explicit assign per syndrome bit (matches original style)
# ---------------------------------------------------------------------------

def gen_ecc_decoder(p: dict) -> str:
    ww = p["word_width"]
    ew = p["ecc_width"]
    tw = p["tword_width"]
    data_pos = hamming_data_positions(ww, ew)
    parity_pos = hamming_parity_positions(ew)

    lines = []
    lines.append("// epl_ecc_decoder.v")
    lines.append("module epl_ecc_decoder (")
    lines.append("           // Global Ports")
    lines.append("           input         pCLK_i,")
    lines.append("           input         nRST_i,")
    lines.append("")
    lines.append("           // Control Ports")
    lines.append("           input         pREAD_i,")
    lines.append("")
    lines.append("           // Data Ports")
    lines.append(f"           input  [{tw-1}:0]  pPARITYDATA_i,")
    lines.append(f"           output reg [{ww-1}:0]  pDATA_o,")
    lines.append("           output reg    pERROR_o")
    lines.append("       );")
    lines.append("")
    lines.append("// internal signals")
    lines.append(f"wire [{ew-1}:0] pSyndromeRaw_w;")
    lines.append(f"wire [{ew-1}:0] pSyndrome_w;")
    lines.append(f"wire [{ew-1}:0] ErrorPos_w;")
    lines.append("")
    lines.append("// registers for corrected code, next data, error flag, and valid signal")
    lines.append(f"reg [{tw-1}:0] CorrectedCode_w;")
    lines.append(f"reg [{ww-1}:0] pNextData_w;")
    lines.append("reg       pNextError_w;")
    lines.append("reg       pValid_w;        ")
    lines.append("")
    lines.append("// syndrome calculation (combinational logic)")

    # Explicit syndrome assigns
    for pk_idx in range(ew):
        covered = hamming_parity_cover(pk_idx, tw)
        terms = [f"pPARITYDATA_i[{c}]" for c in covered]
        terms.append("1'b1")
        lines.append(f"assign pSyndromeRaw_w[{pk_idx}] = {' ^ '.join(terms)};")

    lines.append("")
    lines.append(f"assign pSyndrome_w = (pREAD_i) ? pSyndromeRaw_w : {ew}'b{'0'*ew};")
    lines.append("assign ErrorPos_w  = pSyndrome_w;")
    lines.append("")
    lines.append("// combinational logic to determine next data, error flag, and valid signal based on read enable and syndrome")
    lines.append("always @(*)")
    lines.append("begin")
    lines.append(f"    // Default values when not reading: outputs are cleared to avoid stale data/error.")
    lines.append(f"    pNextData_w = {ww}'b0;")
    lines.append("    pNextError_w = 0;")
    lines.append("    pValid_w = 0;")
    lines.append("    CorrectedCode_w = pPARITYDATA_i;")
    lines.append("")
    lines.append("    // When read is enabled, calculate corrected data and error flag based on syndrome.")
    lines.append("    if (pREAD_i)")
    lines.append("    begin")
    lines.append(f"        // 1. error correction: if syndrome is non-zero, flip the bit at the indicated position.")
    lines.append(f"        if (ErrorPos_w != {ew}'b{'0'*ew})")
    lines.append("        begin")
    lines.append("            // ErrorPos_w is 1-based index for bit position (1 to %d), so we adjust for 0-based indexing in Verilog." % tw)
    lines.append("            CorrectedCode_w[ErrorPos_w - 1] = ~CorrectedCode_w[ErrorPos_w - 1];")
    lines.append("            pNextError_w = 1;")
    lines.append("        end")
    lines.append("        else")
    lines.append("        begin")
    lines.append("            pNextError_w = 0;")
    lines.append("        end")
    lines.append("")

    # Explicit data extraction (MSB first concatenation, matching original style)
    data_bits_msb_first = [f"CorrectedCode_w[{data_pos[i]}]" for i in range(ww - 1, -1, -1)]
    extract_line = "        pNextData_w = {" + ", ".join(data_bits_msb_first) + "};"
    # Add comment showing data bit positions
    pos_comment = ", ".join([str(dp + 1) for dp in reversed(data_pos)])
    lines.append(f"        // 2. data recovery: extract data bits from the corrected code. Data bits are at positions {pos_comment} (0-based indices {', '.join([str(dp) for dp in reversed(data_pos)])}).")
    lines.append(extract_line)
    lines.append("")
    lines.append("        // 3. valid signal: indicate that the output data and error flag are valid when read is enabled.")
    lines.append("        pValid_w = 1'b1;")
    lines.append("    end")
    lines.append("end")
    lines.append("")
    lines.append("// register outputs on clock edge, with asynchronous reset. Outputs are cleared when not valid to avoid stale data/error.")
    lines.append("always @(posedge pCLK_i or negedge nRST_i)")
    lines.append("begin")
    lines.append("    if (!nRST_i)")
    lines.append("    begin")
    lines.append(f"        pDATA_o   <= {ww}'b0;")
    lines.append("        pERROR_o  <= 1'b0;")
    lines.append("    end")
    lines.append("    else  if (pValid_w)")
    lines.append("    begin")
    lines.append("        pDATA_o  <= pNextData_w;")
    lines.append("        pERROR_o <= pNextError_w;")
    lines.append("    end")
    lines.append("    else")
    lines.append("    begin")
    lines.append("        // Clear outputs when read is not valid to avoid stale data/error.")
    lines.append(f"        pDATA_o  <= {ww}'b0;")
    lines.append("        pERROR_o <= 1'b0;")
    lines.append("    end")
    lines.append("end")
    lines.append("")
    lines.append("")
    lines.append("endmodule")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Row Decode — explicit case per row (matches original style)
# ---------------------------------------------------------------------------

def gen_row_decode(p: dict) -> str:
    row = p["word"] // p["mux"]
    ax = int(math.log2(p["word"])) - int(math.log2(p["mux"]))
    axo = 1 << ax

    lines = []
    lines.append('// epl_Row_Decode_sub.v')
    lines.append('`include "EPLFFRAM02_spec.vh"')
    lines.append('')
    lines.append('module epl_Row_Decode_sub (')
    lines.append('           input  wire [`ADDR_AX-1:0]  pAr_i,')
    lines.append('           output reg [`ADDR_AXO-1:0] pArx_o')
    lines.append('       );')
    lines.append('')
    lines.append('always @(*)')
    lines.append('begin')
    lines.append('    case (pAr_i)')

    for r in range(row):
        one_hot = 1 << r
        bin_str = f"{one_hot:0{axo}b}"
        # Insert underscores every 4 bits from right for readability
        formatted = _format_bin_underscored(bin_str)
        lines.append(f"        {ax}'d{r}:")
        lines.append(f"            pArx_o = {axo}'b{formatted};")

    lines.append(f"        default:")
    lines.append(f"            pArx_o = {axo}'b{'0' * axo};")
    lines.append('    endcase')
    lines.append('end')
    lines.append('')
    lines.append('')
    lines.append('endmodule')
    return "\n".join(lines) + "\n"


def _format_bin_underscored(bin_str: str) -> str:
    """Format binary string with underscores every 4 bits from right."""
    if len(bin_str) <= 4:
        return bin_str
    parts = []
    for i in range(len(bin_str), 0, -4):
        start = max(0, i - 4)
        parts.append(bin_str[start:i])
    parts.reverse()
    return "_".join(parts)


# ---------------------------------------------------------------------------
# Column Decode — explicit case per mux (matches original style)
# ---------------------------------------------------------------------------

def gen_column_decode(p: dict) -> str:
    mux = p["mux"]
    ay = int(math.log2(mux))
    ayo = 1 << ay  # == mux

    lines = []
    lines.append('// epl_Column_Decode_sub.v')
    lines.append('`include "EPLFFRAM02_spec.vh"')
    lines.append('')
    lines.append('module epl_Column_Decode_sub (')
    lines.append("           input  wire [`ADDR_AY-1:0]  pAc_i,")
    lines.append("           output reg  [`ADDR_AYO-1:0] pAcy_o")
    lines.append('       );')
    lines.append('')
    lines.append('always @(*)')
    lines.append('begin')
    lines.append('    case (pAc_i)')

    for m in range(mux):
        one_hot = 1 << m
        lines.append(f"        {ay}'d{m}:")
        lines.append(f"            pAcy_o = {ayo}'b{one_hot:0{ayo}b};")

    lines.append(f"        default:")
    lines.append(f"            pAcy_o = {ayo}'b{'0' * ayo};")
    lines.append('    endcase')
    lines.append('end')
    lines.append('')
    lines.append('endmodule')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Column Access — explicit case per mux (matches original style)
# ---------------------------------------------------------------------------

def gen_column_access(p: dict) -> str:
    mux = p["mux"]
    tw = p["tword_width"]
    col = tw * mux
    ayo = mux  # one-hot width

    lines = []
    lines.append('// epl_Column_Access_sub.v')
    lines.append('`include "EPLFFRAM02_spec.vh"')
    lines.append('')
    lines.append('module epl_Column_Access_sub (')
    lines.append("           input  wire [`ADDR_AYO-1:0]    pAcy_i,")
    lines.append("           input  wire                    pValide_i,")
    lines.append("           input  wire [`TWORD_WIDTH-1:0] pCodeword_i,")
    lines.append("           output reg  [`COLUMN-1:0]      pWe_o,")
    lines.append("           input  wire                    pClk_i,")
    lines.append("           input  wire                    nRst_i,")
    lines.append("           output  reg [`ADDR_AYO-1:0]    pAcy1_o,")
    lines.append("           output reg  [`COLUMN-1:0]  pDi_o")
    lines.append('       );')
    lines.append('')
    lines.append("reg [`COLUMN-1:0] pWemask_r , pDs_r;")
    lines.append('')
    lines.append('// Column enable mask (case table)')
    lines.append('always @(*)')
    lines.append('begin')
    lines.append("    pWemask_r = {`COLUMN{1'b0}};")
    lines.append("    pDs_r = {`COLUMN{1'b0}};")
    lines.append('    case (pAcy_i)')

    for m in range(mux):
        one_hot = 1 << m
        lines.append(f"        {ayo}'b{one_hot:0{ayo}b}:")
        lines.append("        begin")
        for j in range(tw):
            col_idx = m + j * mux
            lines.append(f"            pWemask_r[{col_idx}] = 1'b1;")
        for j in range(tw):
            col_idx = m + j * mux
            lines.append(f"            pDs_r[{col_idx}] = pCodeword_i[{j}];")
        lines.append("")
        lines.append("        end")
        lines.append("")

    lines.append("        default:")
    lines.append("        begin")
    lines.append("            pWemask_r = {`COLUMN{1'b0}};")
    lines.append("        end")
    lines.append('    endcase')
    lines.append('end')
    lines.append('')
    lines.append('// Registered outputs (pWe_o & pDi_o aligned)')
    lines.append('always @(posedge pClk_i or negedge nRst_i)')
    lines.append('begin')
    lines.append('    if (!nRst_i)')
    lines.append('    begin')
    lines.append("        pWe_o <= {`COLUMN{1'b0}};")
    lines.append("        pDi_o <= {`COLUMN{1'b0}};")
    lines.append('    end')
    lines.append('    else if (pValide_i)')
    lines.append('    begin')
    lines.append('        pWe_o <= pWemask_r;')
    lines.append('        pDi_o <= pDs_r;')
    lines.append('    end')
    lines.append('    else')
    lines.append('    begin')
    lines.append("        pWe_o <= {`COLUMN{1'b0}};")
    lines.append("        pDi_o <={`COLUMN{1'b0}};")
    lines.append('    end')
    lines.append('end')
    lines.append('')
    lines.append('')
    lines.append('always @(posedge pClk_i or negedge nRst_i)')
    lines.append('begin')
    lines.append('    if (!nRst_i)')
    lines.append('    begin')
    lines.append("        pAcy1_o <= {`ADDR_AYO{1'b0}};")
    lines.append('    end')
    lines.append('    else')
    lines.append('    begin')
    lines.append('        pAcy1_o <= pAcy_i;')
    lines.append('    end')
    lines.append('end')
    lines.append('endmodule')
    lines.append('')
    lines.append('')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Read Mux — explicit case per mux (matches original style)
# ---------------------------------------------------------------------------

def gen_read_mux(p: dict) -> str:
    mux = p["mux"]
    tw = p["tword_width"]
    ayo = mux

    lines = []
    lines.append('// epl_Read_Mux_sub.v')
    lines.append('`include "EPLFFRAM02_spec.vh"')
    lines.append('')
    lines.append('module epl_Read_Mux_sub (')
    lines.append("           input  wire [`COLUMN-1:0]      pDto_i,")
    lines.append("           input  wire [`ADDR_AYO-1:0]     pAcy2_i,")
    lines.append("           output reg  [`TWORD_WIDTH-1:0]  pDo_o,")
    lines.append("           output reg                      pRead1_o,")
    lines.append("           input  wire                     pClk_i,")
    lines.append("           input  wire                     nRst_i,")
    lines.append("           input  wire                     pRead01_i")
    lines.append('       );')
    lines.append('')
    lines.append("reg [`TWORD_WIDTH-1:0] pDomux_r;")
    lines.append('')
    lines.append('// Read data mux (case table)')
    lines.append('always @(*)')
    lines.append('begin')
    lines.append("    pDomux_r = {`TWORD_WIDTH{1'b0}};")
    lines.append('')
    lines.append('    case (pAcy2_i)')

    for m in range(mux):
        one_hot = 1 << m
        lines.append(f"        {ayo}'b{one_hot:0{ayo}b}:")
        lines.append("        begin")
        for j in range(tw):
            col_idx = m + j * mux
            lines.append(f"            pDomux_r[{j}] = pDto_i[{col_idx}];")
        lines.append("        end")
        lines.append("")

    lines.append("        default:")
    lines.append("        begin")
    lines.append("            pDomux_r = {`TWORD_WIDTH{1'b0}};")
    lines.append("        end")
    lines.append('    endcase')
    lines.append('end')
    lines.append('')
    lines.append('// Registered outputs (pDo_o & pRead1_o aligned)')
    lines.append('always @(posedge pClk_i or negedge nRst_i)')
    lines.append('begin')
    lines.append('    if (!nRst_i)')
    lines.append('    begin')
    lines.append("        pDo_o    <= {`TWORD_WIDTH{1'b0}};")
    lines.append("        pRead1_o <= 1'b0;")
    lines.append('    end')
    lines.append('    else if (pRead01_i)')
    lines.append('    begin')
    lines.append('        pDo_o    <= pDomux_r;')
    lines.append("        pRead1_o <= 1'b1;")
    lines.append('    end')
    lines.append('    else')
    lines.append('    begin')
    lines.append("        pRead1_o <= 1'b0;")
    lines.append("        pDo_o    <={`TWORD_WIDTH{1'b0}};")
    lines.append('    end')
    lines.append('end')
    lines.append('')
    lines.append('endmodule')
    lines.append('')
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Memory Array — explicit Bit instantiations + explicit case readout
# ---------------------------------------------------------------------------

def gen_memory_array(p: dict) -> str:
    mux = p["mux"]
    tw = p["tword_width"]
    col = tw * mux
    row = p["word"] // mux

    lines = []
    lines.append('// epl_Memory_Array_sub.v')
    lines.append('`include "EPLFFRAM02_spec.vh"')
    lines.append('')
    lines.append('module epl_Memory_Array_sub (')
    lines.append("           input  wire [`COLUMN-1:0]   pWe_i,")
    lines.append("           input  wire [`COLUMN-1:0]   pDi_i,")
    lines.append("           input  wire [`ROW-1:0]      pWl_i,")
    lines.append("           output reg [`COLUMN-1:0]    pDto_o,")
    lines.append("           output reg                  pRead01_o,")
    lines.append("           input  wire                 pClk_i,")
    lines.append("           input  wire                 pRead0_i,")
    lines.append("           input  wire                 nRst_i,")
    lines.append("           input  wire [`ADDR_AYO-1:0]  pAcy1_i,")
    lines.append("           output reg [`ADDR_AYO-1:0]  pAcy2_o")
    lines.append('       );')
    lines.append('')
    lines.append('')
    lines.append("wire   [`TOTAL-1 : 0] pDtoc_w;")
    lines.append('')

    # Explicit Bit instantiations per row
    bit = 0
    for r in range(row):
        lines.append(f"// ==========================")
        lines.append(f"// Row{r} (WL[{r}]) : Bit_{bit} ~ Bit_{bit + col - 1}")
        lines.append(f"// ==========================")
        for c in range(col):
            pad = " " * (1 if bit < 10 else (0 if bit < 100 else 0))
            label = f"Bit_{bit}"
            # Pad label to align
            label_padded = label.ljust(7)
            lines.append(
                f"epl_Ffbit_n_sub {label_padded} "
                f"( .pClk_i(pClk_i), .nRst_i(nRst_i), "
                f".pWec_i(pWl_i[{r}] & pWe_i[{c}]),{' ' if c < 10 else ''} "
                f".pDic_i(pDi_i[{c}]),{' ' if c < 10 else ''} "
                f".pDtoc_o(pDtoc_w[{bit}]) );"
            )
            bit += 1
        lines.append('')

    # Explicit case readout
    lines.append(f"reg [`COLUMN-1:0] pDataout0_r;")
    lines.append("")
    lines.append("always @(*)")
    lines.append("begin")
    lines.append("    pDataout0_r = {`COLUMN{1'b0}};")
    lines.append("")
    lines.append("    case (pWl_i)")

    for r in range(row):
        one_hot = 1 << r
        bin_str = f"{one_hot:0{row}b}"
        formatted = _format_bin_underscored(bin_str)
        base = r * col
        lines.append(f"        {row}'b{formatted}:  // Row {r}: Bit[{base}:{base + col - 1}]")
        lines.append("        begin")
        for c in range(col):
            gidx = base + c
            lines.append(f"            pDataout0_r[{c}]{' ' if c < 10 else ''} = pDtoc_w[{gidx}];")
        lines.append("        end")
        lines.append("")

    lines.append(f"        default:  // Invalid or idle")
    lines.append("        begin")
    lines.append("            pDataout0_r = {`COLUMN{1'b0}};")
    lines.append("        end")
    lines.append("    endcase")
    lines.append("end")
    lines.append("")
    lines.append("")
    lines.append("always @(posedge pClk_i or negedge nRst_i)")
    lines.append("begin")
    lines.append("    if (!nRst_i)")
    lines.append("    begin")
    lines.append("        pDto_o <= {`COLUMN{1'b0}};")
    lines.append("        pRead01_o <= 1'b0;")
    lines.append("    end")
    lines.append("    else if (pRead0_i)")
    lines.append("    begin")
    lines.append("        pDto_o <= pDataout0_r ;")
    lines.append("        pRead01_o <= 1'b1;")
    lines.append("    end")
    lines.append("    else")
    lines.append("    begin")
    lines.append("        pDto_o <= {`COLUMN{1'b0}};")
    lines.append("        pRead01_o <= 1'b0;")
    lines.append("    end")
    lines.append("end")
    lines.append("")
    lines.append("always @(posedge pClk_i or negedge nRst_i)")
    lines.append("begin")
    lines.append("    if (!nRst_i)")
    lines.append("    begin")
    lines.append("        pAcy2_o <= {`ADDR_AYO{1'b0}};")
    lines.append("    end")
    lines.append("    else")
    lines.append("    begin")
    lines.append("        pAcy2_o <= pAcy1_i;")
    lines.append("    end")
    lines.append("end")
    lines.append("")
    lines.append("")
    lines.append("")
    lines.append("")
    lines.append("endmodule")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Top module — parameterized pCcodeword width
# ---------------------------------------------------------------------------

def gen_top(p: dict) -> str:
    tw = p["tword_width"]
    word = p["word"]

    wf_word_hex = fmt_mask_hex(p["wf_word_mask_int"], word)
    wf_bit_bin = fmt_mask_bin(p["wf_bit_mask_int"], tw)
    rd_word_hex = fmt_mask_hex(p["rd_word_mask_int"], word)
    rd_bit_bin = fmt_mask_bin(p["rd_bit_mask_int"], tw)

    return f'''// epl_FFRAM02_top_fi.v
`include "EPLFFRAM02_spec.vh"

//------------------------------------------------------------------------------
// FI configuration (no "parameter" / "localparam" used)
//------------------------------------------------------------------------------
`ifndef FI_WF_WORD_MASK
  `define FI_WF_WORD_MASK {wf_word_hex}
`endif
`ifndef FI_WF_BIT_MASK
  `define FI_WF_BIT_MASK  {wf_bit_bin}
`endif
`ifndef FI_WF_FORCE_ZERO
  `define FI_WF_FORCE_ZERO 1'b0
`endif

`ifndef FI_RD_WORD_MASK
  `define FI_RD_WORD_MASK {rd_word_hex}
`endif
`ifndef FI_RD_BIT_MASK
  `define FI_RD_BIT_MASK  {rd_bit_bin}
`endif

module epl_FFRAM02_top_fi (
           input  wire [`ADDR_WIDTH-1 :0] pA_i,
           input  wire [`FAULT-1:0]       pFS_i,
           input  wire [`WORD_WIDTH-1:0]  pD_i,
           input  wire                    pCLOCK_i,
           input  wire                    nRESET_i,
           input  wire                    nCEN_i,
           input  wire                    nWEN_i,
           output wire [`WORD_WIDTH-1:0]  pQ_o,
           output wire                    pERR_o,
           output wire [`TWORD_WIDTH-1:0] pCcodeword1_o
       );

// -------------------------------------------------------------------------
// Internal signals (follow naming convention: _w for wire, _r for reg)
// -------------------------------------------------------------------------
wire [`ADDR_AX -1 : 0] pAr_w;
wire [`ADDR_AY - 1 : 0] pAc_w;

wire [`WORD_WIDTH-1:0] pData_w , pDfo_w;

wire nCen_w , nWen_w , pWrite_w , pRead_w  , pError_w , pValide_w;
wire pRead1_w , pRead0_w , pRead01_w;

wire [`FAULT-1:0] pFs_w;

wire [`ADDR_AYO - 1 : 0] pAcy_w , pAcy1_w ,  pAcy2_w;
wire [`ADDR_AXO - 1 : 0] pArx_w;

wire [ `COLUMN - 1 : 0] pWe_w , pDto_w , pDi_w;
wire [`TWORD_WIDTH-1 :0] pCodeword_w , pCodewordFi_w;
wire [`TWORD_WIDTH-1:0] pCcodeword_w;
wire [`TWORD_WIDTH-1 :0] pDo_w , pDoFi_w;
wire [ `ROW - 1 : 0] pWl_w;

// FI constant wires (tape-out friendly; no parameters)
wire [`WORD-1:0]        pWfWordMask_w;
wire [`TWORD_WIDTH-1:0] pWfBitMask_w;
wire                   pWfForceZero_w;
wire [`WORD-1:0]        pRdWordMask_w;
wire [`TWORD_WIDTH-1:0] pRdBitMask_w;


assign pWfWordMask_w    = `FI_WF_WORD_MASK;
assign pWfBitMask_w     = `FI_WF_BIT_MASK;
assign pWfForceZero_w   = `FI_WF_FORCE_ZERO;
assign pRdWordMask_w    = `FI_RD_WORD_MASK;
assign pRdBitMask_w     = `FI_RD_BIT_MASK;

// Read FI alignment (latch read-address and FI request at read command)
reg [`ADDR_WIDTH-1:0] pRdAddr_r;
reg                  pRdFiEn_r;


assign pAc_w    = pA_i [`ADDR_AY - 1 : 0];
assign pAr_w    = pA_i [`ADDR_WIDTH  - 1 : `ADDR_AY];
assign pData_w  = pD_i;
assign nCen_w   = nCEN_i;
assign nWen_w   = nWEN_i;
assign pQ_o     = pDfo_w;
assign pERR_o   = pError_w;
assign pCcodeword1_o = pCcodeword_w;
assign pFs_w    = pFS_i;

// Latch read address and FI request for read-disturb mode
always @(posedge pCLOCK_i or negedge nRESET_i)
begin
    if (!nRESET_i)
    begin
        pRdAddr_r <= {{`ADDR_WIDTH{{1'b0}}}};
        pRdFiEn_r <= 1'b0;
    end
    else if (pRead_w)
    begin
        pRdAddr_r <= pA_i;
        pRdFiEn_r <= pFs_w[0];
    end
    else if (pRead1_w)
    begin
        // consume one-shot FI request
        pRdFiEn_r <= 1'b0;
    end
end

// -------------------------------------------------------------------------
// Sub-module instantiation
// -------------------------------------------------------------------------

// Row Decode
epl_Row_Decode_sub RD_s(
                       .pAr_i(pAr_w),
                       .pArx_o(pArx_w)
                   );

// Column Decode
epl_Column_Decode_sub CD_s(
                          .pAc_i(pAc_w),
                          .pAcy_o(pAcy_w)
                      );

// Encoder
epl_ecc_encoder EE(
                    .pDATA_i(pData_w),
                    .pWRITE_i(pWrite_w),
                    .pVALIDE_o(pValide_w),
                    .pCODEWORD_o(pCodeword_w),
                    .pCcodeword_o(pCcodeword_w),
                    .pCLK_i(pCLOCK_i),
                    .nRST_i(nRESET_i)
                );

// ------------------------------------------------------------
// FI-1: Write Failure (after encoder, before Column Access)
// ------------------------------------------------------------
epl_FiWrFail_sub FI_WF_s (
                    .pA_i          (pA_i),
                    .pWRITE_i      (pWrite_w),
                    .pFS_i         (pFs_w),
                    .pFiWordMask_i (pWfWordMask_w),
                    .pFiBitMask_i  (pWfBitMask_w),
                    .pFiForceZero_i(pWfForceZero_w),
                    .pCODEWORD_i   (pCodeword_w),
                    .pCODEWORD_o   (pCodewordFi_w)
                );

// Column Access
epl_Column_Access_sub CA_s(
                          .pAcy_i(pAcy_w),
                          .pValide_i(pValide_w),
                          .pCodeword_i(pCodewordFi_w),
                          .pWe_o(pWe_w),
                          .pClk_i(pCLOCK_i),
                          .nRst_i(nRESET_i),
                          .pAcy1_o(pAcy1_w),
                          .pDi_o(pDi_w)
                      );

// Control Circuit
epl_Control_Circuit_sub CCs(
                            .nWen_i(nWen_w),
                            .nCen_i(nCen_w),
                            .pWrite_o(pWrite_w),
                            .pRead_o(pRead_w)
                        );

// Row Selection
epl_Row_Selection_sub RSs(
                          .pValide_i(pValide_w),
                          .pArx_i(pArx_w),
                          .pRead_i(pRead_w),
                          .pRead0_o(pRead0_w),
                          .pClk_i(pCLOCK_i),
                          .nRst_i(nRESET_i),
                          .pWl_o(pWl_w)
                      );

// Memory Array (pFs_i kept for compatibility; unused inside original array)
epl_Memory_Array_sub MAs(
                         .pWe_i(pWe_w),
                         .pDi_i(pDi_w),
                         .pWl_i(pWl_w),
                         .pDto_o(pDto_w),
                         .pRead0_i(pRead0_w),
                         .pRead01_o(pRead01_w),
                         .pClk_i(pCLOCK_i),
                         .nRst_i(nRESET_i),
                         .pAcy1_i(pAcy1_w),
                         .pAcy2_o(pAcy2_w)
                     );

// Read Mux
epl_Read_Mux_sub RMs(
                     .pDto_i(pDto_w),
                     .pAcy2_i(pAcy2_w),
                     .pDo_o(pDo_w),
                     .pRead1_o(pRead1_w),
                     .pClk_i(pCLOCK_i),
                     .nRst_i(nRESET_i),
                     .pRead01_i(pRead01_w)
                 );

// ------------------------------------------------------------
// FI-2: Read Disturb (after Read Mux, before ECC decoder)
// ------------------------------------------------------------
epl_FiRdDist_sub FI_RD_s (
                    .pA_i          (pRdAddr_r),
                    .pREAD_i       (pRead1_w),
                    .pFIEN_i       (pRdFiEn_r),
                    .pFiWordMask_i (pRdWordMask_w),
                    .pFiBitMask_i  (pRdBitMask_w),
                    .pPARITYDATA_i (pDo_w),
                    .pPARITYDATA_o (pDoFi_w)
                );

// ECC Decoder
epl_ecc_decoder ED(
                    .pPARITYDATA_i(pDoFi_w),
                    .pREAD_i(pRead1_w),
                    .pDATA_o(pDfo_w),
                    .pCLK_i(pCLOCK_i),
                    .nRST_i(nRESET_i),
                    .pERROR_o(pError_w)
                );

endmodule
'''


# ---------------------------------------------------------------------------
# Testbench — parameterized data width and word count
# ---------------------------------------------------------------------------

def gen_testbench(p: dict) -> str:
    ww = p["word_width"]
    tw = p["tword_width"]
    word = p["word"]
    # Generate data mask for init: e.g. 4'hF for 4-bit
    data_hex_width = max(1, math.ceil(ww / 4))
    data_mask = (1 << ww) - 1
    data_mask_str = f"{ww}'h{data_mask:0{data_hex_width}X}"
    # Starting value
    start_val = 0xA & data_mask
    start_val_str = f"{ww}'h{start_val:0{data_hex_width}X}"

    rd_word_hex = fmt_mask_hex(p["rd_word_mask_int"], word)
    wf_word_hex = fmt_mask_hex(p["wf_word_mask_int"], word)

    return f'''// epl_testbench_rtl_fi.v
`timescale 1ns/1ps
`include "EPLFFRAM02_spec.vh"

`ifndef TB_RD_WORD_MASK_CONST
  `define TB_RD_WORD_MASK_CONST {rd_word_hex}
`endif
`ifndef TB_WF_WORD_MASK_CONST
  `define TB_WF_WORD_MASK_CONST {wf_word_hex}
`endif

module epl_testbench_rtl_fi;

//==== TB signals ====//
reg pCLK_r;
reg nRST_r;
reg [`ADDR_WIDTH-1:0] pA_r;
reg [`WORD_WIDTH-1:0] pD_r;
reg nWEN_r;
reg nCEN_r;
reg [`FAULT-1:0] pFS_r;

wire [`WORD_WIDTH-1:0] pQ_w;
wire pERR_w;
wire [`TWORD_WIDTH-1:0] pCcodeword_w;

//==== Expected data ====//
reg [`WORD_WIDTH-1:0] expected_data [`WORD-1:0];
reg [`WORD_WIDTH-1:0] input_data    [`WORD-1:0];
reg [`ADDR_WIDTH-1:0] input_addr    [`WORD-1:0];

integer i;
integer pass_count, fail_count;
integer errpass_count, errfail_count;

wire [`WORD-1:0] TB_RD_WORD_MASK;
wire [`WORD-1:0] TB_WF_WORD_MASK;
assign TB_RD_WORD_MASK = `TB_RD_WORD_MASK_CONST;
assign TB_WF_WORD_MASK = `TB_WF_WORD_MASK_CONST;

epl_FFRAM02_top_fi uut (
                    .pA_i      (pA_r),
                    .pD_i      (pD_r),
                    .nWEN_i    (nWEN_r),
                    .nCEN_i    (nCEN_r),
                    .pCLOCK_i  (pCLK_r),
                    .nRESET_i  (nRST_r),
                    .pFS_i     (pFS_r),
                    .pQ_o      (pQ_w),
                    .pERR_o    (pERR_w),
                    .pCcodeword1_o (pCcodeword_w)
                );

//==== CLK generator ====//
parameter CLK_PERIOD = 20;
initial
begin
    pCLK_r = 0;
    forever #(CLK_PERIOD/2) pCLK_r = ~pCLK_r;
end

//==== Reset (Active-Low) ====//
initial
begin
    nRST_r = 0;
    repeat (3) @(posedge pCLK_r);
    nRST_r = 1;
end

//==== Data init ====//
initial
begin
    for (i = 0; i < `WORD; i = i + 1)
    begin
        input_addr[i]    = i[`ADDR_WIDTH-1:0];
        input_data[i]    = ({start_val_str} + i) & {data_mask_str};
        expected_data[i] = input_data[i];
    end
end

//==== Write task ====//
task write_data;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] data;
    input                   fi_en;
    begin
        @(negedge pCLK_r);
        nCEN_r <= 0;
        nWEN_r <= 0;
        pA_r   <= addr;
        pD_r   <= data;
        pFS_r  <= fi_en;

        @(negedge pCLK_r);
        nCEN_r <= 1;
        nWEN_r <= 1;
        pA_r   <= 0;
        pD_r   <= 0;
        pFS_r  <= 0;

        @(posedge pCLK_r);
        @(posedge pCLK_r);

        $display("[%0t] Write -> Addr: 0x%0h, Data: 0x%0h, FI: %0b", $time, addr, data, fi_en);
    end
endtask

//==== Read task ====//
task read_data;
    input  [`ADDR_WIDTH-1:0] addr;
    input                    fi_en;
    output [`WORD_WIDTH-1:0] val;
    output                   err;
    reg    [`WORD_WIDTH-1:0] temp_val;
    reg                      temp_err;
    begin
        @(negedge pCLK_r);
        nCEN_r <= 0;
        nWEN_r <= 1;
        pA_r   <= addr;
        pD_r   <= 0;
        pFS_r  <= fi_en;

        @(negedge pCLK_r);
        nCEN_r <= 1;
        nWEN_r <= 1;
        pA_r   <= 0;
        pD_r   <= 0;
        pFS_r  <= 0;

        @(posedge pCLK_r);
        @(posedge pCLK_r);
        @(posedge pCLK_r);
        @(posedge pCLK_r);

        temp_val = pQ_w;
        temp_err = pERR_w;

        @(posedge pCLK_r);

        val = temp_val;
        err = temp_err;
    end
endtask

//==== reset task ====
task tb_pulse_reset;
begin
    nRST_r = 0;
    repeat (3) @(posedge pCLK_r);
    nRST_r = 1;         
end
endtask


//==== Checker helpers ====//
task check_no_error;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if ((val === expected_data[addr]) && (err === 1'b0))
        begin
            pass_count = pass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS", $time, addr, expected_data[addr], val, err);
        end
        else
        begin
            fail_count = fail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL", $time, addr, expected_data[addr], val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (no_error) at addr 0x%0h", addr);
`endif
        end
    end
endtask

task check_expect_err_and_correct;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if ((val === expected_data[addr]) && (err === 1'b1))
        begin
            errpass_count = errpass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS (corrected)", $time, addr, expected_data[addr], val, err);
        end
        else
        begin
            errfail_count = errfail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL (corrected)", $time, addr, expected_data[addr], val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (expect_err_and_correct) at addr 0x%0h", addr);
`endif
        end
    end
endtask

task check_expect_err_only;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if (err === 1'b1)
        begin
            errpass_count = errpass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  PASS (error flagged)", $time, addr, val, err);
        end
        else
        begin
            errfail_count = errfail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  FAIL (error flagged)", $time, addr, val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (expect_err_only) at addr 0x%0h", addr);
`endif
        end
    end
endtask


//==== Main flow ====//
reg [`WORD_WIDTH-1:0] rdata;
reg rerr;

initial
begin
    // Init
    pA_r   = 0;
    pD_r   = 0;
    nCEN_r = 1;
    nWEN_r = 1;
    pFS_r  = 0;

    pass_count    = 0;
    fail_count    = 0;
    errpass_count = 0;
    errfail_count = 0;

    @(posedge nRST_r);
    @(posedge pCLK_r);

    $display("\\n====================");
    $display("  FFRAM02 RTL Test (FI)");
    $display("====================\\n");

    // Phase 1: Normal write all
    $display("---- Phase 1: Normal Write All ----");
    for (i = 0; i < `WORD; i = i + 1)
        write_data(input_addr[i], input_data[i], 1'b0);
    $display("");

    // Phase 2: Normal read all (expect no error)
    $display("---- Phase 2: Normal Read All (No Error) ----");
    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b0, rdata, rerr);
        check_no_error(input_addr[i], rdata, rerr);
    end
    $display("");

    // Phase 3: Read Disturb
    $display("---- Phase 3: Read Disturb (Expect Corrected + ERR=1 on masked addrs) ----");
    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b1, rdata, rerr);
        if (TB_RD_WORD_MASK[input_addr[i]])
            check_expect_err_and_correct(input_addr[i], rdata, rerr);
        else
            check_no_error(input_addr[i], rdata, rerr);
    end
    $display("");

    // Phase 4: Write Failure
    tb_pulse_reset();

    $display("---- Phase 4: Write Failure (Expect ERR=1 on masked addrs) ----");
    for (i = 0; i < `WORD; i = i + 1)
        write_data(input_addr[i], input_data[i], 1'b1);

    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b0, rdata, rerr);
        if (TB_WF_WORD_MASK[input_addr[i]])
            check_expect_err_only(input_addr[i], rdata, rerr);
        else
            check_no_error(input_addr[i], rdata, rerr);
    end

    // Summary
    $display("\\n========================================");
    $display("            Test Summary (FI)");
    $display("========================================");
    $display("  Pass (no-error)        : %0d", pass_count);
    $display("  Fail (no-error)        : %0d", fail_count);
    $display("  Pass (expect error)    : %0d", errpass_count);
    $display("  Fail (expect error)    : %0d", errfail_count);
    $display("----------------------------------------");
    if ((fail_count == 0) && (errfail_count == 0))
        $display("  Result                 : ALL PASSED");
    else
        $display("  Result                 : FAILED");
    $display("========================================\\n");

    $finish;
end

//==== Waveform Output ====//
initial
begin
    $dumpfile("epl_ffram02_rtl.vcd");
    $dumpvars(0, epl_testbench_rtl_fi);

`ifdef DUMP_FSDB
  `ifdef RTL_SIMULATION
    $fsdbDumpfile("epl_ffram02_rtl.fsdb");
  `elsif POST_SIMULATION
    $fsdbDumpfile("epl_ffram02_post.fsdb");
  `else
    $fsdbDumpfile("epl_ffram02_default.fsdb");
  `endif
    $fsdbDumpvars(0, epl_testbench_rtl_fi);
`endif
end

`ifdef POST_SIMULATION
initial
begin
    $sdf_annotate("chip_syn.sdf", uut);
end
`endif

endmodule
'''


# ---------------------------------------------------------------------------
# Static files (no parameterization needed)
# ---------------------------------------------------------------------------

STATIC_FILES = {
    'Makefile': '''TB   = epl_testbench_rtl_fi
OUT  = sim.out

SRCS = \\
  epl_testbench_rtl_fi.v \\
  epl_FFRAM02_top_fi.v \\
  epl_Column_Access_sub.v epl_Column_Decode_sub.v epl_Control_Circuit_sub.v \\
  epl_Ffbit_n_sub.v epl_FiRdDist_sub.v epl_FiWrFail_sub.v \\
  epl_Memory_Array_sub.v epl_Read_Mux_sub.v epl_Row_Decode_sub.v epl_Row_Selection_sub.v \\
  epl_ecc_encoder.v epl_ecc_decoder.v


all: run

build:
\tiverilog -g2012 -I . -o $(OUT) $(EPL_DEFS) $(SRCS)

run: build
\tvvp $(OUT)

clean:
\trm -f $(OUT) *.vcd *.fst *.fsdb pattern.avc
''',
    'run.f': '''EPLFFRAM02_spec.vh

epl_testbench_rtl_fi.v

epl_Column_Access_sub.v
epl_Column_Decode_sub.v
epl_Control_Circuit_sub.v
epl_ecc_decoder.v
epl_ecc_encoder.v
epl_Ffbit_n_sub.v
epl_Memory_Array_sub.v
epl_Read_Mux_sub.v
epl_Row_Decode_sub.v
epl_Row_Selection_sub.v

epl_FiWrFail_sub.v
epl_FiRdDist_sub.v

epl_FFRAM02_top_fi.v
''',
    'epl_Control_Circuit_sub.v': '''// epl_Control_Circuit_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Control_Circuit_sub (
           input  wire nWen_i,
           input  wire nCen_i,
           output wire pWrite_o,
           output wire pRead_o
       );

assign pWrite_o = (~nCen_i) & (~nWen_i);
assign pRead_o  = (~nCen_i) & ( nWen_i);

endmodule
''',
    'epl_Ffbit_n_sub.v': """// epl_Ffbit_n_sub.v
module epl_Ffbit_n_sub (
           input  wire                     pClk_i,
           input  wire                     nRst_i,
           input  wire                     pWec_i,
           input  wire                     pDic_i,
           output reg                      pDtoc_o
       );

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
        pDtoc_o <= 1'b0;
    else if (pWec_i)
    begin
        pDtoc_o <= pDic_i;
    end
end

endmodule
""",
    'epl_Row_Selection_sub.v': '''// epl_Row_Selection_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Row_Selection_sub (
           input  wire                    pValide_i,
           input  wire [`ADDR_AXO-1:0]     pArx_i,
           input  wire                    pRead_i,
           input  wire                    pClk_i,
           input  wire                    nRst_i,
           output reg                    pRead0_o,
           output reg  [`ROW-1:0]          pWl_o
       );

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pWl_o <= {`ROW{1\'b0}};
        pRead0_o <= 1\'b0;
    end
    else if (pValide_i)
    begin
        pWl_o <= pArx_i;
        pRead0_o <= 1\'b0;
    end
    else if (pRead_i)
    begin
        pWl_o <= pArx_i;
        pRead0_o <= 1\'b1;
    end
    else
    begin
        pWl_o <= {`ROW{1\'b0}};
        pRead0_o <= 1\'b0;
    end
end

endmodule
''',
    'epl_FiWrFail_sub.v': '''// epl_FiWrFail_sub.v
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

// internal signals
wire pHit_w;
wire pFiEn_w;

// FI-1: Write Failure (after encoder, before Column Access)
assign pHit_w  = pFiWordMask_i[pA_i];
assign pFiEn_w = pWRITE_i & pFS_i[0] & pHit_w;

assign pCODEWORD_o = (pFiEn_w) ?
                     (pFiForceZero_i ? {`TWORD_WIDTH{1\'b0}} : (pCODEWORD_i ^ pFiBitMask_i)) :
                     pCODEWORD_i;

endmodule
''',
    'epl_FiRdDist_sub.v': '''// epl_FiRdDist_sub.v
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

// internal signals
wire pHit_w;
wire pFiEn_w;

// FI-2: Read Disturb (after decoder, before output)
assign pHit_w  = pFiWordMask_i[pA_i];
assign pFiEn_w = pREAD_i & pFIEN_i & pHit_w;

assign pPARITYDATA_o = pFiEn_w ? (pPARITYDATA_i ^ pFiBitMask_i) : pPARITYDATA_i;

endmodule
''',
}


# ---------------------------------------------------------------------------
# Passthrough modules (for when ECC/FI is disabled)
# ---------------------------------------------------------------------------

def ecc_encoder_passthrough(p: dict) -> str:
    ww = p["word_width"]
    tw = p["tword_width"]
    return f"""// epl_ecc_encoder.v (passthrough — ECC disabled)
module epl_ecc_encoder (
           input         pCLK_i,
           input         nRST_i,
           input         pWRITE_i,
           input  [{ww-1}:0]  pDATA_i,
           output [{tw-1}:0] pCODEWORD_o,
           output reg [{tw-1}:0] pCcodeword_o,
           output pVALIDE_o
       );

assign pVALIDE_o = pWRITE_i;
assign pCODEWORD_o = (pWRITE_i) ? pDATA_i : {tw}'b0;

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
        pCcodeword_o <= {tw}'b0;
    else if (pWRITE_i)
        pCcodeword_o <= pDATA_i;
    else
        pCcodeword_o <= {tw}'b0;
end

endmodule
"""


def ecc_decoder_passthrough(p: dict) -> str:
    ww = p["word_width"]
    tw = p["tword_width"]
    return f"""// epl_ecc_decoder.v (passthrough — ECC disabled)
module epl_ecc_decoder (
           input         pCLK_i,
           input         nRST_i,
           input         pREAD_i,
           input  [{tw-1}:0]  pPARITYDATA_i,
           output reg [{ww-1}:0]  pDATA_o,
           output reg    pERROR_o
       );

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
    begin
        pDATA_o  <= {ww}'b0;
        pERROR_o <= 1'b0;
    end
    else if (pREAD_i)
    begin
        pDATA_o  <= pPARITYDATA_i[{ww-1}:0];
        pERROR_o <= 1'b0;
    end
    else
    begin
        pDATA_o  <= {ww}'b0;
        pERROR_o <= 1'b0;
    end
end

endmodule
"""


def fi_wf_passthrough() -> str:
    return '''// epl_FiWrFail_sub.v (passthrough — WF FI disabled)
`include "EPLFFRAM02_spec.vh"

module epl_FiWrFail_sub (
    pA_i, pWRITE_i, pFS_i, pFiWordMask_i, pFiBitMask_i, pFiForceZero_i,
    pCODEWORD_i, pCODEWORD_o
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
'''


def fi_rd_passthrough() -> str:
    return '''// epl_FiRdDist_sub.v (passthrough — RD FI disabled)
`include "EPLFFRAM02_spec.vh"

module epl_FiRdDist_sub (
    pA_i, pREAD_i, pFIEN_i, pFiWordMask_i, pFiBitMask_i,
    pPARITYDATA_i, pPARITYDATA_o
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
'''


# ===========================================================================
# Output compiler
# ===========================================================================

def compile_output(params: dict) -> Path:
    out_root = Path(params["output_root"]).expanduser().resolve()
    out_dir = out_root / params["subfolder"] if params["subfolder"].strip() else out_root
    out_dir.mkdir(parents=True, exist_ok=True)

    # Apply enable switches to masks
    p = dict(params)
    if not p["enable_wf"]:
        p["wf_word_mask_int"] = 0
        p["wf_bit_mask_int"] = 0
    if not p["enable_rd"]:
        p["rd_word_mask_int"] = 0
        p["rd_bit_mask_int"] = 0

    # 1) Static files
    for name, content in STATIC_FILES.items():
        (out_dir / name).write_text(content, encoding="utf-8")

    # 2) Spec header
    (out_dir / "EPLFFRAM02_spec.vh").write_text(gen_spec(p), encoding="utf-8")

    # 3) Parameterized modules (all in original explicit style)
    (out_dir / "epl_Row_Decode_sub.v").write_text(gen_row_decode(p), encoding="utf-8")
    (out_dir / "epl_Column_Decode_sub.v").write_text(gen_column_decode(p), encoding="utf-8")
    (out_dir / "epl_Column_Access_sub.v").write_text(gen_column_access(p), encoding="utf-8")
    (out_dir / "epl_Read_Mux_sub.v").write_text(gen_read_mux(p), encoding="utf-8")
    (out_dir / "epl_Memory_Array_sub.v").write_text(gen_memory_array(p), encoding="utf-8")
    (out_dir / "epl_FFRAM02_top_fi.v").write_text(gen_top(p), encoding="utf-8")
    (out_dir / "epl_testbench_rtl_fi.v").write_text(gen_testbench(p), encoding="utf-8")

    # 4) ECC encoder/decoder
    if p["enable_ecc"]:
        (out_dir / "epl_ecc_encoder.v").write_text(gen_ecc_encoder(p), encoding="utf-8")
        (out_dir / "epl_ecc_decoder.v").write_text(gen_ecc_decoder(p), encoding="utf-8")
    else:
        (out_dir / "epl_ecc_encoder.v").write_text(ecc_encoder_passthrough(p), encoding="utf-8")
        (out_dir / "epl_ecc_decoder.v").write_text(ecc_decoder_passthrough(p), encoding="utf-8")

    # 5) FI modules
    if not p["enable_wf"]:
        (out_dir / "epl_FiWrFail_sub.v").write_text(fi_wf_passthrough(), encoding="utf-8")
    if not p["enable_rd"]:
        (out_dir / "epl_FiRdDist_sub.v").write_text(fi_rd_passthrough(), encoding="utf-8")

    return out_dir


# ===========================================================================
# CLI / GUI
# ===========================================================================

def read_params_from_cli() -> dict:
    print("=== hamming1 Memory Compiler (CLI) ===")
    return build_params(
        word=int(ask("word 數", str(DEFAULTS["word"]))),
        word_width=int(ask("word 寬度", str(DEFAULTS["word_width"]))),
        mux=int(ask("mux 數量", str(DEFAULTS["mux"]))),
        fault=int(ask("FAULT 寬度", str(DEFAULTS["fault"]))),
        wf_word_mask=ask("WF word mask (支援 0x/0b/十進位)", DEFAULTS["wf_word_mask"]),
        rd_word_mask=ask("RD word mask (支援 0x/0b/十進位)", DEFAULTS["rd_word_mask"]),
        wf_bit_mask=ask("WF bit mask (支援 0x/0b/十進位)", DEFAULTS["wf_bit_mask"]),
        rd_bit_mask=ask("RD bit mask (支援 0x/0b/十進位)", DEFAULTS["rd_bit_mask"]),
        enable_ecc=ask_bool("是否啟用 ECC", DEFAULTS["enable_ecc"]),
        enable_wf=ask_bool("是否啟用 WF 故障注入模組", DEFAULTS["enable_wf"]),
        enable_rd=ask_bool("是否啟用 RD 故障注入模組", DEFAULTS["enable_rd"]),
        output_root=ask("輸出根目錄", DEFAULTS["output_root"]),
        subfolder=ask("輸出子資料夾名稱（留空代表不使用）", DEFAULTS["subfolder"]),
    )


def run_gui() -> bool:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        return False

    try:
        root = tk.Tk()
    except Exception:
        return False

    root.title("hamming1 Memory Compiler")

    fields = {}
    bools = {}

    def add_entry(row: int, label: str, key: str, default: str):
        tk.Label(root, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=6, pady=3)
        e = tk.Entry(root, width=48)
        e.insert(0, default)
        e.grid(row=row, column=1, sticky="we", padx=6, pady=3)
        fields[key] = e

    def add_check(row: int, label: str, key: str, default: bool):
        var = tk.BooleanVar(value=default)
        tk.Checkbutton(root, text=label, variable=var).grid(row=row, column=1, sticky="w", padx=6, pady=3)
        bools[key] = var

    add_entry(0, "word（2 的次方）", "word", str(DEFAULTS["word"]))
    add_entry(1, "word_width（1~1024）", "word_width", str(DEFAULTS["word_width"]))
    add_entry(2, "mux（2 的次方）", "mux", str(DEFAULTS["mux"]))
    add_entry(3, "FAULT", "fault", str(DEFAULTS["fault"]))
    add_entry(4, "WF word mask", "wf_word_mask", DEFAULTS["wf_word_mask"])
    add_entry(5, "RD word mask", "rd_word_mask", DEFAULTS["rd_word_mask"])
    add_entry(6, "WF bit mask", "wf_bit_mask", DEFAULTS["wf_bit_mask"])
    add_entry(7, "RD bit mask", "rd_bit_mask", DEFAULTS["rd_bit_mask"])
    add_entry(8, "輸出根目錄", "output_root", DEFAULTS["output_root"])
    add_entry(9, "輸出子資料夾", "subfolder", DEFAULTS["subfolder"])

    add_check(10, "啟用 ECC", "enable_ecc", DEFAULTS["enable_ecc"])
    add_check(11, "啟用 WF 故障注入", "enable_wf", DEFAULTS["enable_wf"])
    add_check(12, "啟用 RD 故障注入", "enable_rd", DEFAULTS["enable_rd"])

    capacity_var = tk.StringVar(value="總容量：-")
    tk.Label(root, textvariable=capacity_var, fg="#1f5aa6").grid(row=13, column=0, columnspan=2, sticky="w", padx=6, pady=6)

    status_var = tk.StringVar(value="")
    tk.Label(root, textvariable=status_var, fg="#2f7d32").grid(row=14, column=0, columnspan=2, sticky="w", padx=6, pady=3)

    def collect_params() -> dict:
        return build_params(
            word=int(fields["word"].get().strip()),
            word_width=int(fields["word_width"].get().strip()),
            mux=int(fields["mux"].get().strip()),
            fault=int(fields["fault"].get().strip()),
            wf_word_mask=fields["wf_word_mask"].get().strip(),
            rd_word_mask=fields["rd_word_mask"].get().strip(),
            wf_bit_mask=fields["wf_bit_mask"].get().strip(),
            rd_bit_mask=fields["rd_bit_mask"].get().strip(),
            enable_ecc=bools["enable_ecc"].get(),
            enable_wf=bools["enable_wf"].get(),
            enable_rd=bools["enable_rd"].get(),
            output_root=fields["output_root"].get().strip(),
            subfolder=fields["subfolder"].get().strip(),
        )

    def refresh_capacity(*_):
        try:
            cp = collect_params()
            capacity_var.set(f"總容量：{human_readable_bytes(cp['capacity_bytes'])}")
            status_var.set("")
        except Exception as exc:
            capacity_var.set("總容量：-")
            status_var.set(f"參數尚未有效：{exc}")

    def do_compile():
        try:
            cp = collect_params()
            out_dir = compile_output(cp)
            msg = f"完成輸出：{out_dir}\n總容量：{human_readable_bytes(cp['capacity_bytes'])}"
            if cp["enable_ecc"]:
                msg += f"\nECC：Hamming (m={cp['word_width']}, r={cp['ecc_width']}, n={cp['tword_width']})"
            status_var.set(f"完成：{out_dir}")
            messagebox.showinfo("Memory Compiler", msg)
        except Exception as exc:
            status_var.set(f"失敗：{exc}")
            messagebox.showerror("Memory Compiler", str(exc))

    for e in fields.values():
        e.bind("<KeyRelease>", refresh_capacity)
    for var in bools.values():
        var.trace_add("write", refresh_capacity)

    tk.Button(root, text="更新容量", command=refresh_capacity).grid(row=15, column=0, sticky="w", padx=6, pady=8)
    tk.Button(root, text="生成", command=do_compile, bg="#1f5aa6", fg="white").grid(row=15, column=1, sticky="e", padx=6, pady=8)

    root.columnconfigure(1, weight=1)
    refresh_capacity()
    root.mainloop()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="hamming1 memory compiler")
    parser.add_argument("--cli", action="store_true", help="強制使用 CLI")
    parser.add_argument("--gui", action="store_true", help="強制使用 GUI")
    args = parser.parse_args()

    try:
        gui_used = False
        if not args.cli:
            gui_used = run_gui()
            if args.gui and not gui_used:
                raise RuntimeError("無法啟動 GUI")

        if gui_used:
            return

        params = read_params_from_cli()
        out_dir = compile_output(params)

        print("\n[完成] 已輸出到:", out_dir)
        print(f"- WORD={params['word']}, WORD_WIDTH={params['word_width']}, MUX={params['mux']}, FAULT={params['fault']}")
        print(f"- ECC={'ON' if params['enable_ecc'] else 'OFF'}, WF={'ON' if params['enable_wf'] else 'OFF'}, RD={'ON' if params['enable_rd'] else 'OFF'}")
        print(f"- 總容量：{human_readable_bytes(params['capacity_bytes'])}")

    except Exception as exc:
        print(f"[失敗] {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
