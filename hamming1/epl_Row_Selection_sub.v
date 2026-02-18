// epl_Row_Selection_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Row_Selection_sub (
           input  wire                    pValide_i,
           input  wire [`ADDR_AXO-1:0]     pArx_i,
           input  wire                    pRead_i,
           input  wire                    pClk_i,
           input  wire                    nRst_i,
           output reg                    pRead0_o,
           output reg  [`ROW-1:0]          pWl_o
       );

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pWl_o <= {`ROW{1'b0}};
        pRead0_o <= 1'b0;
    end
    else if (pValide_i)
    begin
        pWl_o <= pArx_i;
        pRead0_o <= 1'b0;
    end
    else if (pRead_i)
    begin
        pWl_o <= pArx_i;
        pRead0_o <= 1'b1;
    end
    else
    begin
        pWl_o <= {`ROW{1'b0}};
        pRead0_o <= 1'b0;
    end
end

endmodule
