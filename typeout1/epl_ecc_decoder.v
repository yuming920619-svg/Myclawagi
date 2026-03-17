//==============================================================================
// Creation Date    : 2026/01/08
// Module Name      : epl_ecc_decoder
// Version          : 1.1
// Modification Date: 2026/01/16
// Description of Changes:
//                   1. Changed pCLK_i and nRST_i signal names to match IO declarations.
//                   2. Updated syndrome calculation to include 1'b1 parity term.
// IO Declarations  :
//              input         pCLK_i
//              input         nRST_i
//              input         pREAD_i
//              input  [6:0]  pPARITYDATA_i
//              output [3:0]  pDATA_o
//              output        pERROR_o
// Function Description:
//              ECC Decoder (Hamming Code).
//              Calculates Syndrome to detect and correct single-bit errors,
//              recovering 4-bit data.
//              Output signals are registered and delayed by one clock cycle.
// Note             : Asynchronous active-low reset (nRST_i).
//==============================================================================
// epl_ecc_decoder.v
module epl_ecc_decoder (
           // Global Ports
           input         pCLK_i,
           input         nRST_i,

           // Control Ports
           input         pREAD_i,

           // Data Ports
           input  [6:0]  pPARITYDATA_i,
           output reg [3:0]  pDATA_o,
           output reg    pERROR_o
       );

// ?§éƒ¨ç·šè·¯ (Combinational Logic Wires)
wire [2:0] pSyndromeRaw_w;
wire [2:0] pSyndrome_w;
wire [2:0] ErrorPos_w;

// çµ„å??è¼¯ä¸­é?è¨Šè? (Naming convention: _w for wires/comb logic)
reg [6:0] CorrectedCode_w;
reg [3:0] pNextData_w;
reg       pNextError_w;
reg       pValid_w;        // ?§éƒ¨??Valid wire

// çµ„å??è¼¯: Syndrome è¨ˆç? (Hamming (7,4))
assign pSyndromeRaw_w[0] = pPARITYDATA_i[0] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[6] ^ 1'b1;
assign pSyndromeRaw_w[1] = pPARITYDATA_i[1] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;
assign pSyndromeRaw_w[2] = pPARITYDATA_i[3] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;

assign pSyndrome_w = (pREAD_i) ? pSyndromeRaw_w : 3'b000;
assign ErrorPos_w  = pSyndrome_w;

// ä¸»è?è§?¢¼çµ„å??è¼¯ (Combinational Logic)
always @(*)
begin
    // ?è¨­??
    pNextData_w = 4'b0;
    pNextError_w = 0;
    pValid_w = 0;
    CorrectedCode_w = pPARITYDATA_i;

    // ?¶è??–è???(pREAD_i) ??1 ?‚ï??§éƒ¨?è¼¯?‹å??‹ç?
    if (pREAD_i)
    begin
        // 1. ?·è??¯èª¤ä¿®æ­£
        if (ErrorPos_w != 3'b000)
        begin
            // ErrorPos_w ?¸å€¼å???Bit ä½ç½® (1-based)ï¼Œè???Index (0-based) ?€æ¸?1
            CorrectedCode_w[ErrorPos_w - 1] = ~CorrectedCode_w[ErrorPos_w - 1];
            pNextError_w = 1;
        end
        else
        begin
            pNextError_w = 0;
        end

        // 2. è¼¸å‡ºè³‡æ?? å? (Hamming 7,4 data mapping)
        // Data bits are usually at pos 3, 5, 6, 7 -> indices 2, 4, 5, 6
        pNextData_w = {CorrectedCode_w[6], CorrectedCode_w[5], CorrectedCode_w[4], CorrectedCode_w[2]};

        // 3. ?‰é??§éƒ¨ Valid è¨Šè?
        pValid_w = 1'b1;
    end
end

// è¼¸å‡º?«å???(Sequential Logic)
// è®“è??Ÿè???CLK ç©©å?ä¸€?å??é€å‡ºä¾?
always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
    begin
        pDATA_o   <= 4'b0;
        pERROR_o  <= 1'b0;
    end
    else  if (pValid_w)
    begin
        pDATA_o  <= pNextData_w;
        pERROR_o <= pNextError_w;
    end
    else
    begin
        // Clear outputs when read is not valid to avoid stale data/error.
        pDATA_o  <= 4'b0;
        pERROR_o <= 1'b0;
    end
end


endmodule

