//==============================================================================
// Creation Date    : 2026/01/08
// Module Name      : epl_ecc_encoder
// Version          : 1.2
// Modification Date: 2026/01/16
// Description of Changes:
//                   1. Changed pCODEWORD_o assignments to conditional assignments based on pWRITE_i.
// IO Declarations  :
//              input         pWRITE_i,
//              input  [3:0]  pDATA_i,
//              output [6:0] pCODEWORD_o,
//              output pVALIDE_o
// Function Description:
//              ECC Encoder (Hamming Code).
//              Encodes 4-bit data into a 7-bit codeword with parity bits.
//              pCODEWORD_o is only valid when pWRITE_i is high.
// Note             : None
//==============================================================================
// epl_ecc_encoder.v
module epl_ecc_encoder (
           // Global Ports
           input         pCLK_i,
           input         nRST_i,
           input         pWRITE_i,
           // Data Ports
           input  [3:0]  pDATA_i,
           output [6:0] pCODEWORD_o,
           output reg [6:0] pCcodeword_o,
           output pVALIDE_o
       );

wire [6:0] pCcodeword_w;


// Codeword 輸出賦�?
assign pCODEWORD_o[6] = (pWRITE_i) ? pDATA_i[3] : 1'b0;
assign pCODEWORD_o[5] = (pWRITE_i) ? pDATA_i[2] : 1'b0;
assign pCODEWORD_o[4] = (pWRITE_i) ? pDATA_i[1] : 1'b0;
assign pCODEWORD_o[3] = (pWRITE_i) ? {pDATA_i[1] ^ pDATA_i[2] ^ pDATA_i[3] ^ 1'b1} : 1'b0;
assign pCODEWORD_o[2] = (pWRITE_i) ? pDATA_i[0] : 1'b0;
assign pCODEWORD_o[1] = (pWRITE_i) ? {pDATA_i[0] ^ pDATA_i[2] ^ pDATA_i[3] ^ 1'b1} : 1'b0;
assign pCODEWORD_o[0] = (pWRITE_i) ? {pDATA_i[0] ^ pDATA_i[1] ^ pDATA_i[3] ^ 1'b1} : 1'b0;

// ?��? Valid 訊�?
assign pVALIDE_o = pWRITE_i;
assign pCcodeword_w = pCODEWORD_o;
// 外部檢查編碼訊�?
always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
    begin
        pCcodeword_o <= 7'b0;
    end
    else  if (pVALIDE_o)
    begin
        pCcodeword_o <= pCcodeword_w;
    end
    else
    begin
        // Clear outputs when read is not valid to avoid stale data/error.
        pCcodeword_o <= 7'b0;
    end
end

endmodule

