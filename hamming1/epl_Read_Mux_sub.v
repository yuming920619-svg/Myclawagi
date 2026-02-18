// epl_Read_Mux_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Read_Mux_sub (
           input  wire [`COLUMN-1:0]      pDto_i,
           input  wire [`ADDR_AYO-1:0]     pAcy2_i,
           output reg  [`TWORD_WIDTH-1:0]  pDo_o,
           output reg                      pRead1_o,
           input  wire                     pClk_i,
           input  wire                     nRst_i,
           input  wire                     pRead01_i
       );

reg [`TWORD_WIDTH-1:0] pDomux_r;

// ------------------------------------------------------------
// Read data mux (case table; Column_Access-style; Python-friendly)
// pAcy_i is assumed one-hot. Invalid values -> all-0.
// ------------------------------------------------------------
always @(*)
begin
    pDomux_r = {`TWORD_WIDTH{1'b0}};

    case (pAcy2_i)
        2'b01:
        begin
            // even columns
            pDomux_r[0] = pDto_i[0];
            pDomux_r[1] = pDto_i[2];
            pDomux_r[2] = pDto_i[4];
            pDomux_r[3] = pDto_i[6];
            pDomux_r[4] = pDto_i[8];
            pDomux_r[5] = pDto_i[10];
            pDomux_r[6] = pDto_i[12];
        end

        2'b10:
        begin
            // odd columns
            pDomux_r[0] = pDto_i[1];
            pDomux_r[1] = pDto_i[3];
            pDomux_r[2] = pDto_i[5];
            pDomux_r[3] = pDto_i[7];
            pDomux_r[4] = pDto_i[9];
            pDomux_r[5] = pDto_i[11];
            pDomux_r[6] = pDto_i[13];
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
        pDo_o    <={`TWORD_WIDTH{1'b0}};
    end
end

endmodule

