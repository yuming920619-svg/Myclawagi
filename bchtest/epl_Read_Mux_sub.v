// epl_Read_Mux_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Read_Mux_sub (
           input  wire [`COLUMN-1:0]       pDto_i,
           input  wire [`ADDR_AYO-1:0]     pAcy2_i,
           output reg  [`TWORD_WIDTH-1:0]  pDo_o,
           output reg                      pRead1_o,
           input  wire                     pClk_i,
           input  wire                     nRst_i,
           input  wire                     pRead01_i
       );

reg [`TWORD_WIDTH-1:0] pDomux_r;
integer idx;

// ------------------------------------------------------------
// Read data mux for MUX=2:
//   pAcy2_i = 2'b01 -> pick even columns
//   pAcy2_i = 2'b10 -> pick odd  columns
// ------------------------------------------------------------
always @(*)
begin
    pDomux_r = {`TWORD_WIDTH{1'b0}};

    case (pAcy2_i)
        2'b01:
        begin
            for (idx = 0; idx < `TWORD_WIDTH; idx = idx + 1)
            begin
                pDomux_r[idx] = pDto_i[idx*`MUX];
            end
        end

        2'b10:
        begin
            for (idx = 0; idx < `TWORD_WIDTH; idx = idx + 1)
            begin
                pDomux_r[idx] = pDto_i[(idx*`MUX)+1];
            end
        end

        default:
        begin
            pDomux_r = {`TWORD_WIDTH{1'b0}};
        end
    endcase
end

// ------------------------------------------------------------
// Registered outputs (pDo_o & pRead1_o aligned)
// ------------------------------------------------------------
always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pDo_o    <= {`TWORD_WIDTH{1'b0}};
        pRead1_o <= 1'b0;
    end
    else if (pRead01_i)
    begin
        pDo_o    <= pDomux_r;
        pRead1_o <= 1'b1;
    end
    else
    begin
        pRead1_o <= 1'b0;
        pDo_o    <= {`TWORD_WIDTH{1'b0}};
    end
end

endmodule
