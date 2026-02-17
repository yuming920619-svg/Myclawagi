// epl_Control_Circuit_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Control_Circuit_sub (
           input  wire nWen_i,
           input  wire nCen_i,
           output wire pWrite_o,
           output wire pRead_o
       );

assign pWrite_o = (~nCen_i) & (~nWen_i);
assign pRead_o  = (~nCen_i) & ( nWen_i);

endmodule
