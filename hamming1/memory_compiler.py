#!/usr/bin/env python3
"""
單檔 Memory Compiler (hamming1)
- 盡量重用 hamming1 現有檔案
- 提供 Tkinter GUI（可直接打字）
- 保留 CLI fallback（互動式問答）
"""

from __future__ import annotations

import argparse
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
    print("=== hamming1 Memory Compiler (CLI) ===")
    print("提示：已支援 GUI，若在無圖形環境會自動 fallback 到 CLI。")

    params = build_params(
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

    if params["enable_ecc"] and params["word_width"] != 4:
        print("[警告] 現有 ECC RTL 是針對 4-bit data；已保留原寫法，非 4-bit 可能需自行擴充 ECC 模組。")
    print(f"[容量] 總容量：{human_readable_bytes(params['capacity_bytes'])}")
    return params


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
            p = collect_params()
            capacity_var.set(f"總容量：{human_readable_bytes(p['capacity_bytes'])}")
            status_var.set("")
        except Exception as exc:
            capacity_var.set("總容量：-")
            status_var.set(f"參數尚未有效：{exc}")

    def do_compile():
        try:
            p = collect_params()
            out_dir = compile_output(p)
            msg = f"完成輸出：{out_dir}\n總容量：{human_readable_bytes(p['capacity_bytes'])}"
            if p["enable_ecc"] and p["word_width"] != 4:
                msg += "\n注意：ECC RTL 原本針對 4-bit。"
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
                raise RuntimeError("無法啟動 GUI（可能無 DISPLAY 或缺少 tkinter）")

        if gui_used:
            return

        params = read_params_from_cli()
        out_dir = compile_output(params)

        print("\n[完成] 已輸出到:", out_dir)
        print("主要設定：")
        print(f"- WORD={params['word']}, WORD_WIDTH={params['word_width']}, MUX={params['mux']}, FAULT={params['fault']}")
        print(f"- ECC={'ON' if params['enable_ecc'] else 'OFF'}, WF={'ON' if params['enable_wf'] else 'OFF'}, RD={'ON' if params['enable_rd'] else 'OFF'}")
        print(f"- WF word mask={fmt_mask_hex(params['wf_word_mask_int'], params['word'])}")
        print(f"- RD word mask={fmt_mask_hex(params['rd_word_mask_int'], params['word'])}")
        print(f"- WF bit mask={fmt_mask_bin(params['wf_bit_mask_int'], params['tword_width'])}")
        print(f"- RD bit mask={fmt_mask_bin(params['rd_bit_mask_int'], params['tword_width'])}")
        print(f"- 總容量：{human_readable_bytes(params['capacity_bytes'])}")

    except Exception as exc:
        print(f"[失敗] {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
