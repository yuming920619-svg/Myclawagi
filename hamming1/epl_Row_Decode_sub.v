// epl_Row_Decode_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Row_Decode_sub (
           input  wire [`ADDR_AX-1:0]  pAr_i,
           output reg [`ADDR_AXO-1:0] pArx_o
       );

always @(*)
begin
    case (pAr_i)
        3'd0:
            pArx_o = 8'b0000_0001;
        3'd1:
            pArx_o = 8'b0000_0010;
        3'd2:
            pArx_o = 8'b0000_0100;
        3'd3:
            pArx_o = 8'b0000_1000;
        3'd4:
            pArx_o = 8'b0001_0000;
        3'd5:
            pArx_o = 8'b0010_0000;
        3'd6:
            pArx_o = 8'b0100_0000;
        3'd7:
            pArx_o = 8'b1000_0000;
        default:
            pArx_o = 8'b0000_0000;
    endcase
end


endmodule
