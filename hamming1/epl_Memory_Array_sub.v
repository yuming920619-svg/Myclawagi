// epl_Memory_Array_sub.v
`include "EPLFFRAM02_spec.vh"

module epl_Memory_Array_sub (
           input  wire [`COLUMN-1:0]   pWe_i,
           input  wire [`COLUMN-1:0]   pDi_i,
           input  wire [`ROW-1:0]      pWl_i,
           output reg [`COLUMN-1:0]    pDto_o,
           output reg                  pRead01_o,
           input  wire                 pClk_i,
           input  wire                 pRead0_i,
           input  wire                 nRst_i,
           input  wire [`ADDR_AYO-1:0]  pAcy1_i,
           output reg [`ADDR_AYO-1:0]  pAcy2_o
       );


wire   [`TOTAL-1 : 0] pDtoc_w;

// ==========================
// Row0 (WL[0]) : Bit_0 ~ Bit_13
// ==========================
epl_Ffbit_n_sub Bit_0   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[0])  );
epl_Ffbit_n_sub Bit_1   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[1])  );
epl_Ffbit_n_sub Bit_2   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[2])  );
epl_Ffbit_n_sub Bit_3   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[3])  );
epl_Ffbit_n_sub Bit_4   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[4])  );
epl_Ffbit_n_sub Bit_5   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[5])  );
epl_Ffbit_n_sub Bit_6   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[6])  );
epl_Ffbit_n_sub Bit_7   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[7])  );
epl_Ffbit_n_sub Bit_8   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[8])  );
epl_Ffbit_n_sub Bit_9   ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[9])  );
epl_Ffbit_n_sub Bit_10  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[10]) );
epl_Ffbit_n_sub Bit_11  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[11]) );
epl_Ffbit_n_sub Bit_12  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[12]) );
epl_Ffbit_n_sub Bit_13  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[0] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[13]) );

// ==========================
// Row1 (WL[1]) : Bit_14 ~ Bit_27
// ==========================
epl_Ffbit_n_sub Bit_14  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[14]) );
epl_Ffbit_n_sub Bit_15  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[15]) );
epl_Ffbit_n_sub Bit_16  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[16]) );
epl_Ffbit_n_sub Bit_17  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[17]) );
epl_Ffbit_n_sub Bit_18  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[18]) );
epl_Ffbit_n_sub Bit_19  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[19]) );
epl_Ffbit_n_sub Bit_20  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[20]) );
epl_Ffbit_n_sub Bit_21  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[21]) );
epl_Ffbit_n_sub Bit_22  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[22]) );
epl_Ffbit_n_sub Bit_23  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[23]) );
epl_Ffbit_n_sub Bit_24  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[24]) );
epl_Ffbit_n_sub Bit_25  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[25]) );
epl_Ffbit_n_sub Bit_26  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[26]) );
epl_Ffbit_n_sub Bit_27  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[1] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[27]) );

// ==========================
// Row2 (WL[2]) : Bit_28 ~ Bit_41
// ==========================
epl_Ffbit_n_sub Bit_28  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[28]) );
epl_Ffbit_n_sub Bit_29  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[29]) );
epl_Ffbit_n_sub Bit_30  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[30]) );
epl_Ffbit_n_sub Bit_31  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[31]) );
epl_Ffbit_n_sub Bit_32  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[32]) );
epl_Ffbit_n_sub Bit_33  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[33]) );
epl_Ffbit_n_sub Bit_34  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[34]) );
epl_Ffbit_n_sub Bit_35  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[35]) );
epl_Ffbit_n_sub Bit_36  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[36]) );
epl_Ffbit_n_sub Bit_37  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[37]) );
epl_Ffbit_n_sub Bit_38  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[38]) );
epl_Ffbit_n_sub Bit_39  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[39]) );
epl_Ffbit_n_sub Bit_40  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[40]) );
epl_Ffbit_n_sub Bit_41  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[2] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[41]) );

// ==========================
// Row3 (WL[3]) : Bit_42 ~ Bit_55
// ==========================
epl_Ffbit_n_sub Bit_42  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[42]) );
epl_Ffbit_n_sub Bit_43  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[43]) );
epl_Ffbit_n_sub Bit_44  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[44]) );
epl_Ffbit_n_sub Bit_45  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[45]) );
epl_Ffbit_n_sub Bit_46  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[46]) );
epl_Ffbit_n_sub Bit_47  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[47]) );
epl_Ffbit_n_sub Bit_48  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[48]) );
epl_Ffbit_n_sub Bit_49  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[49]) );
epl_Ffbit_n_sub Bit_50  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[50]) );
epl_Ffbit_n_sub Bit_51  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[51]) );
epl_Ffbit_n_sub Bit_52  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[52]) );
epl_Ffbit_n_sub Bit_53  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[53]) );
epl_Ffbit_n_sub Bit_54  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[54]) );
epl_Ffbit_n_sub Bit_55  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[3] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[55]) );

