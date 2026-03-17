/******************************************************************************
* File Name   : epl_Row_Selection_sub.v
* Created     : 2026/01/08
* Author      : EPL Lab Memory Test and Repair Group
* Version     : 1.0
*
* Description :
*   Row Selection sub-module (synchronous)
*
*   - Synchronously register row one-hot address to wordline output (pWl_o).
*   - Priority behavior:
*       1. When pValide_i == 1:
*            - Latch pArx_i into pWl_o
*            - Force pRead0_o = 0
*       2. When pRead_i == 1:
*            - Latch pArx_i into pWl_o
*            - Assert pRead0_o for one clock cycle
*       3. Otherwise:
*            - Drive pWl_o to all-zero
*            - Deassert pRead0_o
*
*   - Active-low asynchronous reset clears pWl_o and pRead0_o.
*
* Modification History :
*   Date        Version    Author                               Description
*   ----------  ---------  -----------------------------------  ----------------
*   2026/01/08  1.0        EPL Lab Memory Test and Repair Group  Initial implementation
******************************************************************************/

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
