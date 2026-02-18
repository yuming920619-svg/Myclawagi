// epl_Ffbit_n_sub.v
module epl_Ffbit_n_sub (
           input  wire                     pClk_i,
           input  wire                     nRst_i,
           input  wire                     pWec_i,
           input  wire                     pDic_i,
           output reg                      pDtoc_o
       );

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
        pDtoc_o <= 1'b0;
    else if (pWec_i)
    begin
        pDtoc_o <= pDic_i;
    end
end

endmodule