// ==========================
// Row4 (WL[4]) : Bit_56 ~ Bit_69
// ==========================
epl_Ffbit_n_sub Bit_56  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[56]) );
epl_Ffbit_n_sub Bit_57  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[57]) );
epl_Ffbit_n_sub Bit_58  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[58]) );
epl_Ffbit_n_sub Bit_59  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[59]) );
epl_Ffbit_n_sub Bit_60  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[60]) );
epl_Ffbit_n_sub Bit_61  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[61]) );
epl_Ffbit_n_sub Bit_62  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[62]) );
epl_Ffbit_n_sub Bit_63  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[63]) );
epl_Ffbit_n_sub Bit_64  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[64]) );
epl_Ffbit_n_sub Bit_65  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[65]) );
epl_Ffbit_n_sub Bit_66  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[66]) );
epl_Ffbit_n_sub Bit_67  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[67]) );
epl_Ffbit_n_sub Bit_68  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[68]) );
epl_Ffbit_n_sub Bit_69  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[4] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[69]) );

// ==========================
// Row5 (WL[5]) : Bit_70 ~ Bit_83
// ==========================
epl_Ffbit_n_sub Bit_70  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[70]) );
epl_Ffbit_n_sub Bit_71  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[71]) );
epl_Ffbit_n_sub Bit_72  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[72]) );
epl_Ffbit_n_sub Bit_73  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[73]) );
epl_Ffbit_n_sub Bit_74  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[74]) );
epl_Ffbit_n_sub Bit_75  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[75]) );
epl_Ffbit_n_sub Bit_76  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[76]) );
epl_Ffbit_n_sub Bit_77  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[77]) );
epl_Ffbit_n_sub Bit_78  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[78]) );
epl_Ffbit_n_sub Bit_79  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[79]) );
epl_Ffbit_n_sub Bit_80  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[80]) );
epl_Ffbit_n_sub Bit_81  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[81]) );
epl_Ffbit_n_sub Bit_82  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[82]) );
epl_Ffbit_n_sub Bit_83  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[5] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[83]) );

// ==========================
// Row6 (WL[6]) : Bit_84 ~ Bit_97
// ==========================
epl_Ffbit_n_sub Bit_84  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[84]) );
epl_Ffbit_n_sub Bit_85  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[85]) );
epl_Ffbit_n_sub Bit_86  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[86]) );
epl_Ffbit_n_sub Bit_87  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[87]) );
epl_Ffbit_n_sub Bit_88  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[88]) );
epl_Ffbit_n_sub Bit_89  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[89]) );
epl_Ffbit_n_sub Bit_90  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[90]) );
epl_Ffbit_n_sub Bit_91  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[91]) );
epl_Ffbit_n_sub Bit_92  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[92]) );
epl_Ffbit_n_sub Bit_93  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[93]) );
epl_Ffbit_n_sub Bit_94  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[94]) );
epl_Ffbit_n_sub Bit_95  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[95]) );
epl_Ffbit_n_sub Bit_96  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[96]) );
epl_Ffbit_n_sub Bit_97  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[6] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[97]) );

// ==========================
// Row7 (WL[7]) : Bit_98 ~ Bit_111
// ==========================
epl_Ffbit_n_sub Bit_98  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[0]),  .pDic_i(pDi_i[0]),  .pDtoc_o(pDtoc_w[98]) );
epl_Ffbit_n_sub Bit_99  ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[1]),  .pDic_i(pDi_i[1]),  .pDtoc_o(pDtoc_w[99]) );
epl_Ffbit_n_sub Bit_100 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[2]),  .pDic_i(pDi_i[2]),  .pDtoc_o(pDtoc_w[100]) );
epl_Ffbit_n_sub Bit_101 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[3]),  .pDic_i(pDi_i[3]),  .pDtoc_o(pDtoc_w[101]) );
epl_Ffbit_n_sub Bit_102 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[4]),  .pDic_i(pDi_i[4]),  .pDtoc_o(pDtoc_w[102]) );
epl_Ffbit_n_sub Bit_103 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[5]),  .pDic_i(pDi_i[5]),  .pDtoc_o(pDtoc_w[103]) );
epl_Ffbit_n_sub Bit_104 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[6]),  .pDic_i(pDi_i[6]),  .pDtoc_o(pDtoc_w[104]) );
epl_Ffbit_n_sub Bit_105 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[7]),  .pDic_i(pDi_i[7]),  .pDtoc_o(pDtoc_w[105]) );
epl_Ffbit_n_sub Bit_106 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[8]),  .pDic_i(pDi_i[8]),  .pDtoc_o(pDtoc_w[106]) );
epl_Ffbit_n_sub Bit_107 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[9]),  .pDic_i(pDi_i[9]),  .pDtoc_o(pDtoc_w[107]) );
epl_Ffbit_n_sub Bit_108 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[10]), .pDic_i(pDi_i[10]), .pDtoc_o(pDtoc_w[108]) );
epl_Ffbit_n_sub Bit_109 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[11]), .pDic_i(pDi_i[11]), .pDtoc_o(pDtoc_w[109]) );
epl_Ffbit_n_sub Bit_110 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[12]), .pDic_i(pDi_i[12]), .pDtoc_o(pDtoc_w[110]) );
epl_Ffbit_n_sub Bit_111 ( .pClk_i(pClk_i), .nRst_i(nRst_i), .pWec_i(pWl_i[7] & pWe_i[13]), .pDic_i(pDi_i[13]), .pDtoc_o(pDtoc_w[111]) );


