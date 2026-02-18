// epl_FiWrFail_sub.v
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
// This module simulates a write failure by either forcing the codeword to zero or flipping bits
assign pHit_w  = pFiWordMask_i[pA_i];
assign pFiEn_w = pWRITE_i & pFS_i[0] & pHit_w;

assign pCODEWORD_o = (pFiEn_w) ?
                     (pFiForceZero_i ? {`TWORD_WIDTH{1'b0}} : (pCODEWORD_i ^ pFiBitMask_i)) :
                     pCODEWORD_i;

endmodule
