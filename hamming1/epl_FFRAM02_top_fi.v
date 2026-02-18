// epl_FFRAM02_top_fi.v
`include "EPLFFRAM02_spec.vh"

//------------------------------------------------------------------------------
// FI configuration (no "parameter" / "localparam" used)
// - You can override these by compiler option, e.g.
//     +define+FI_WF_WORD_MASK=16'h0030
//------------------------------------------------------------------------------
`ifndef FI_WF_WORD_MASK
  `define FI_WF_WORD_MASK 16'h0030
`endif
`ifndef FI_WF_BIT_MASK
  `define FI_WF_BIT_MASK  7'b0000001
`endif
`ifndef FI_WF_FORCE_ZERO
  `define FI_WF_FORCE_ZERO 1'b1
`endif

`ifndef FI_RD_WORD_MASK
  `define FI_RD_WORD_MASK 16'h000C
`endif
`ifndef FI_RD_BIT_MASK
  `define FI_RD_BIT_MASK  7'b0000001
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
           output wire [6:0]              pCcodeword1_o
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
wire [6:0] pCcodeword_w;
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
assign pCcodeword1_o = pCcodeword_w [6:0];
assign pFs_w    = pFS_i;

// Latch read address and FI request for read-disturb mode
always @(posedge pCLOCK_i or negedge nRESET_i)
begin
    if (!nRESET_i)
    begin
        pRdAddr_r <= {`ADDR_WIDTH{1'b0}};
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
