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

// internal signals
wire [2:0] pSyndromeRaw_w;
wire [2:0] pSyndrome_w;
wire [2:0] ErrorPos_w;

// registers for corrected code, next data, error flag, and valid signal
reg [6:0] CorrectedCode_w;
reg [3:0] pNextData_w;
reg       pNextError_w;
reg       pValid_w;        

// syndrome calculation (combinational logic)
assign pSyndromeRaw_w[0] = pPARITYDATA_i[0] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[6] ^ 1'b1;
assign pSyndromeRaw_w[1] = pPARITYDATA_i[1] ^ pPARITYDATA_i[2] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;
assign pSyndromeRaw_w[2] = pPARITYDATA_i[3] ^ pPARITYDATA_i[4] ^ pPARITYDATA_i[5] ^ pPARITYDATA_i[6] ^ 1'b1;

assign pSyndrome_w = (pREAD_i) ? pSyndromeRaw_w : 3'b000;
assign ErrorPos_w  = pSyndrome_w;

// combinational logic to determine next data, error flag, and valid signal based on read enable and syndrome
always @(*)
begin
    // Default values when not reading: outputs are cleared to avoid stale data/error.
    pNextData_w = 4'b0;
    pNextError_w = 0;
    pValid_w = 0;
    CorrectedCode_w = pPARITYDATA_i;

    // When read is enabled, calculate corrected data and error flag based on syndrome.
    if (pREAD_i)
    begin
        // 1. error correction: if syndrome is non-zero, flip the bit at the indicated position.
        if (ErrorPos_w != 3'b000)
        begin
            // ErrorPos_w is 1-based index for bit position (1 to 7), so we adjust for 0-based indexing in Verilog.
            CorrectedCode_w[ErrorPos_w - 1] = ~CorrectedCode_w[ErrorPos_w - 1];
            pNextError_w = 1;
        end
        else
        begin
            pNextError_w = 0;
        end

        // 2. data recovery: extract data bits from the corrected code. Data bits are at positions 3, 5, 6, 7 (0-based indices 2, 4, 5, 6).
        // Data bits are usually at pos 3, 5, 6, 7 -> indices 2, 4, 5, 6
        pNextData_w = {CorrectedCode_w[6], CorrectedCode_w[5], CorrectedCode_w[4], CorrectedCode_w[2]};

        // 3. valid signal: indicate that the output data and error flag are valid when read is enabled.
        pValid_w = 1'b1;
    end
end

// register outputs on clock edge, with asynchronous reset. Outputs are cleared when not valid to avoid stale data/error. This also ensures that outputs are only updated when read is enabled and valid.
// Note: The outputs are registered to ensure timing stability and to synchronize with the clock, providing a one-cycle delay from input to output. This is common in ECC decoders to allow for proper timing of data and error signals. The asynchronous reset ensures that the outputs are initialized to a known state when the system is reset.
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

