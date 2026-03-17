/******************************************************************************
* File Name   : epl_Column_Decode_sub.v
* Created     : 2026/01/08
* Author      : EPL Lab Memory Test and Repair Group
* Version     : 1.0
*
* Description :
*   Column Decode sub-module
*   - Decode column mux select (binary) to 1-of-2 onehot select.
*
* I/O :
*   Inputs  :
*     pAc_i[`ADDR_AY-1:0]     - Column mux select (binary)
*
*   Outputs :
*     pAcy_o[`ADDR_AYO-1:0]   - Column mux select (onehot)
*
* Modification History :
*   Date        Version    Author                               Description
*   ----------  ---------  -----------------------------------  ----------------
*   2026/01/08  1.0        EPL Lab Memory Test and Repair Group  Implement column decode
******************************************************************************/
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
