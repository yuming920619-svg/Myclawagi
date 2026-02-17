// epl_Column_Decode_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Column_Decode_sub (
           input  wire [`ADDR_AY-1:0]  pAc_i,
           output reg  [`ADDR_AYO-1:0] pAcy_o
       );

always @(*)
begin
    case (pAc_i)
        1'd0:
            pAcy_o = 2'b01;
        1'd1:
            pAcy_o = 2'b10;
        default:
            pAcy_o = 2'b00;
    endcase
end

endmodule
