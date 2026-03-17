/******************************************************************************
* File Name   : epl_Control_Circut_sub.v
* Created     : 2026/01/08
* Author      : EPL Lab Memory Test and Repair Group
* Version     : 1.0
*
* Description :
*   Control Circuit sub-module
*   - Generate internal read/write enables from chip enable and write enable.
*   - nCen_i : active-low chip enable
*   - nWen_i : active-low write enable
*
* I/O :
*   Inputs  :
*     nWen_i     - Write enable (active-low)
*     nCen_i     - Chip enable  (active-low)
*
*   Outputs :
*     pWrite_o   - Write enable (active-high)
*     pRead_o    - Read  enable (active-high)
*
* Modification History :
*   Date        Version    Author                               Description
*   ----------  ---------  -----------------------------------  ----------------
*   2026/01/08  1.0        EPL Lab Memory Test and Repair Group  Implement control circuit
******************************************************************************/
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