reg [`COLUMN-1:0] pDataout0_r;

always @(*)
begin
    pDataout0_r = {`COLUMN{1'b0}};

    case (pWl_i)
        8'b0000_0001:  // Row 0: Bit[0:13]
        begin
            pDataout0_r[0]  = pDtoc_w[0];
            pDataout0_r[1]  = pDtoc_w[1];
            pDataout0_r[2]  = pDtoc_w[2];
            pDataout0_r[3]  = pDtoc_w[3];
            pDataout0_r[4]  = pDtoc_w[4];
            pDataout0_r[5]  = pDtoc_w[5];
            pDataout0_r[6]  = pDtoc_w[6];
            pDataout0_r[7]  = pDtoc_w[7];
            pDataout0_r[8]  = pDtoc_w[8];
            pDataout0_r[9]  = pDtoc_w[9];
            pDataout0_r[10] = pDtoc_w[10];
            pDataout0_r[11] = pDtoc_w[11];
            pDataout0_r[12] = pDtoc_w[12];
            pDataout0_r[13] = pDtoc_w[13];
        end

        8'b0000_0010:  // Row 1: Bit[14:27]
        begin
            pDataout0_r[0]  = pDtoc_w[14];
            pDataout0_r[1]  = pDtoc_w[15];
            pDataout0_r[2]  = pDtoc_w[16];
            pDataout0_r[3]  = pDtoc_w[17];
            pDataout0_r[4]  = pDtoc_w[18];
            pDataout0_r[5]  = pDtoc_w[19];
            pDataout0_r[6]  = pDtoc_w[20];
            pDataout0_r[7]  = pDtoc_w[21];
            pDataout0_r[8]  = pDtoc_w[22];
            pDataout0_r[9]  = pDtoc_w[23];
            pDataout0_r[10] = pDtoc_w[24];
            pDataout0_r[11] = pDtoc_w[25];
            pDataout0_r[12] = pDtoc_w[26];
            pDataout0_r[13] = pDtoc_w[27];
        end

        8'b0000_0100:  // Row 2: Bit[28:41]
        begin
            pDataout0_r[0]  = pDtoc_w[28];
            pDataout0_r[1]  = pDtoc_w[29];
            pDataout0_r[2]  = pDtoc_w[30];
            pDataout0_r[3]  = pDtoc_w[31];
            pDataout0_r[4]  = pDtoc_w[32];
            pDataout0_r[5]  = pDtoc_w[33];
            pDataout0_r[6]  = pDtoc_w[34];
            pDataout0_r[7]  = pDtoc_w[35];
            pDataout0_r[8]  = pDtoc_w[36];
            pDataout0_r[9]  = pDtoc_w[37];
            pDataout0_r[10] = pDtoc_w[38];
            pDataout0_r[11] = pDtoc_w[39];
            pDataout0_r[12] = pDtoc_w[40];
            pDataout0_r[13] = pDtoc_w[41];
        end

        8'b0000_1000:  // Row 3: Bit[42:55]
        begin
            pDataout0_r[0]  = pDtoc_w[42];
            pDataout0_r[1]  = pDtoc_w[43];
            pDataout0_r[2]  = pDtoc_w[44];
            pDataout0_r[3]  = pDtoc_w[45];
            pDataout0_r[4]  = pDtoc_w[46];
            pDataout0_r[5]  = pDtoc_w[47];
            pDataout0_r[6]  = pDtoc_w[48];
            pDataout0_r[7]  = pDtoc_w[49];
            pDataout0_r[8]  = pDtoc_w[50];
            pDataout0_r[9]  = pDtoc_w[51];
            pDataout0_r[10] = pDtoc_w[52];
            pDataout0_r[11] = pDtoc_w[53];
            pDataout0_r[12] = pDtoc_w[54];
            pDataout0_r[13] = pDtoc_w[55];
        end

        8'b0001_0000:  // Row 4: Bit[56:69]
        begin
            pDataout0_r[0]  = pDtoc_w[56];
            pDataout0_r[1]  = pDtoc_w[57];
            pDataout0_r[2]  = pDtoc_w[58];
            pDataout0_r[3]  = pDtoc_w[59];
            pDataout0_r[4]  = pDtoc_w[60];
            pDataout0_r[5]  = pDtoc_w[61];
            pDataout0_r[6]  = pDtoc_w[62];
            pDataout0_r[7]  = pDtoc_w[63];
            pDataout0_r[8]  = pDtoc_w[64];
            pDataout0_r[9]  = pDtoc_w[65];
            pDataout0_r[10] = pDtoc_w[66];
            pDataout0_r[11] = pDtoc_w[67];
            pDataout0_r[12] = pDtoc_w[68];
            pDataout0_r[13] = pDtoc_w[69];
        end

        8'b0010_0000:  // Row 5: Bit[70:83]
        begin
            pDataout0_r[0]  = pDtoc_w[70];
            pDataout0_r[1]  = pDtoc_w[71];
            pDataout0_r[2]  = pDtoc_w[72];
            pDataout0_r[3]  = pDtoc_w[73];
            pDataout0_r[4]  = pDtoc_w[74];
            pDataout0_r[5]  = pDtoc_w[75];
            pDataout0_r[6]  = pDtoc_w[76];
            pDataout0_r[7]  = pDtoc_w[77];
            pDataout0_r[8]  = pDtoc_w[78];
            pDataout0_r[9]  = pDtoc_w[79];
            pDataout0_r[10] = pDtoc_w[80];
            pDataout0_r[11] = pDtoc_w[81];
            pDataout0_r[12] = pDtoc_w[82];
            pDataout0_r[13] = pDtoc_w[83];
        end

        8'b0100_0000:  // Row 6: Bit[84:97]
        begin
            pDataout0_r[0]  = pDtoc_w[84];
            pDataout0_r[1]  = pDtoc_w[85];
            pDataout0_r[2]  = pDtoc_w[86];
            pDataout0_r[3]  = pDtoc_w[87];
            pDataout0_r[4]  = pDtoc_w[88];
            pDataout0_r[5]  = pDtoc_w[89];
            pDataout0_r[6]  = pDtoc_w[90];
            pDataout0_r[7]  = pDtoc_w[91];
            pDataout0_r[8]  = pDtoc_w[92];
            pDataout0_r[9]  = pDtoc_w[93];
            pDataout0_r[10] = pDtoc_w[94];
            pDataout0_r[11] = pDtoc_w[95];
            pDataout0_r[12] = pDtoc_w[96];
            pDataout0_r[13] = pDtoc_w[97];
        end

        8'b1000_0000:  // Row 7: Bit[98:111]
        begin
            pDataout0_r[0]  = pDtoc_w[98];
            pDataout0_r[1]  = pDtoc_w[99];
            pDataout0_r[2]  = pDtoc_w[100];
            pDataout0_r[3]  = pDtoc_w[101];
            pDataout0_r[4]  = pDtoc_w[102];
            pDataout0_r[5]  = pDtoc_w[103];
            pDataout0_r[6]  = pDtoc_w[104];
            pDataout0_r[7]  = pDtoc_w[105];
            pDataout0_r[8]  = pDtoc_w[106];
            pDataout0_r[9]  = pDtoc_w[107];
            pDataout0_r[10] = pDtoc_w[108];
            pDataout0_r[11] = pDtoc_w[109];
            pDataout0_r[12] = pDtoc_w[110];
            pDataout0_r[13] = pDtoc_w[111];
        end

        default:  // Invalid or idle (pWl_i = 0 or non-one-hot)
        begin
            pDataout0_r = {`COLUMN{1'b0}};
        end
    endcase
end


always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pDto_o <= {`COLUMN{1'b0}};
        pRead01_o <= 1'b0;
    end
    else if (pRead0_i)
    begin
        pDto_o <= pDataout0_r ;
        pRead01_o <= 1'b1;
    end
    else
    begin
        pDto_o <= {`COLUMN{1'b0}};
        pRead01_o <= 1'b0;
    end
end

always @(posedge pClk_i or negedge nRst_i)
begin
    if (!nRst_i)
    begin
        pAcy2_o <= {`ADDR_AYO{1'b0}};
    end
    else
    begin
        pAcy2_o <= pAcy1_i;
    end
end




endmodule

