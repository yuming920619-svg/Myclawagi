// epl_Column_Access_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Column_Access_sub (
           input  wire [`ADDR_AYO-1:0]    pAcy_i,
           input  wire                    pValide_i,
           input  wire [`TWORD_WIDTH-1:0] pCodeword_i,
           output reg  [`COLUMN-1:0]      pWe_o,
           input  wire                    pClk_i,
           input  wire                    nRst_i,
           output reg  [`ADDR_AYO-1:0]    pAcy1_o,
           output reg  [`COLUMN-1:0]      pDi_o
       );

reg [`COLUMN-1:0] pWemask_r;
reg [`COLUMN-1:0] pDs_r;
integer idx;

// ------------------------------------------------------------
// Column enable/data mapping for MUX=2:
//   pAcy_i = 2'b01 -> even columns (0,2,4,...)
//   pAcy_i = 2'b10 -> odd  columns (1,3,5,...)
// ------------------------------------------------------------
always @(*)
begin
    pWemask_r = {`COLUMN{1'b0}};
    pDs_r     = {`COLUMN{1'b0}};

    case (pAcy_i)
        2'b01:
        begin
            for (idx = 0; idx < `TWORD_WIDTH; idx = idx + 1)
            begin
                pWemask_r[idx*`MUX] = 1'b1;
                pDs_r[idx*`MUX]     = pCodeword_i[idx];
            end
        end

        2'b10:
        begin
            for (idx = 0; idx < `TWORD_WIDTH; idx = idx + 1)
            begin
                pWemask_r[(idx*`MUX)+1] = 1'b1;
                pDs_r[(idx*`MUX)+1]     = pCodeword_i[idx];
            end
        end

        default:
        begin
            pWemask_r = {`COLUMN{1'b0}};
            pDs_r     = {`COLUMN{1'b0}};
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
        pDi_o <= {`COLUMN{1'b0}};
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
