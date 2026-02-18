// EPLFFRAM02_spec.vh
// Shortened BCH configuration:
// - Payload per word      : 4 bits
// - ECC parity bits       : 11 bits
// - Stored codeword width : 15 bits (BCH(15,5, t=3) with fixed MSB payload bit = 0)
`define WORD             16
`define WORD_WIDTH       4
`define ECC_WIDTH        11
`define TWORD_WIDTH      15

`define MUX              2
`define FAULT            1
`define COLUMN           (`TWORD_WIDTH * `MUX)
`define ROW              (`WORD / `MUX)
`define TOTAL            (`ROW * `COLUMN)

`define ADDR_WIDTH       4
`define ADDR_AX          3
`define ADDR_AXO         8
`define ADDR_AY          1
`define ADDR_AYO         2

`define FI_WF_WORD_MASK 14485
`define FI_WF_BIT_MASK  15'b000010000000001
`define FI_WF_FORCE_ZERO 1'b0
`define FI_RD_WORD_MASK 2657
`define FI_RD_BIT_MASK  15'b000000000000111

`define TB_RD_WORD_MASK_CONST 2657
`define TB_WF_WORD_MASK_CONST 14485
