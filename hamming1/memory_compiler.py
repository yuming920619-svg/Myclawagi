#!/usr/bin/env python3
"""
單檔 Memory Compiler (hamming1)
- 完全自包含：不依賴外部 .v/.vh 模板檔
- 提供 Tkinter GUI（可直接打字）
- 保留 CLI fallback（互動式問答）
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_CONTENTS = {
    'Makefile': 'TB   = epl_testbench_rtl_fi\nOUT  = sim.out\n\nSRCS = \\\n  epl_testbench_rtl_fi.v \\\n  epl_FFRAM02_top_fi.v \\\n  epl_Column_Access_sub.v epl_Column_Decode_sub.v epl_Control_Circuit_sub.v \\\n  epl_Ffbit_n_sub.v epl_FiRdDist_sub.v epl_FiWrFail_sub.v \\\n  epl_Memory_Array_sub.v epl_Read_Mux_sub.v epl_Row_Decode_sub.v epl_Row_Selection_sub.v \\\n  epl_ecc_encoder.v epl_ecc_decoder.v\n\n\nall: run\n\nbuild:\n\tiverilog -g2012 -I . -o $(OUT) $(EPL_DEFS) $(SRCS)\n\nrun: build\n\tvvp $(OUT)\n\nclean:\n\trm -f $(OUT) *.vcd *.fst *.fsdb pattern.avc\n',
    'run.f': 'EPLFFRAM02_spec.vh\n\nepl_testbench_rtl_fi.v\n\nepl_Column_Access_sub.v\nepl_Column_Decode_sub.v\nepl_Control_Circuit_sub.v\nepl_ecc_decoder.v\nepl_ecc_encoder.v\nepl_Ffbit_n_sub.v\nepl_Memory_Array_sub.v\nepl_Read_Mux_sub.v\nepl_Row_Decode_sub.v\nepl_Row_Selection_sub.v\n\nepl_FiWrFail_sub.v\nepl_FiRdDist_sub.v\n\nepl_FFRAM02_top_fi.v\n',
    'epl_Column_Access_sub.v': '// epl_Column_Access_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Column_Access_sub (\n           input  wire [`ADDR_AYO-1:0]    pAcy_i,\n           input  wire                    pValide_i,\n           input  wire [`TWORD_WIDTH-1:0] pCodeword_i,\n           output reg  [`COLUMN-1:0]      pWe_o,\n           input  wire                    pClk_i,\n           input  wire                    nRst_i,\n           output  reg [`ADDR_AYO-1:0]    pAcy1_o,\n           output reg  [`COLUMN-1:0]  pDi_o\n       );\n\nreg [`COLUMN-1:0] pWemask_r , pDs_r;\n\n// ------------------------------------------------------------\n// Column enable mask (case table; Python-friendly)\n// pAcy_i is assumed one-hot. Invalid values -> all-0.\n// ------------------------------------------------------------\nalways @(*)\nbegin\n    pWemask_r = {`COLUMN{1\'b0}};\n    pDs_r = {`COLUMN{1\'b0}};\n    case (pAcy_i)\n        // MUX = 2 (one-hot)\n        2\'b01:\n        begin\n            // even columns\n            pWemask_r[0]  = 1\'b1;\n            pWemask_r[2]  = 1\'b1;\n            pWemask_r[4]  = 1\'b1;\n            pWemask_r[6]  = 1\'b1;\n            pWemask_r[8]  = 1\'b1;\n            pWemask_r[10] = 1\'b1;\n            pWemask_r[12] = 1\'b1;\n            pDs_r[0] = pCodeword_i[0];\n            pDs_r[2] = pCodeword_i[1];\n            pDs_r[4] = pCodeword_i[2];\n            pDs_r[6] = pCodeword_i[3];\n            pDs_r[8] = pCodeword_i[4];\n            pDs_r[10] = pCodeword_i[5];\n            pDs_r[12] = pCodeword_i[6];\n\n        end\n\n        2\'b10:\n        begin\n            // odd columns\n            pWemask_r[1]  = 1\'b1;\n            pWemask_r[3]  = 1\'b1;\n            pWemask_r[5]  = 1\'b1;\n            pWemask_r[7]  = 1\'b1;\n            pWemask_r[9]  = 1\'b1;\n            pWemask_r[11] = 1\'b1;\n            pWemask_r[13] = 1\'b1;\n            pDs_r[1] = pCodeword_i[0];\n            pDs_r[3] = pCodeword_i[1];\n            pDs_r[5] = pCodeword_i[2];\n            pDs_r[7] = pCodeword_i[3];\n            pDs_r[9] = pCodeword_i[4];\n            pDs_r[11] = pCodeword_i[5];\n            pDs_r[13] = pCodeword_i[6];\n\n        end\n\n        default:\n        begin\n            pWemask_r = {`COLUMN{1\'b0}};\n        end\n    endcase\nend\n\n// ------------------------------------------------------------\n// Registered outputs (pWe_o & pDi_o aligned)\n// ------------------------------------------------------------\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pWe_o <= {`COLUMN{1\'b0}};\n        pDi_o <= {`COLUMN{1\'b0}};\n    end\n    else if (pValide_i)\n    begin\n        pWe_o <= pWemask_r;\n        pDi_o <= pDs_r;\n    end\n    else\n    begin\n        pWe_o <= {`COLUMN{1\'b0}};\n        pDi_o <={`COLUMN{1\'b0}};\n    end\nend\n\n\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pAcy1_o <= {`ADDR_AYO{1\'b0}};\n    end\n    else\n    begin\n        pAcy1_o <= pAcy_i;\n    end\nend\nendmodule\n\n\n',
    'epl_Column_Decode_sub.v': '// epl_Column_Decode_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Column_Decode_sub (\n           input  wire [`ADDR_AY-1:0]  pAc_i,\n           output reg  [`ADDR_AYO-1:0] pAcy_o\n       );\n\nalways @(*)\nbegin\n    case (pAc_i)\n        1\'d0:\n            pAcy_o = 2\'b01;\n        1\'d1:\n            pAcy_o = 2\'b10;\n        default:\n            pAcy_o = 2\'b00;\n    endcase\nend\n\nendmodule\n',
    'epl_Control_Circuit_sub.v': '// epl_Control_Circuit_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Control_Circuit_sub (\n           input  wire nWen_i,\n           input  wire nCen_i,\n           output wire pWrite_o,\n           output wire pRead_o\n       );\n\nassign pWrite_o = (~nCen_i) & (~nWen_i);\nassign pRead_o  = (~nCen_i) & ( nWen_i);\n\nendmodule\n',
    'epl_FFRAM02_top_fi.v': '// epl_FFRAM02_top_fi.v\n`include "EPLFFRAM02_spec.vh"\n\n//------------------------------------------------------------------------------\n// FI configuration (no "parameter" / "localparam" used)\n// - You can override these by compiler option, e.g.\n//     +define+FI_WF_WORD_MASK=16\'h0030\n//------------------------------------------------------------------------------\n`ifndef FI_WF_WORD_MASK\n  `define FI_WF_WORD_MASK 16\'h0030\n`endif\n`ifndef FI_WF_BIT_MASK\n  `define FI_WF_BIT_MASK  7\'b0000001\n`endif\n`ifndef FI_WF_FORCE_ZERO\n  `define FI_WF_FORCE_ZERO 1\'b1\n`endif\n\n`ifndef FI_RD_WORD_MASK\n  `define FI_RD_WORD_MASK 16\'h000C\n`endif\n`ifndef FI_RD_BIT_MASK\n  `define FI_RD_BIT_MASK  7\'b0000001\n`endif\n\nmodule epl_FFRAM02_top_fi (\n           input  wire [`ADDR_WIDTH-1 :0] pA_i,\n           input  wire [`FAULT-1:0]       pFS_i,\n           input  wire [`WORD_WIDTH-1:0]  pD_i,\n           input  wire                    pCLOCK_i,\n           input  wire                    nRESET_i,\n           input  wire                    nCEN_i,\n           input  wire                    nWEN_i,\n           output wire [`WORD_WIDTH-1:0]  pQ_o,\n           output wire                    pERR_o,\n           output wire [6:0]              pCcodeword1_o\n       );\n\n// -------------------------------------------------------------------------\n// Internal signals (follow naming convention: _w for wire, _r for reg)\n// -------------------------------------------------------------------------\nwire [`ADDR_AX -1 : 0] pAr_w;\nwire [`ADDR_AY - 1 : 0] pAc_w;\n\nwire [`WORD_WIDTH-1:0] pData_w , pDfo_w;\n\nwire nCen_w , nWen_w , pWrite_w , pRead_w  , pError_w , pValide_w;\nwire pRead1_w , pRead0_w , pRead01_w;\n\nwire [`FAULT-1:0] pFs_w;\n\nwire [`ADDR_AYO - 1 : 0] pAcy_w , pAcy1_w ,  pAcy2_w;\nwire [`ADDR_AXO - 1 : 0] pArx_w;\n\nwire [ `COLUMN - 1 : 0] pWe_w , pDto_w , pDi_w;\nwire [`TWORD_WIDTH-1 :0] pCodeword_w , pCodewordFi_w;\nwire [6:0] pCcodeword_w;\nwire [`TWORD_WIDTH-1 :0] pDo_w , pDoFi_w;\nwire [ `ROW - 1 : 0] pWl_w;\n\n// FI constant wires (tape-out friendly; no parameters)\nwire [`WORD-1:0]        pWfWordMask_w;\nwire [`TWORD_WIDTH-1:0] pWfBitMask_w;\nwire                   pWfForceZero_w;\nwire [`WORD-1:0]        pRdWordMask_w;\nwire [`TWORD_WIDTH-1:0] pRdBitMask_w;\n\n\nassign pWfWordMask_w    = `FI_WF_WORD_MASK;\nassign pWfBitMask_w     = `FI_WF_BIT_MASK;\nassign pWfForceZero_w   = `FI_WF_FORCE_ZERO;\nassign pRdWordMask_w    = `FI_RD_WORD_MASK;\nassign pRdBitMask_w     = `FI_RD_BIT_MASK;\n\n// Read FI alignment (latch read-address and FI request at read command)\nreg [`ADDR_WIDTH-1:0] pRdAddr_r;\nreg                  pRdFiEn_r;\n\n\nassign pAc_w    = pA_i [`ADDR_AY - 1 : 0];\nassign pAr_w    = pA_i [`ADDR_WIDTH  - 1 : `ADDR_AY];\nassign pData_w  = pD_i;\nassign nCen_w   = nCEN_i;\nassign nWen_w   = nWEN_i;\nassign pQ_o     = pDfo_w;\nassign pERR_o   = pError_w;\nassign pCcodeword1_o = pCcodeword_w [6:0];\nassign pFs_w    = pFS_i;\n\n// Latch read address and FI request for read-disturb mode\nalways @(posedge pCLOCK_i or negedge nRESET_i)\nbegin\n    if (!nRESET_i)\n    begin\n        pRdAddr_r <= {`ADDR_WIDTH{1\'b0}};\n        pRdFiEn_r <= 1\'b0;\n    end\n    else if (pRead_w)\n    begin\n        pRdAddr_r <= pA_i;\n        pRdFiEn_r <= pFs_w[0];\n    end\n    else if (pRead1_w)\n    begin\n        // consume one-shot FI request\n        pRdFiEn_r <= 1\'b0;\n    end\nend\n\n// -------------------------------------------------------------------------\n// Sub-module instantiation\n// -------------------------------------------------------------------------\n\n// Row Decode\nepl_Row_Decode_sub RD_s(\n                       .pAr_i(pAr_w),\n                       .pArx_o(pArx_w)\n                   );\n\n// Column Decode\nepl_Column_Decode_sub CD_s(\n                          .pAc_i(pAc_w),\n                          .pAcy_o(pAcy_w)\n                      );\n\n// Encoder\nepl_ecc_encoder EE(\n                    .pDATA_i(pData_w),\n                    .pWRITE_i(pWrite_w),\n                    .pVALIDE_o(pValide_w),\n                    .pCODEWORD_o(pCodeword_w),\n                    .pCcodeword_o(pCcodeword_w),\n                    .pCLK_i(pCLOCK_i),\n                    .nRST_i(nRESET_i)\n                );\n\n// ------------------------------------------------------------\n// FI-1: Write Failure (after encoder, before Column Access)\n// ------------------------------------------------------------\nepl_FiWrFail_sub FI_WF_s (\n                    .pA_i          (pA_i),\n                    .pWRITE_i      (pWrite_w),\n                    .pFS_i         (pFs_w),\n                    .pFiWordMask_i (pWfWordMask_w),\n                    .pFiBitMask_i  (pWfBitMask_w),\n                    .pFiForceZero_i(pWfForceZero_w),\n                    .pCODEWORD_i   (pCodeword_w),\n                    .pCODEWORD_o   (pCodewordFi_w)\n                );\n\n// Column Access\nepl_Column_Access_sub CA_s(\n                          .pAcy_i(pAcy_w),\n                          .pValide_i(pValide_w),\n                          .pCodeword_i(pCodewordFi_w),\n                          .pWe_o(pWe_w),\n                          .pClk_i(pCLOCK_i),\n                          .nRst_i(nRESET_i),\n                          .pAcy1_o(pAcy1_w),\n                          .pDi_o(pDi_w)\n                      );\n\n// Control Circuit\nepl_Control_Circuit_sub CCs(\n                            .nWen_i(nWen_w),\n                            .nCen_i(nCen_w),\n                            .pWrite_o(pWrite_w),\n                            .pRead_o(pRead_w)\n                        );\n\n// Row Selection\nepl_Row_Selection_sub RSs(\n                          .pValide_i(pValide_w),\n                          .pArx_i(pArx_w),\n                          .pRead_i(pRead_w),\n                          .pRead0_o(pRead0_w),\n                          .pClk_i(pCLOCK_i),\n                          .nRst_i(nRESET_i),\n                          .pWl_o(pWl_w)\n                      );\n\n// Memory Array (pFs_i kept for compatibility; unused inside original array)\nepl_Memory_Array_sub MAs(\n                         .pWe_i(pWe_w),\n                         .pDi_i(pDi_w),\n                         .pWl_i(pWl_w),\n                         .pDto_o(pDto_w),\n                         .pRead0_i(pRead0_w),\n                         .pRead01_o(pRead01_w),\n                         .pClk_i(pCLOCK_i),\n                         .nRst_i(nRESET_i),\n                         .pAcy1_i(pAcy1_w),\n                         .pAcy2_o(pAcy2_w)\n                     );\n\n// Read Mux\nepl_Read_Mux_sub RMs(\n                     .pDto_i(pDto_w),\n                     .pAcy2_i(pAcy2_w),\n                     .pDo_o(pDo_w),\n                     .pRead1_o(pRead1_w),\n                     .pClk_i(pCLOCK_i),\n                     .nRst_i(nRESET_i),\n                     .pRead01_i(pRead01_w)\n                 );\n\n// ------------------------------------------------------------\n// FI-2: Read Disturb (after Read Mux, before ECC decoder)\n// ------------------------------------------------------------\nepl_FiRdDist_sub FI_RD_s (\n                    .pA_i          (pRdAddr_r),\n                    .pREAD_i       (pRead1_w),\n                    .pFIEN_i       (pRdFiEn_r),\n                    .pFiWordMask_i (pRdWordMask_w),\n                    .pFiBitMask_i  (pRdBitMask_w),\n                    .pPARITYDATA_i (pDo_w),\n                    .pPARITYDATA_o (pDoFi_w)\n                );\n\n// ECC Decoder\nepl_ecc_decoder ED(\n                    .pPARITYDATA_i(pDoFi_w),\n                    .pREAD_i(pRead1_w),\n                    .pDATA_o(pDfo_w),\n                    .pCLK_i(pCLOCK_i),\n                    .nRST_i(nRESET_i),\n                    .pERROR_o(pError_w)\n                );\n\nendmodule\n',
    'epl_Ffbit_n_sub.v': "// epl_Ffbit_n_sub.v\nmodule epl_Ffbit_n_sub (\n           input  wire                     pClk_i,\n           input  wire                     nRst_i,\n           input  wire                     pWec_i,\n           input  wire                     pDic_i,\n           output reg                      pDtoc_o\n       );\n\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n        pDtoc_o <= 1'b0;\n    else if (pWec_i)\n    begin\n        pDtoc_o <= pDic_i;\n    end\nend\n\nendmodule\n",
    'epl_FiRdDist_sub.v': '// epl_FiRdDist_sub.v\n`include "EPLFFRAM02_spec.vh"\n\n//------------------------------------------------------------------------------\n// epl_FiRdDist_sub\n//   Read-Disturb FI injection (synthesizable, combinational)\n//------------------------------------------------------------------------------\nmodule epl_FiRdDist_sub (\n    pA_i,\n    pREAD_i,\n    pFIEN_i,\n    pFiWordMask_i,\n    pFiBitMask_i,\n    pPARITYDATA_i,\n    pPARITYDATA_o\n);\n\ninput  [`ADDR_WIDTH-1:0]  pA_i;\ninput                     pREAD_i;\ninput                     pFIEN_i;\ninput  [`WORD-1:0]        pFiWordMask_i;\ninput  [`TWORD_WIDTH-1:0] pFiBitMask_i;\ninput  [`TWORD_WIDTH-1:0] pPARITYDATA_i;\noutput [`TWORD_WIDTH-1:0] pPARITYDATA_o;\n\n// internal signals\nwire pHit_w;\nwire pFiEn_w;\n\n// FI-2: Read Disturb (after decoder, before output)\nassign pHit_w  = pFiWordMask_i[pA_i];\nassign pFiEn_w = pREAD_i & pFIEN_i & pHit_w;\n\nassign pPARITYDATA_o = pFiEn_w ? (pPARITYDATA_i ^ pFiBitMask_i) : pPARITYDATA_i;\n\nendmodule\n',
    'epl_FiWrFail_sub.v': '// epl_FiWrFail_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_FiWrFail_sub (\n    pA_i,\n    pWRITE_i,\n    pFS_i,\n    pFiWordMask_i,\n    pFiBitMask_i,\n    pFiForceZero_i,\n    pCODEWORD_i,\n    pCODEWORD_o\n);\n\ninput  [`ADDR_WIDTH-1:0]  pA_i;\ninput                     pWRITE_i;\ninput  [`FAULT-1:0]       pFS_i;\ninput  [`WORD-1:0]        pFiWordMask_i;\ninput  [`TWORD_WIDTH-1:0] pFiBitMask_i;\ninput                     pFiForceZero_i;\ninput  [`TWORD_WIDTH-1:0] pCODEWORD_i;\noutput [`TWORD_WIDTH-1:0] pCODEWORD_o;\n\n// internal signals\nwire pHit_w;\nwire pFiEn_w;\n\n// FI-1: Write Failure (after encoder, before Column Access)\n// This module simulates a write failure by either forcing the codeword to zero or flipping bits\nassign pHit_w  = pFiWordMask_i[pA_i];\nassign pFiEn_w = pWRITE_i & pFS_i[0] & pHit_w;\n\nassign pCODEWORD_o = (pFiEn_w) ?\n                     (pFiForceZero_i ? {`TWORD_WIDTH{1\'b0}} : (pCODEWORD_i ^ pFiBitMask_i)) :\n                     pCODEWORD_i;\n\nendmodule\n',
    'epl_Memory_Array_sub.v': '// epl_Memory_Array_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Memory_Array_sub (\n           input  wire [`COLUMN-1:0]   pWe_i,\n           input  wire [`COLUMN-1:0]   pDi_i,\n           input  wire [`ROW-1:0]      pWl_i,\n           output reg [`COLUMN-1:0]    pDto_o,\n           output reg                  pRead01_o,\n           input  wire                 pClk_i,\n           input  wire                 pRead0_i,\n           input  wire                 nRst_i,\n           input  wire [`ADDR_AYO-1:0]  pAcy1_i,\n           output reg [`ADDR_AYO-1:0]  pAcy2_o\n       );\n\n\nwire   [`TOTAL-1 : 0] pDtoc_w;\n\n// ==========================\n// Row0 (WL[0]) : Bit_0 ~ Bit_13\n// ==========================\nepl_Ffbit_n_sub Bit_0   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[0])  );\nepl_Ffbit_n_sub Bit_1   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[1])  );\nepl_Ffbit_n_sub Bit_2   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[2])  );\nepl_Ffbit_n_sub Bit_3   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[3])  );\nepl_Ffbit_n_sub Bit_4   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[4])  );\nepl_Ffbit_n_sub Bit_5   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[5])  );\nepl_Ffbit_n_sub Bit_6   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[6])  );\nepl_Ffbit_n_sub Bit_7   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[7])  );\nepl_Ffbit_n_sub Bit_8   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[8])  );\nepl_Ffbit_n_sub Bit_9   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[9])  );\nepl_Ffbit_n_sub Bit_10  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[10]) );\nepl_Ffbit_n_sub Bit_11  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[11]) );\nepl_Ffbit_n_sub Bit_12  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[12]) );\nepl_Ffbit_n_sub Bit_13  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[13]) );\n\n// ==========================\n// Row1 (WL[1]) : Bit_14 ~ Bit_27\n// ==========================\nepl_Ffbit_n_sub Bit_14  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[14]) );\nepl_Ffbit_n_sub Bit_15  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[15]) );\nepl_Ffbit_n_sub Bit_16  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[16]) );\nepl_Ffbit_n_sub Bit_17  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[17]) );\nepl_Ffbit_n_sub Bit_18  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[18]) );\nepl_Ffbit_n_sub Bit_19  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[19]) );\nepl_Ffbit_n_sub Bit_20  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[20]) );\nepl_Ffbit_n_sub Bit_21  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[21]) );\nepl_Ffbit_n_sub Bit_22  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[22]) );\nepl_Ffbit_n_sub Bit_23  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[23]) );\nepl_Ffbit_n_sub Bit_24  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[24]) );\nepl_Ffbit_n_sub Bit_25  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[25]) );\nepl_Ffbit_n_sub Bit_26  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[26]) );\nepl_Ffbit_n_sub Bit_27  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[27]) );\n\n// ==========================\n// Row2 (WL[2]) : Bit_28 ~ Bit_41\n// ==========================\nepl_Ffbit_n_sub Bit_28  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[28]) );\nepl_Ffbit_n_sub Bit_29  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[29]) );\nepl_Ffbit_n_sub Bit_30  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[30]) );\nepl_Ffbit_n_sub Bit_31  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[31]) );\nepl_Ffbit_n_sub Bit_32  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[32]) );\nepl_Ffbit_n_sub Bit_33  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[33]) );\nepl_Ffbit_n_sub Bit_34  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[34]) );\nepl_Ffbit_n_sub Bit_35  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[35]) );\nepl_Ffbit_n_sub Bit_36  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[36]) );\nepl_Ffbit_n_sub Bit_37  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[37]) );\nepl_Ffbit_n_sub Bit_38  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[38]) );\nepl_Ffbit_n_sub Bit_39  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[39]) );\nepl_Ffbit_n_sub Bit_40  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[40]) );\nepl_Ffbit_n_sub Bit_41  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[41]) );\n\n// ==========================\n// Row3 (WL[3]) : Bit_42 ~ Bit_55\n// ==========================\nepl_Ffbit_n_sub Bit_42  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[42]) );\nepl_Ffbit_n_sub Bit_43  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[43]) );\nepl_Ffbit_n_sub Bit_44  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[44]) );\nepl_Ffbit_n_sub Bit_45  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[45]) );\nepl_Ffbit_n_sub Bit_46  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[46]) );\nepl_Ffbit_n_sub Bit_47  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[47]) );\nepl_Ffbit_n_sub Bit_48  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[48]) );\nepl_Ffbit_n_sub Bit_49  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[49]) );\nepl_Ffbit_n_sub Bit_50  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[50]) );\nepl_Ffbit_n_sub Bit_51  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[51]) );\nepl_Ffbit_n_sub Bit_52  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[52]) );\nepl_Ffbit_n_sub Bit_53  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[53]) );\nepl_Ffbit_n_sub Bit_54  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[54]) );\nepl_Ffbit_n_sub Bit_55  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[55]) );\n\n// ==========================\n// Row4 (WL[4]) : Bit_56 ~ Bit_69\n// ==========================\nepl_Ffbit_n_sub Bit_56  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[56]) );\nepl_Ffbit_n_sub Bit_57  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[57]) );\nepl_Ffbit_n_sub Bit_58  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[58]) );\nepl_Ffbit_n_sub Bit_59  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[59]) );\nepl_Ffbit_n_sub Bit_60  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[60]) );\nepl_Ffbit_n_sub Bit_61  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[61]) );\nepl_Ffbit_n_sub Bit_62  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[62]) );\nepl_Ffbit_n_sub Bit_63  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[63]) );\nepl_Ffbit_n_sub Bit_64  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[64]) );\nepl_Ffbit_n_sub Bit_65  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[65]) );\nepl_Ffbit_n_sub Bit_66  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[66]) );\nepl_Ffbit_n_sub Bit_67  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[67]) );\nepl_Ffbit_n_sub Bit_68  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[68]) );\nepl_Ffbit_n_sub Bit_69  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[69]) );\n\n// ==========================\n// Row5 (WL[5]) : Bit_70 ~ Bit_83\n// ==========================\nepl_Ffbit_n_sub Bit_70  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[70]) );\nepl_Ffbit_n_sub Bit_71  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[71]) );\nepl_Ffbit_n_sub Bit_72  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[72]) );\nepl_Ffbit_n_sub Bit_73  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[73]) );\nepl_Ffbit_n_sub Bit_74  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[74]) );\nepl_Ffbit_n_sub Bit_75  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[75]) );\nepl_Ffbit_n_sub Bit_76  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[76]) );\nepl_Ffbit_n_sub Bit_77  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[77]) );\nepl_Ffbit_n_sub Bit_78  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[78]) );\nepl_Ffbit_n_sub Bit_79  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[79]) );\nepl_Ffbit_n_sub Bit_80  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[80]) );\nepl_Ffbit_n_sub Bit_81  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[81]) );\nepl_Ffbit_n_sub Bit_82  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[82]) );\nepl_Ffbit_n_sub Bit_83  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[83]) );\n\n// ==========================\n// Row6 (WL[6]) : Bit_84 ~ Bit_97\n// ==========================\nepl_Ffbit_n_sub Bit_84  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[84]) );\nepl_Ffbit_n_sub Bit_85  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[85]) );\nepl_Ffbit_n_sub Bit_86  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[86]) );\nepl_Ffbit_n_sub Bit_87  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[87]) );\nepl_Ffbit_n_sub Bit_88  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[88]) );\nepl_Ffbit_n_sub Bit_89  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[89]) );\nepl_Ffbit_n_sub Bit_90  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[90]) );\nepl_Ffbit_n_sub Bit_91  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[91]) );\nepl_Ffbit_n_sub Bit_92  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[92]) );\nepl_Ffbit_n_sub Bit_93  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[93]) );\nepl_Ffbit_n_sub Bit_94  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[94]) );\nepl_Ffbit_n_sub Bit_95  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[95]) );\nepl_Ffbit_n_sub Bit_96  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[96]) );\nepl_Ffbit_n_sub Bit_97  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[97]) );\n\n// ==========================\n// Row7 (WL[7]) : Bit_98 ~ Bit_111\n// ==========================\nepl_Ffbit_n_sub Bit_98  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[98]) );\nepl_Ffbit_n_sub Bit_99  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[99]) );\nepl_Ffbit_n_sub Bit_100 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[100]) );\nepl_Ffbit_n_sub Bit_101 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[101]) );\nepl_Ffbit_n_sub Bit_102 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[102]) );\nepl_Ffbit_n_sub Bit_103 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[103]) );\nepl_Ffbit_n_sub Bit_104 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[104]) );\nepl_Ffbit_n_sub Bit_105 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[105]) );\nepl_Ffbit_n_sub Bit_106 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[106]) );\nepl_Ffbit_n_sub Bit_107 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[107]) );\nepl_Ffbit_n_sub Bit_108 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[108]) );\nepl_Ffbit_n_sub Bit_109 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[109]) );\nepl_Ffbit_n_sub Bit_110 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[110]) );\nepl_Ffbit_n_sub Bit_111 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[111]) );\n\n\nreg [`COLUMN-1:0] pDataout0_r;\n\nalways @(*)\nbegin\n    pDataout0_r = {`COLUMN{1\'b0}};\n\n    case (pWl_i)\n        8\'b0000_0001:  // Row 0: Bit[0:13]\n        begin\n            pDataout0_r[0]  = pDtoc_w[0];\n            pDataout0_r[1]  = pDtoc_w[1];\n            pDataout0_r[2]  = pDtoc_w[2];\n            pDataout0_r[3]  = pDtoc_w[3];\n            pDataout0_r[4]  = pDtoc_w[4];\n            pDataout0_r[5]  = pDtoc_w[5];\n            pDataout0_r[6]  = pDtoc_w[6];\n            pDataout0_r[7]  = pDtoc_w[7];\n            pDataout0_r[8]  = pDtoc_w[8];\n            pDataout0_r[9]  = pDtoc_w[9];\n            pDataout0_r[10] = pDtoc_w[10];\n            pDataout0_r[11] = pDtoc_w[11];\n            pDataout0_r[12] = pDtoc_w[12];\n            pDataout0_r[13] = pDtoc_w[13];\n        end\n\n        8\'b0000_0010:  // Row 1: Bit[14:27]\n        begin\n            pDataout0_r[0]  = pDtoc_w[14];\n            pDataout0_r[1]  = pDtoc_w[15];\n            pDataout0_r[2]  = pDtoc_w[16];\n            pDataout0_r[3]  = pDtoc_w[17];\n            pDataout0_r[4]  = pDtoc_w[18];\n            pDataout0_r[5]  = pDtoc_w[19];\n            pDataout0_r[6]  = pDtoc_w[20];\n            pDataout0_r[7]  = pDtoc_w[21];\n            pDataout0_r[8]  = pDtoc_w[22];\n            pDataout0_r[9]  = pDtoc_w[23];\n            pDataout0_r[10] = pDtoc_w[24];\n            pDataout0_r[11] = pDtoc_w[25];\n            pDataout0_r[12] = pDtoc_w[26];\n            pDataout0_r[13] = pDtoc_w[27];\n        end\n\n        8\'b0000_0100:  // Row 2: Bit[28:41]\n        begin\n            pDataout0_r[0]  = pDtoc_w[28];\n            pDataout0_r[1]  = pDtoc_w[29];\n            pDataout0_r[2]  = pDtoc_w[30];\n            pDataout0_r[3]  = pDtoc_w[31];\n            pDataout0_r[4]  = pDtoc_w[32];\n            pDataout0_r[5]  = pDtoc_w[33];\n            pDataout0_r[6]  = pDtoc_w[34];\n            pDataout0_r[7]  = pDtoc_w[35];\n            pDataout0_r[8]  = pDtoc_w[36];\n            pDataout0_r[9]  = pDtoc_w[37];\n            pDataout0_r[10] = pDtoc_w[38];\n            pDataout0_r[11] = pDtoc_w[39];\n            pDataout0_r[12] = pDtoc_w[40];\n            pDataout0_r[13] = pDtoc_w[41];\n        end\n\n        8\'b0000_1000:  // Row 3: Bit[42:55]\n        begin\n            pDataout0_r[0]  = pDtoc_w[42];\n            pDataout0_r[1]  = pDtoc_w[43];\n            pDataout0_r[2]  = pDtoc_w[44];\n            pDataout0_r[3]  = pDtoc_w[45];\n            pDataout0_r[4]  = pDtoc_w[46];\n            pDataout0_r[5]  = pDtoc_w[47];\n            pDataout0_r[6]  = pDtoc_w[48];\n            pDataout0_r[7]  = pDtoc_w[49];\n            pDataout0_r[8]  = pDtoc_w[50];\n            pDataout0_r[9]  = pDtoc_w[51];\n            pDataout0_r[10] = pDtoc_w[52];\n            pDataout0_r[11] = pDtoc_w[53];\n            pDataout0_r[12] = pDtoc_w[54];\n            pDataout0_r[13] = pDtoc_w[55];\n        end\n\n        8\'b0001_0000:  // Row 4: Bit[56:69]\n        begin\n            pDataout0_r[0]  = pDtoc_w[56];\n            pDataout0_r[1]  = pDtoc_w[57];\n            pDataout0_r[2]  = pDtoc_w[58];\n            pDataout0_r[3]  = pDtoc_w[59];\n            pDataout0_r[4]  = pDtoc_w[60];\n            pDataout0_r[5]  = pDtoc_w[61];\n            pDataout0_r[6]  = pDtoc_w[62];\n            pDataout0_r[7]  = pDtoc_w[63];\n            pDataout0_r[8]  = pDtoc_w[64];\n            pDataout0_r[9]  = pDtoc_w[65];\n            pDataout0_r[10] = pDtoc_w[66];\n            pDataout0_r[11] = pDtoc_w[67];\n            pDataout0_r[12] = pDtoc_w[68];\n            pDataout0_r[13] = pDtoc_w[69];\n        end\n\n        8\'b0010_0000:  // Row 5: Bit[70:83]\n        begin\n            pDataout0_r[0]  = pDtoc_w[70];\n            pDataout0_r[1]  = pDtoc_w[71];\n            pDataout0_r[2]  = pDtoc_w[72];\n            pDataout0_r[3]  = pDtoc_w[73];\n            pDataout0_r[4]  = pDtoc_w[74];\n            pDataout0_r[5]  = pDtoc_w[75];\n            pDataout0_r[6]  = pDtoc_w[76];\n            pDataout0_r[7]  = pDtoc_w[77];\n            pDataout0_r[8]  = pDtoc_w[78];\n            pDataout0_r[9]  = pDtoc_w[79];\n            pDataout0_r[10] = pDtoc_w[80];\n            pDataout0_r[11] = pDtoc_w[81];\n            pDataout0_r[12] = pDtoc_w[82];\n            pDataout0_r[13] = pDtoc_w[83];\n        end\n\n        8\'b0100_0000:  // Row 6: Bit[84:97]\n        begin\n            pDataout0_r[0]  = pDtoc_w[84];\n            pDataout0_r[1]  = pDtoc_w[85];\n            pDataout0_r[2]  = pDtoc_w[86];\n            pDataout0_r[3]  = pDtoc_w[87];\n            pDataout0_r[4]  = pDtoc_w[88];\n            pDataout0_r[5]  = pDtoc_w[89];\n            pDataout0_r[6]  = pDtoc_w[90];\n            pDataout0_r[7]  = pDtoc_w[91];\n            pDataout0_r[8]  = pDtoc_w[92];\n            pDataout0_r[9]  = pDtoc_w[93];\n            pDataout0_r[10] = pDtoc_w[94];\n            pDataout0_r[11] = pDtoc_w[95];\n            pDataout0_r[12] = pDtoc_w[96];\n            pDataout0_r[13] = pDtoc_w[97];\n        end\n\n        8\'b1000_0000:  // Row 7: Bit[98:111]\n        begin\n            pDataout0_r[0]  = pDtoc_w[98];\n            pDataout0_r[1]  = pDtoc_w[99];\n            pDataout0_r[2]  = pDtoc_w[100];\n            pDataout0_r[3]  = pDtoc_w[101];\n            pDataout0_r[4]  = pDtoc_w[102];\n            pDataout0_r[5]  = pDtoc_w[103];\n            pDataout0_r[6]  = pDtoc_w[104];\n            pDataout0_r[7]  = pDtoc_w[105];\n            pDataout0_r[8]  = pDtoc_w[106];\n            pDataout0_r[9]  = pDtoc_w[107];\n            pDataout0_r[10] = pDtoc_w[108];\n            pDataout0_r[11] = pDtoc_w[109];\n            pDataout0_r[12] = pDtoc_w[110];\n            pDataout0_r[13] = pDtoc_w[111];\n        end\n\n        default:  // Invalid or idle (pWl_i = 0 or non-one-hot)\n        begin\n            pDataout0_r = {`COLUMN{1\'b0}};\n        end\n    endcase\nend\n\n\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pDto_o <= {`COLUMN{1\'b0}};\n        pRead01_o <= 1\'b0;\n    end\n    else if (pRead0_i)\n    begin\n        pDto_o <= pDataout0_r ;\n        pRead01_o <= 1\'b1;\n    end\n    else\n    begin\n        pDto_o <= {`COLUMN{1\'b0}};\n        pRead01_o <= 1\'b0;\n    end\nend\n\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pAcy2_o <= {`ADDR_AYO{1\'b0}};\n    end\n    else\n    begin\n        pAcy2_o <= pAcy1_i;\n    end\nend\n\n\n\n\nendmodule\n\n',
    'epl_Read_Mux_sub.v': '// epl_Read_Mux_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Read_Mux_sub (\n           input  wire [`COLUMN-1:0]      pDto_i,\n           input  wire [`ADDR_AYO-1:0]     pAcy2_i,\n           output reg  [`TWORD_WIDTH-1:0]  pDo_o,\n           output reg                      pRead1_o,\n           input  wire                     pClk_i,\n           input  wire                     nRst_i,\n           input  wire                     pRead01_i\n       );\n\nreg [`TWORD_WIDTH-1:0] pDomux_r;\n\n// ------------------------------------------------------------\n// Read data mux (case table; Column_Access-style; Python-friendly)\n// pAcy_i is assumed one-hot. Invalid values -> all-0.\n// ------------------------------------------------------------\nalways @(*)\nbegin\n    pDomux_r = {`TWORD_WIDTH{1\'b0}};\n\n    case (pAcy2_i)\n        2\'b01:\n        begin\n            // even columns\n            pDomux_r[0] = pDto_i[0];\n            pDomux_r[1] = pDto_i[2];\n            pDomux_r[2] = pDto_i[4];\n            pDomux_r[3] = pDto_i[6];\n            pDomux_r[4] = pDto_i[8];\n            pDomux_r[5] = pDto_i[10];\n            pDomux_r[6] = pDto_i[12];\n        end\n\n        2\'b10:\n        begin\n            // odd columns\n            pDomux_r[0] = pDto_i[1];\n            pDomux_r[1] = pDto_i[3];\n            pDomux_r[2] = pDto_i[5];\n            pDomux_r[3] = pDto_i[7];\n            pDomux_r[4] = pDto_i[9];\n            pDomux_r[5] = pDto_i[11];\n            pDomux_r[6] = pDto_i[13];\n        end\n\n        default:\n        begin\n            pDomux_r = {`TWORD_WIDTH{1\'b0}};\n        end\n    endcase\nend\n\n// ------------------------------------------------------------\n// Registered outputs (pDo_o & pRead1_o aligned)\n// ------------------------------------------------------------\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pDo_o    <= {`TWORD_WIDTH{1\'b0}};\n        pRead1_o <= 1\'b0;\n    end\n    else if (pRead01_i)\n    begin\n        pDo_o    <= pDomux_r;\n        pRead1_o <= 1\'b1;\n    end\n    else\n    begin\n        pRead1_o <= 1\'b0;\n        pDo_o    <={`TWORD_WIDTH{1\'b0}};\n    end\nend\n\nendmodule\n\n',
    'epl_Row_Decode_sub.v': '// epl_Row_Decode_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Row_Decode_sub (\n           input  wire [`ADDR_AX-1:0]  pAr_i,\n           output reg [`ADDR_AXO-1:0] pArx_o\n       );\n\nalways @(*)\nbegin\n    case (pAr_i)\n        3\'d0:\n            pArx_o = 8\'b0000_0001;\n        3\'d1:\n            pArx_o = 8\'b0000_0010;\n        3\'d2:\n            pArx_o = 8\'b0000_0100;\n        3\'d3:\n            pArx_o = 8\'b0000_1000;\n        3\'d4:\n            pArx_o = 8\'b0001_0000;\n        3\'d5:\n            pArx_o = 8\'b0010_0000;\n        3\'d6:\n            pArx_o = 8\'b0100_0000;\n        3\'d7:\n            pArx_o = 8\'b1000_0000;\n        default:\n            pArx_o = 8\'b0000_0000;\n    endcase\nend\n\n\nendmodule\n',
    'epl_Row_Selection_sub.v': '// epl_Row_Selection_sub.v\n`include "EPLFFRAM02_spec.vh"\n\nmodule epl_Row_Selection_sub (\n           input  wire                    pValide_i,\n           input  wire [`ADDR_AXO-1:0]     pArx_i,\n           input  wire                    pRead_i,\n           input  wire                    pClk_i,\n           input  wire                    nRst_i,\n           output reg                    pRead0_o,\n           output reg  [`ROW-1:0]          pWl_o\n       );\n\nalways @(posedge pClk_i or negedge nRst_i)\nbegin\n    if (!nRst_i)\n    begin\n        pWl_o <= {`ROW{1\'b0}};\n        pRead0_o <= 1\'b0;\n    end\n    else if (pValide_i)\n    begin\n        pWl_o <= pArx_i;\n        pRead0_o <= 1\'b0;\n    end\n    else if (pRead_i)\n    begin\n        pWl_o <= pArx_i;\n        pRead0_o <= 1\'b1;\n    end\n    else\n    begin\n        pWl_o <= {`ROW{1\'b0}};\n        pRead0_o <= 1\'b0;\n    end\nend\n\nendmodule\n',
    'epl_ecc_decoder.v': "// epl_ecc_decoder.v\nmodule epl_ecc_decoder (\n           // Global Ports\n           input         pCLK_i,\n           input         nRST_i,\n\n           // Control Ports\n           input         pREAD_i,\n\n           // Data Ports\n           input  [6:0]  pPARITYDATA_i,\n           output reg [3:0]  pDATA_o,\n           output reg    pERROR_o\n       );\n\n// internal signals\nwire [2:0] pSyndromeRaw_w;\nwire [2:0] pSyndrome_w;\nwire [2:0] ErrorPos_w;\n\n// registers for corrected code, next data, error flag, and valid signal\nreg [6:0] CorrectedCode_w;\nreg [3:0] pNextData_w;\nreg       pNextError_w;\nreg       pValid_w;        \n\n// syndrome calculation (combinational logic)\nassign pSyndromeRaw_w[0] = pPARITYDATA_i[0] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[6] ^ 1'b1;\nassign pSyndromeRaw_w[1] = pPARITYDATA_i[1] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;\nassign pSyndromeRaw_w[2] = pPARITYDATA_i[3] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;\n\nassign pSyndrome_w = (pREAD_i) ? pSyndromeRaw_w : 3'b000;\nassign ErrorPos_w  = pSyndrome_w;\n\n// combinational logic to determine next data, error flag, and valid signal based on read enable and syndrome\nalways @(*)\nbegin\n    // Default values when not reading: outputs are cleared to avoid stale data/error.\n    pNextData_w = 4'b0;\n    pNextError_w = 0;\n    pValid_w = 0;\n    CorrectedCode_w = pPARITYDATA_i;\n\n    // When read is enabled, calculate corrected data and error flag based on syndrome.\n    if (pREAD_i)\n    begin\n        // 1. error correction: if syndrome is non-zero, flip the bit at the indicated position.\n        if (ErrorPos_w != 3'b000)\n        begin\n            // ErrorPos_w is 1-based index for bit position (1 to 7), so we adjust for 0-based indexing in Verilog.\n            CorrectedCode_w[ErrorPos_w - 1] = ~CorrectedCode_w[ErrorPos_w - 1];\n            pNextError_w = 1;\n        end\n        else\n        begin\n            pNextError_w = 0;\n        end\n\n        // 2. data recovery: extract data bits from the corrected code. Data bits are at positions 3, 5, 6, 7 (0-based indices 2, 4, 5, 6).\n        // Data bits are usually at pos 3, 5, 6, 7 -> indices 2, 4, 5, 6\n        pNextData_w = {CorrectedCode_w[6], CorrectedCode_w[5], CorrectedCode_w[4], CorrectedCode_w[2]};\n\n        // 3. valid signal: indicate that the output data and error flag are valid when read is enabled.\n        pValid_w = 1'b1;\n    end\nend\n\n// register outputs on clock edge, with asynchronous reset. Outputs are cleared when not valid to avoid stale data/error. This also ensures that outputs are only updated when read is enabled and valid.\n// Note: The outputs are registered to ensure timing stability and to synchronize with the clock, providing a one-cycle delay from input to output. This is common in ECC decoders to allow for proper timing of data and error signals. The asynchronous reset ensures that the outputs are initialized to a known state when the system is reset.\nalways @(posedge pCLK_i or negedge nRST_i)\nbegin\n    if (!nRST_i)\n    begin\n        pDATA_o   <= 4'b0;\n        pERROR_o  <= 1'b0;\n    end\n    else  if (pValid_w)\n    begin\n        pDATA_o  <= pNextData_w;\n        pERROR_o <= pNextError_w;\n    end\n    else\n    begin\n        // Clear outputs when read is not valid to avoid stale data/error.\n        pDATA_o  <= 4'b0;\n        pERROR_o <= 1'b0;\n    end\nend\n\n\nendmodule\n\n",
    'epl_ecc_encoder.v': "// epl_ecc_encoder.v\nmodule epl_ecc_encoder (\n           // Global Ports\n           input         pCLK_i,\n           input         nRST_i,\n           input         pWRITE_i,\n           // Data Ports\n           input  [3:0]  pDATA_i,\n           output [6:0] pCODEWORD_o,\n           output reg [6:0] pCcodeword_o,\n           output pVALIDE_o\n       );\n\nwire [6:0] pCcodeword_w;\n\n\n// Codeword generation (combinational logic)\nassign pCODEWORD_o[6] = (pWRITE_i) ? pDATA_i[3] : 1'b0;\nassign pCODEWORD_o[5] = (pWRITE_i) ? pDATA_i[2] : 1'b0;\nassign pCODEWORD_o[4] = (pWRITE_i) ? pDATA_i[1] : 1'b0;\nassign pCODEWORD_o[3] = (pWRITE_i) ? {pDATA_i[1] ^ pDATA_i[2] ^ pDATA_i[3] ^ 1'b1} : 1'b0;\nassign pCODEWORD_o[2] = (pWRITE_i) ? pDATA_i[0] : 1'b0;\nassign pCODEWORD_o[1] = (pWRITE_i) ? {pDATA_i[0] ^ pDATA_i[2] ^ pDATA_i[3] ^ 1'b1} : 1'b0;\nassign pCODEWORD_o[0] = (pWRITE_i) ? {pDATA_i[0] ^ pDATA_i[1] ^ pDATA_i[3] ^ 1'b1} : 1'b0;\n\n// The codeword is only valid when pWRITE_i is high.\nassign pVALIDE_o = pWRITE_i;\nassign pCcodeword_w = pCODEWORD_o;\n\nalways @(posedge pCLK_i or negedge nRST_i)\nbegin\n    if (!nRST_i)\n    begin\n        pCcodeword_o <= 7'b0;\n    end\n    else  if (pVALIDE_o)\n    begin\n        pCcodeword_o <= pCcodeword_w;\n    end\n    else\n    begin\n        // Clear outputs when read is not valid to avoid stale data/error.\n        pCcodeword_o <= 7'b0;\n    end\nend\n\nendmodule\n\n",
    'epl_testbench_rtl_fi.v': '// epl_testbench_rtl_fi.v\n`timescale 1ns/1ps\n`include "EPLFFRAM02_spec.vh"\n\n// Allow overriding masks from compile command line if desired.\n// Example:\n//   +define+TB_RD_WORD_MASK_CONST=16\'h000C +define+TB_WF_WORD_MASK_CONST=16\'h0030\n`ifndef TB_RD_WORD_MASK_CONST\n  `define TB_RD_WORD_MASK_CONST 16\'h000C //addr 2??\n`endif\n`ifndef TB_WF_WORD_MASK_CONST\n  `define TB_WF_WORD_MASK_CONST 16\'h0030 //addr 4??\n`endif\n\nmodule epl_testbench_rtl_fi;\n\n//==== TB signals ====//\nreg pCLK_r;\nreg nRST_r;\nreg [`ADDR_WIDTH-1:0] pA_r;\nreg [`WORD_WIDTH-1:0] pD_r;\nreg nWEN_r;\nreg nCEN_r;\nreg [`FAULT-1:0] pFS_r;\n\nwire [`WORD_WIDTH-1:0] pQ_w;\nwire pERR_w;\nwire [6:0] pCcodeword_w;\n\n//==== Expected data ====//\nreg [`WORD_WIDTH-1:0] expected_data [`WORD-1:0];\nreg [`WORD_WIDTH-1:0] input_data    [`WORD-1:0];\nreg [`ADDR_WIDTH-1:0] input_addr    [`WORD-1:0];\n\ninteger i;\ninteger pass_count, fail_count;\ninteger errpass_count, errfail_count;\n\n// -----------------------------------------------------------------------------\n// TB word masks (must match the defaults used in epl_FFRAM02_top_fi)\n//   - RD targets : Addr 0x2, 0x3  -> 16\'h000C\n//   - WF targets : Addr 0x4, 0x5  -> 16\'h0030\n// NOTE: Use wires + assigns (no parameter/localparam) to avoid tool restrictions.\n// -----------------------------------------------------------------------------\nwire [`WORD-1:0] TB_RD_WORD_MASK;\nwire [`WORD-1:0] TB_WF_WORD_MASK;\nassign TB_RD_WORD_MASK = `TB_RD_WORD_MASK_CONST;\nassign TB_WF_WORD_MASK = `TB_WF_WORD_MASK_CONST;\n\n// -----------------------------------------------------------------------------\n// DUT (FI-enabled TOP)\n//   - Read disturb targets : Addr 0x2, 0x3\n//   - Write failure targets: Addr 0x4, 0x5\n// -----------------------------------------------------------------------------\n// Note:\n//   This FI-enabled top does not use "parameter"/"localparam". Word masks are\n//   configured inside epl_FFRAM02_top_fi.v by `define (default: RD=16\'h000C,\n//   WF=16\'h0030). If you need different masks, override them by compiler option.\n\nepl_FFRAM02_top_fi uut (\n                    .pA_i      (pA_r),\n                    .pD_i      (pD_r),\n                    .nWEN_i    (nWEN_r),\n                    .nCEN_i    (nCEN_r),\n                    .pCLOCK_i  (pCLK_r),\n                    .nRESET_i  (nRST_r),\n                    .pFS_i     (pFS_r),\n                    .pQ_o      (pQ_w),\n                    .pERR_o    (pERR_w),\n                    .pCcodeword1_o (pCcodeword_w)\n                );\n\n//==== CLK generator ====//\nparameter CLK_PERIOD = 20;\ninitial\nbegin\n    pCLK_r = 0;\n    forever #(CLK_PERIOD/2) pCLK_r = ~pCLK_r;\nend\n\n//==== Reset (Active-Low) ====//\ninitial\nbegin\n    nRST_r = 0;\n    repeat (3) @(posedge pCLK_r);\n    nRST_r = 1;\nend\n\n//==== Data init ====//\ninitial\nbegin\n    for (i = 0; i < `WORD; i = i + 1)\n    begin\n        input_addr[i]    = i[`ADDR_WIDTH-1:0];\n        input_data[i]    = (4\'hA + i) & 4\'hF;\n        expected_data[i] = input_data[i];\n    end\nend\n\n//==== Write task (optionally assert pFS during the command cycle) ====//\ntask write_data;\n    input [`ADDR_WIDTH-1:0] addr;\n    input [`WORD_WIDTH-1:0] data;\n    input                   fi_en;\n    begin\n        @(negedge pCLK_r);\n        nCEN_r <= 0;\n        nWEN_r <= 0;\n        pA_r   <= addr;\n        pD_r   <= data;\n        pFS_r  <= fi_en;\n\n        @(negedge pCLK_r);\n        nCEN_r <= 1;\n        nWEN_r <= 1;\n        pA_r   <= 0;\n        pD_r   <= 0;\n        pFS_r  <= 0;\n\n        // Write latency = 2 cycles (per original TB comment)\n        @(posedge pCLK_r);\n        @(posedge pCLK_r);\n\n        $display("[%0t] Write -> Addr: 0x%0h, Data: 0x%0h, FI: %0b", $time, addr, data, fi_en);\n    end\nendtask\n\n//==== Read task (optionally assert pFS during the command cycle) ====//\ntask read_data;\n    input  [`ADDR_WIDTH-1:0] addr;\n    input                    fi_en;\n    output [`WORD_WIDTH-1:0] val;\n    output                   err;\n    reg    [`WORD_WIDTH-1:0] temp_val;\n    reg                      temp_err;\n    begin\n        @(negedge pCLK_r);\n        nCEN_r <= 0;\n        nWEN_r <= 1;\n        pA_r   <= addr;\n        pD_r   <= 0;\n        pFS_r  <= fi_en;\n\n        @(negedge pCLK_r);\n        nCEN_r <= 1;\n        nWEN_r <= 1;\n        pA_r   <= 0;\n        pD_r   <= 0;\n        pFS_r  <= 0;\n\n        // Wait read latency = 4 cycles (same as original TB)\n        @(posedge pCLK_r);\n        @(posedge pCLK_r);\n        @(posedge pCLK_r);\n        @(posedge pCLK_r);\n\n        temp_val = pQ_w;\n        temp_err = pERR_w;\n\n        @(posedge pCLK_r); // idle\n\n        val = temp_val;\n        err = temp_err;\n    end\nendtask\n\n//==== reset task ====\ntask tb_pulse_reset;\nbegin\n    nRST_r = 0;\n    repeat (3) @(posedge pCLK_r);\n    nRST_r = 1;         \nend\nendtask\n\n\n//==== Checker helpers ====//\ntask check_no_error;\n    input [`ADDR_WIDTH-1:0] addr;\n    input [`WORD_WIDTH-1:0] val;\n    input                   err;\n    begin\n        if ((val === expected_data[addr]) && (err === 1\'b0))\n        begin\n            pass_count = pass_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS", $time, addr, expected_data[addr], val, err);\n        end\n        else\n        begin\n            fail_count = fail_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL", $time, addr, expected_data[addr], val, err);\n`ifdef ENABLE_ASSERT\n            $fatal("ASSERT FAIL (no_error) at addr 0x%0h", addr);\n`endif\n        end\n    end\nendtask\n\ntask check_expect_err_and_correct;\n    input [`ADDR_WIDTH-1:0] addr;\n    input [`WORD_WIDTH-1:0] val;\n    input                   err;\n    begin\n        if ((val === expected_data[addr]) && (err === 1\'b1))\n        begin\n            errpass_count = errpass_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS (corrected)", $time, addr, expected_data[addr], val, err);\n        end\n        else\n        begin\n            errfail_count = errfail_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL (corrected)", $time, addr, expected_data[addr], val, err);\n`ifdef ENABLE_ASSERT\n            $fatal("ASSERT FAIL (expect_err_and_correct) at addr 0x%0h", addr);\n`endif\n        end\n    end\nendtask\n\ntask check_expect_err_only;\n    input [`ADDR_WIDTH-1:0] addr;\n    input [`WORD_WIDTH-1:0] val;\n    input                   err;\n    begin\n        if (err === 1\'b1)\n        begin\n            errpass_count = errpass_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  PASS (error flagged)", $time, addr, val, err);\n        end\n        else\n        begin\n            errfail_count = errfail_count + 1;\n            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  FAIL (error flagged)", $time, addr, val, err);\n`ifdef ENABLE_ASSERT\n            $fatal("ASSERT FAIL (expect_err_only) at addr 0x%0h", addr);\n`endif\n        end\n    end\nendtask\n\n\n//==== Main flow ====//\nreg [`WORD_WIDTH-1:0] rdata;\nreg rerr;\n\ninitial\nbegin\n    // Init\n    pA_r   = 0;\n    pD_r   = 0;\n    nCEN_r = 1;\n    nWEN_r = 1;\n    pFS_r  = 0;\n\n    pass_count    = 0;\n    fail_count    = 0;\n    errpass_count = 0;\n    errfail_count = 0;\n\n    @(posedge nRST_r);\n    @(posedge pCLK_r);\n\n    $display("\\n====================");\n    $display("  FFRAM02 RTL Test (FI)");\n    $display("====================\\n");\n\n    // -----------------------------------------------------------------\n    // Phase 1: Normal write all\n    // -----------------------------------------------------------------\n    $display("---- Phase 1: Normal Write All ----");\n    for (i = 0; i < `WORD; i = i + 1)\n        write_data(input_addr[i], input_data[i], 1\'b0);\n    $display("");\n\n    // -----------------------------------------------------------------\n    // Phase 2: Normal read all (expect no error)\n    // -----------------------------------------------------------------\n    $display("---- Phase 2: Normal Read All (No Error) ----");\n    for (i = 0; i < `WORD; i = i + 1)\n    begin\n        read_data(input_addr[i], 1\'b0, rdata, rerr);\n        check_no_error(input_addr[i], rdata, rerr);\n    end\n    $display("");\n\n    // -----------------------------------------------------------------\n    // Phase 3: Read Disturb (FI on read, expect corrected + ERR=1)\n    //   - We assert pFS during ALL reads; only masked addresses inject.\n    // -----------------------------------------------------------------\n    $display("---- Phase 3: Read Disturb (Expect Corrected + ERR=1 on masked addrs) ----");\n    for (i = 0; i < `WORD; i = i + 1)\n    begin\n        read_data(input_addr[i], 1\'b1, rdata, rerr);\n        if (TB_RD_WORD_MASK[input_addr[i]])\n            check_expect_err_and_correct(input_addr[i], rdata, rerr);\n        else\n            check_no_error(input_addr[i], rdata, rerr);\n    end\n    $display("");\n\n    // -----------------------------------------------------------------\n    // Phase 4: Write Failure (FI on write)\n    //   - We assert pFS during ALL writes; only masked addresses corrupt.\n    //   - Then read back with pFS=0 and only check ERR=1 on masked addrs.\n    // -----------------------------------------------------------------\n    tb_pulse_reset();  // reset\n\n    $display("---- Phase 4: Write Failure (Expect ERR=1 on masked addrs) ----");\n    for (i = 0; i < `WORD; i = i + 1)\n        write_data(input_addr[i], input_data[i], 1\'b1);\n\n    for (i = 0; i < `WORD; i = i + 1)\n    begin\n        read_data(input_addr[i], 1\'b0, rdata, rerr);\n        if (TB_WF_WORD_MASK[input_addr[i]])\n            check_expect_err_only(input_addr[i], rdata, rerr);\n        else\n            check_no_error(input_addr[i], rdata, rerr);\n    end\n\n    // Summary\n    $display("\\n========================================");\n    $display("            Test Summary (FI)");\n    $display("========================================");\n    $display("  Pass (no-error)        : %0d", pass_count);\n    $display("  Fail (no-error)        : %0d", fail_count);\n    $display("  Pass (expect error)    : %0d", errpass_count);\n    $display("  Fail (expect error)    : %0d", errfail_count);\n    $display("----------------------------------------");\n    if ((fail_count == 0) && (errfail_count == 0))\n        $display("  Result                 : ALL PASSED");\n    else\n        $display("  Result                 : FAILED");\n    $display("========================================\\n");\n\n    $finish;\nend\n\n//==== Waveform Output ====//\ninitial\nbegin\n    $dumpfile("epl_ffram02_rtl.vcd");\n    $dumpvars(0, epl_testbench_rtl_fi);\n`ifdef RTL_SIMULATION\n\n    $fsdbDumpfile("epl_ffram02_rtl.fsdb");\n    `elsif POST_SIMULATION\n           $fsdbDumpfile("epl_ffram02_post.fsdb");\n`else\n    $fsdbDumpfile("epl_ffram02_default.fsdb");\n`endif\n\n    $fsdbDumpvars(0, epl_testbench_rtl_fi);\nend\n\n//==== SDF Annotation (Post-Simulation) ====//\n`ifdef POST_SIMULATION\ninitial\nbegin\n    $sdf_annotate("chip_syn.sdf", uut);\nend\n`endif\n\nendmodule\n\n\n\n\n\n\n\n\n\n\n\n\n\n',
}

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

    for name, content in TEMPLATE_CONTENTS.items():
        (out_dir / name).write_text(content, encoding="utf-8")

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
    top_src = TEMPLATE_CONTENTS["epl_FFRAM02_top_fi.v"]
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
