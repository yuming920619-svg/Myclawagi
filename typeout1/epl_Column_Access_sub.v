//==============================================================================
// File Name   : epl_Column_Access_sub.v
// Created     : 2026/01/08
// Author      : EPL Lab Memory Test and Repair Group
// Version     : 0.3
//
// Description :
//   Column Access sub-module.
//
//   - When pValide_i is asserted, latch incoming pCodeword_i (TWORD_WIDTH bits)
//     and expand it into column-wise bitline data pDi_o (COLUMN bits).
//   - Column expansion is controlled by one-hot pAcy_i (MUX = 2):
//       pAcy_i = 2'b01 : map codeword bits to even columns
//       pAcy_i = 2'b10 : map codeword bits to odd  columns
//   - Generate column write enable pWe_o (COLUMN bits) with the same
//     even/odd sparse mapping.
//   - When pValide_i is deasserted (idle), pWe_o and pDi_o are synchronously
//     cleared to zero.
//
// I/O Description :
//   pClk_i        : Clock input
//   nRst_i        : Asynchronous active-low reset
//   pValide_i    : Write valid enable
//   pAcy_i       : One-hot column select (even / odd)
//   pAcy1_o      : Registered pAcy_i (aligned to pWe_o/pDi_o)
//   pCodeword_i  : Input codeword data (TWORD_WIDTH bits)
//   pWe_o        : Column write enable (COLUMN bits, sparse mapped)
//   pDi_o        : Column data output (COLUMN bits, sparse mapped)
//
// Notes :
//   - pAcy_i is assumed to be one-hot. Invalid values result in zero output.
//   - This module performs only column-level expansion; no storage is included.
//==============================================================================

`include "EPLFFRAM02_spec.vh"

module epl_Column_Access_sub (
           input  wire [`ADDR_AYO-1:0]    pAcy_i,
           input  wire                    pValide_i,
           input  wire [`TWORD_WIDTH-1:0] pCodeword_i,
           output reg  [`COLUMN-1:0]      pWe_o,
           input  wire                    pClk_i,
           input  wire                    nRst_i,
           output  reg [`ADDR_AYO-1:0]    pAcy1_o,
           output reg  [`COLUMN-1:0]  pDi_o
       );

reg [`COLUMN-1:0] pWemask_r , pDs_r;

// ------------------------------------------------------------
// Column enable mask (case table; Python-friendly)
// pAcy_i is assumed one-hot. Invalid values -> all-0.
// ------------------------------------------------------------
always @(*)
begin
    pWemask_r = {`COLUMN{1'b0}};
    pDs_r = {`COLUMN{1'b0}};
    case (pAcy_i)
        // MUX = 2 (one-hot)
        2'b01:
        begin
            // even columns
            pWemask_r[0]  = 1'b1;
            pWemask_r[2]  = 1'b1;
            pWemask_r[4]  = 1'b1;
            pWemask_r[6]  = 1'b1;
            pWemask_r[8]  = 1'b1;
            pWemask_r[10] = 1'b1;
            pWemask_r[12] = 1'b1;
            pDs_r[0] = pCodeword_i[0];
            pDs_r[2] = pCodeword_i[1];
            pDs_r[4] = pCodeword_i[2];
            pDs_r[6] = pCodeword_i[3];
            pDs_r[8] = pCodeword_i[4];
            pDs_r[10] = pCodeword_i[5];
            pDs_r[12] = pCodeword_i[6];

        end

        2'b10:
        begin
            // odd columns
            pWemask_r[1]  = 1'b1;
            pWemask_r[3]  = 1'b1;
            pWemask_r[5]  = 1'b1;
            pWemask_r[7]  = 1'b1;
            pWemask_r[9]  = 1'b1;
            pWemask_r[11] = 1'b1;
            pWemask_r[13] = 1'b1;
            pDs_r[1] = pCodeword_i[0];
            pDs_r[3] = pCodeword_i[1];
            pDs_r[5] = pCodeword_i[2];
            pDs_r[7] = pCodeword_i[3];
            pDs_r[9] = pCodeword_i[4];
            pDs_r[11] = pCodeword_i[5];
            pDs_r[13] = pCodeword_i[6];

        end

        default:
        begin
            pWemask_r = {`COLUMN{1'b0}};
        end
    endcase
end

// ------------------------------------------------------------
// Registered outputs (pWe_o & pDi_o aligned)
// ------------------------------------------------------------
always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pWe_o <= {`COLUMN{1'b0}};
        pDi_o <= {`COLUMN{1'b0}};
    end
    else if (pValide_i)
    begin
        pWe_o <= pWemask_r;
        pDi_o <= pDs_r;
    end
    else
    begin
        pWe_o <= {`COLUMN{1'b0}};
        pDi_o <={`COLUMN{1'b0}};
    end
end


always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pAcy1_o <= {`ADDR_AYO{1'b0}};
    end
    else
    begin
        pAcy1_o <= pAcy_i;
    end
end
endmodule


