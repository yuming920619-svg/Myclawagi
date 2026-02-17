//EPLFFRAM02_spec.vh
`define WORD             16      // 總共有幾個 word
`define WORD_WIDTH       4       // 每個 word 寬度（bits）
`define TWORD_WIDTH      7       // WORD_WIDTH + ECC_WIDTH
`define ECC_WIDTH        3       //所需要的給ECC的冗餘bits
`define MUX              2       // 多工器
`define FAULT            1      // 故障命令寬度
`define COLUMN           14      // TWORD_WIDTH * MUX
`define ROW              8      // WORD/MUX
`define TOTAL            112     // ROW*COLUMN
`define ADDR_WIDTH       4       // log2(WORD)
`define ADDR_AX          3       // row address bits A[m-1:log2(mux)]
`define ADDR_AXO         8      // 2^ADDR_AX
`define ADDR_AY          1       // column mux select bits Ay = A[log2(mux)-1:0]
`define ADDR_AYO         2       // 2^ADDR_AY
