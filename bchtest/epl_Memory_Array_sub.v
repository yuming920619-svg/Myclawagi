// epl_Memory_Array_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Memory_Array_sub (
           input  wire [`COLUMN-1:0]      pWe_i,
           input  wire [`COLUMN-1:0]      pDi_i,
           input  wire [`ROW-1:0]         pWl_i,
           output reg  [`COLUMN-1:0]      pDto_o,
           output reg                      pRead01_o,
           input  wire                     pClk_i,
           input  wire                     pRead0_i,
           input  wire                     nRst_i,
           input  wire [`ADDR_AYO-1:0]    pAcy1_i,
           output reg  [`ADDR_AYO-1:0]    pAcy2_o
       );

wire [`TOTAL-1:0] pDtoc_w;
reg  [`COLUMN-1:0] pDataout0_r;

integer row_sel;
integer col_sel;
genvar row_gen;
genvar col_gen;

// ------------------------------------------------------------
// Bit-cell array
//   Flattened index = row * COLUMN + col
// ------------------------------------------------------------
generate
    for (row_gen = 0; row_gen < `ROW; row_gen = row_gen + 1)
    begin : GEN_ROW
        for (col_gen = 0; col_gen < `COLUMN; col_gen = col_gen + 1)
        begin : GEN_COL
            epl_Ffbit_n_sub BitCell (
                .pClk_i (pClk_i),
                .nRst_i (nRst_i),
                .pWec_i (pWl_i[row_gen] & pWe_i[col_gen]),
                .pDic_i (pDi_i[col_gen]),
                .pDtoc_o(pDtoc_w[(row_gen*`COLUMN)+col_gen])
            );
        end
    end
endgenerate

// ------------------------------------------------------------
// Row read mux: select one row of COLUMN bits by one-hot WL
// ------------------------------------------------------------
always @(*)
begin
    pDataout0_r = {`COLUMN{1'b0}};

    for (row_sel = 0; row_sel < `ROW; row_sel = row_sel + 1)
    begin
        if (pWl_i[row_sel])
        begin
            for (col_sel = 0; col_sel < `COLUMN; col_sel = col_sel + 1)
            begin
                pDataout0_r[col_sel] = pDtoc_w[(row_sel*`COLUMN)+col_sel];
            end
        end
    end
end

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pDto_o    <= {`COLUMN{1'b0}};
        pRead01_o <= 1'b0;
    end
    else if (pRead0_i)
    begin
        pDto_o    <= pDataout0_r;
        pRead01_o <= 1'b1;
    end
    else
    begin
        pDto_o    <= {`COLUMN{1'b0}};
        pRead01_o <= 1'b0;
    end
end

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pAcy2_o <= {`ADDR_AYO{1'b0}};
    end
    else
    begin
        pAcy2_o <= pAcy1_i;
    end
end

endmodule
