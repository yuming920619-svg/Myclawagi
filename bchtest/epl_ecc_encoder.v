// epl_ecc_encoder.v
`include "EPLFFRAM02_spec.vh"

module epl_ecc_encoder (
           input  wire                    pCLK_i,
           input  wire                    nRST_i,
           input  wire                    pWRITE_i,
           input  wire [`WORD_WIDTH-1:0]  pDATA_i,
           output wire [`TWORD_WIDTH-1:0] pCODEWORD_o,
           output reg  [`TWORD_WIDTH-1:0] pCcodeword_o,
           output wire                    pVALIDE_o
       );

// -----------------------------------------------------------------------------
// Systematic BCH(15,5,t=3) encoder:
//   g(x) = x^10 + x^8 + x^5 + x^4 + x^2 + x + 1  (11'b10100110111)
// Shortened payload uses 4 bits: payload5 = {1'b0, pDATA_i}
// -----------------------------------------------------------------------------
function [14:0] bch15_encode5;
    input [4:0] data5_i;
    reg [14:0] work;
    reg [14:0] poly_aligned;
    integer bit_idx;
begin
    work = {data5_i, 10'b0};
    poly_aligned = {4'b0000, 11'b10100110111};

    for (bit_idx = 14; bit_idx >= 10; bit_idx = bit_idx - 1)
    begin
        if (work[bit_idx])
            work = work ^ (poly_aligned << (bit_idx - 10));
    end

    bch15_encode5 = {data5_i, work[9:0]};
end
endfunction

wire [4:0] payload5_w;
wire [`TWORD_WIDTH-1:0] pCodewordRaw_w;

assign payload5_w    = {1'b0, pDATA_i};
assign pCodewordRaw_w = bch15_encode5(payload5_w);

assign pCODEWORD_o = pWRITE_i ? pCodewordRaw_w : {`TWORD_WIDTH{1'b0}};
assign pVALIDE_o   = pWRITE_i;

always @(posedge pCLK_i or negedge nRST_i)
begin
    if (!nRST_i)
        pCcodeword_o <= {`TWORD_WIDTH{1'b0}};
    else if (pVALIDE_o)
        pCcodeword_o <= pCodewordRaw_w;
    else
        pCcodeword_o <= {`TWORD_WIDTH{1'b0}};
end

endmodule
