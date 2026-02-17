// epl_FiRdDist_sub.v
`include "EPLFFRAM02_spec.vh"

//------------------------------------------------------------------------------
// epl_FiRdDist_sub
//   Read-Disturb FI injection (synthesizable, combinational)
//------------------------------------------------------------------------------
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
