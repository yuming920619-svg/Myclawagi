// epl_testbench_rtl_fi.v
`timescale 1ns/1ps
`include "EPLFFRAM02_spec.vh"

// Allow overriding masks from compile command line if desired.
// Example:
//   +define+TB_RD_WORD_MASK_CONST=16'h000C +define+TB_WF_WORD_MASK_CONST=16'h0030
`ifndef TB_RD_WORD_MASK_CONST
  `define TB_RD_WORD_MASK_CONST `FI_RD_WORD_MASK
`endif
`ifndef TB_WF_WORD_MASK_CONST
  `define TB_WF_WORD_MASK_CONST `FI_WF_WORD_MASK
`endif

module epl_testbench_rtl_fi;

//==== TB signals ====//
reg pCLK_r;
reg nRST_r;
reg [`ADDR_WIDTH-1:0] pA_r;
reg [`WORD_WIDTH-1:0] pD_r;
reg nWEN_r;
reg nCEN_r;
reg [`FAULT-1:0] pFS_r;

wire [`WORD_WIDTH-1:0] pQ_w;
wire pERR_w;
wire [`TWORD_WIDTH-1:0] pCcodeword_w;

//==== Expected data ====//
reg [`WORD_WIDTH-1:0] expected_data [`WORD-1:0];
reg [`WORD_WIDTH-1:0] input_data    [`WORD-1:0];
reg [`ADDR_WIDTH-1:0] input_addr    [`WORD-1:0];

integer i;
integer pass_count, fail_count;
integer errpass_count, errfail_count;

// -----------------------------------------------------------------------------
// TB word masks (must match the defaults used in epl_FFRAM02_top_fi)
//   - RD targets : Addr 0x2, 0x3  -> 16'h000C
//   - WF targets : Addr 0x4, 0x5  -> 16'h0030
// NOTE: Use wires + assigns (no parameter/localparam) to avoid tool restrictions.
// -----------------------------------------------------------------------------
wire [`WORD-1:0] TB_RD_WORD_MASK;
wire [`WORD-1:0] TB_WF_WORD_MASK;
assign TB_RD_WORD_MASK = `TB_RD_WORD_MASK_CONST;
assign TB_WF_WORD_MASK = `TB_WF_WORD_MASK_CONST;

// -----------------------------------------------------------------------------
// DUT (FI-enabled TOP)
//   - Read disturb targets : Addr 0x2, 0x3
//   - Write failure targets: Addr 0x4, 0x5
// -----------------------------------------------------------------------------
// Note:
//   This FI-enabled top does not use "parameter"/"localparam". Word masks are
//   configured inside epl_FFRAM02_top_fi.v by `define (default: RD=16'h000C,
//   WF=16'h0030). If you need different masks, override them by compiler option.

epl_FFRAM02_top_fi uut (
                    .pA_i      (pA_r),
                    .pD_i      (pD_r),
                    .nWEN_i    (nWEN_r),
                    .nCEN_i    (nCEN_r),
                    .pCLOCK_i  (pCLK_r),
                    .nRESET_i  (nRST_r),
                    .pFS_i     (pFS_r),
                    .pQ_o      (pQ_w),
                    .pERR_o    (pERR_w),
                    .pCcodeword1_o (pCcodeword_w)
                );

//==== CLK generator ====//
parameter CLK_PERIOD = 20;
initial
begin
    pCLK_r = 0;
    forever #(CLK_PERIOD/2) pCLK_r = ~pCLK_r;
end

//==== Reset (Active-Low) ====//
initial
begin
    nRST_r = 0;
    repeat (3) @(posedge pCLK_r);
    nRST_r = 1;
end

//==== Data init ====//
initial
begin
    for (i = 0; i < `WORD; i = i + 1)
    begin
        input_addr[i]    = i[`ADDR_WIDTH-1:0];
        input_data[i]    = i[3:0] + 4'hA;
        expected_data[i] = input_data[i];
    end
end

//==== Write task (optionally assert pFS during the command cycle) ====//
task write_data;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] data;
    input                   fi_en;
    begin
        @(negedge pCLK_r);
        nCEN_r <= 0;
        nWEN_r <= 0;
        pA_r   <= addr;
        pD_r   <= data;
        pFS_r  <= fi_en;

        @(negedge pCLK_r);
        nCEN_r <= 1;
        nWEN_r <= 1;
        pA_r   <= 0;
        pD_r   <= 0;
        pFS_r  <= 0;

        // Write latency = 2 cycles (per original TB comment)
        @(posedge pCLK_r);
        @(posedge pCLK_r);

        $display("[%0t] Write -> Addr: 0x%0h, Data: 0x%0h, FI: %0b", $time, addr, data, fi_en);
    end
endtask

//==== Read task (optionally assert pFS during the command cycle) ====//
task read_data;
    input  [`ADDR_WIDTH-1:0] addr;
    input                    fi_en;
    output [`WORD_WIDTH-1:0] val;
    output                   err;
    reg    [`WORD_WIDTH-1:0] temp_val;
    reg                      temp_err;
    begin
        @(negedge pCLK_r);
        nCEN_r <= 0;
        nWEN_r <= 1;
        pA_r   <= addr;
        pD_r   <= 0;
        pFS_r  <= fi_en;

        @(negedge pCLK_r);
        nCEN_r <= 1;
        nWEN_r <= 1;
        pA_r   <= 0;
        pD_r   <= 0;
        pFS_r  <= 0;

        // Wait read latency = 4 cycles (same as original TB)
        @(posedge pCLK_r);
        @(posedge pCLK_r);
        @(posedge pCLK_r);
        @(posedge pCLK_r);

        temp_val = pQ_w;
        temp_err = pERR_w;

        @(posedge pCLK_r); // idle

        val = temp_val;
        err = temp_err;
    end
endtask

//==== reset task ====
task tb_pulse_reset;
begin
    nRST_r = 0;
    repeat (3) @(posedge pCLK_r);
    nRST_r = 1;         
end
endtask


//==== Checker helpers ====//
task check_no_error;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if ((val === expected_data[addr]) && (err === 1'b0))
        begin
            pass_count = pass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS", $time, addr, expected_data[addr], val, err);
        end
        else
        begin
            fail_count = fail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL", $time, addr, expected_data[addr], val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (no_error) at addr 0x%0h", addr);
`endif
        end
    end
endtask

task check_expect_err_and_correct;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if ((val === expected_data[addr]) && (err === 1'b1))
        begin
            errpass_count = errpass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  PASS (corrected)", $time, addr, expected_data[addr], val, err);
        end
        else
        begin
            errfail_count = errfail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Expect:0x%0h Got:0x%0h ERR:%0b  FAIL (corrected)", $time, addr, expected_data[addr], val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (expect_err_and_correct) at addr 0x%0h", addr);
`endif
        end
    end
endtask

task check_expect_err_only;
    input [`ADDR_WIDTH-1:0] addr;
    input [`WORD_WIDTH-1:0] val;
    input                   err;
    begin
        if (err === 1'b1)
        begin
            errpass_count = errpass_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  PASS (error flagged)", $time, addr, val, err);
        end
        else
        begin
            errfail_count = errfail_count + 1;
            $display("[%0t] Read  -> Addr:0x%0h Got:0x%0h ERR:%0b  FAIL (error flagged)", $time, addr, val, err);
`ifdef ENABLE_ASSERT
            $fatal("ASSERT FAIL (expect_err_only) at addr 0x%0h", addr);
`endif
        end
    end
endtask


//==== Main flow ====//
reg [`WORD_WIDTH-1:0] rdata;
reg rerr;

initial
begin
    // Init
    pA_r   = 0;
    pD_r   = 0;
    nCEN_r = 1;
    nWEN_r = 1;
    pFS_r  = 0;

    pass_count    = 0;
    fail_count    = 0;
    errpass_count = 0;
    errfail_count = 0;

    @(posedge nRST_r);
    @(posedge pCLK_r);

    $display("\n====================");
    $display("  FFRAM02 RTL Test (FI)");
    $display("====================\n");

    // -----------------------------------------------------------------
    // Phase 1: Normal write all
    // -----------------------------------------------------------------
    $display("---- Phase 1: Normal Write All ----");
    for (i = 0; i < `WORD; i = i + 1)
        write_data(input_addr[i], input_data[i], 1'b0);
    $display("");

    // -----------------------------------------------------------------
    // Phase 2: Normal read all (expect no error)
    // -----------------------------------------------------------------
    $display("---- Phase 2: Normal Read All (No Error) ----");
    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b0, rdata, rerr);
        check_no_error(input_addr[i], rdata, rerr);
    end
    $display("");

    // -----------------------------------------------------------------
    // Phase 3: Read Disturb (FI on read, expect corrected + ERR=1)
    //   - We assert pFS during ALL reads; only masked addresses inject.
    // -----------------------------------------------------------------
    $display("---- Phase 3: Read Disturb (Expect Corrected + ERR=1 on masked addrs) ----");
    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b1, rdata, rerr);
        if (TB_RD_WORD_MASK[input_addr[i]])
            check_expect_err_and_correct(input_addr[i], rdata, rerr);
        else
            check_no_error(input_addr[i], rdata, rerr);
    end
    $display("");

    // -----------------------------------------------------------------
    // Phase 4: Write Failure (FI on write)
    //   - We assert pFS during ALL writes; only masked addresses corrupt.
    //   - Then read back with pFS=0 and only check ERR=1 on masked addrs.
    // -----------------------------------------------------------------
    tb_pulse_reset();  // reset

    $display("---- Phase 4: Write Failure (Expect ERR=1 on masked addrs) ----");
    for (i = 0; i < `WORD; i = i + 1)
        write_data(input_addr[i], input_data[i], 1'b1);

    for (i = 0; i < `WORD; i = i + 1)
    begin
        read_data(input_addr[i], 1'b0, rdata, rerr);
        if (TB_WF_WORD_MASK[input_addr[i]])
            check_expect_err_only(input_addr[i], rdata, rerr);
        else
            check_no_error(input_addr[i], rdata, rerr);
    end

    // Summary
    $display("\n========================================");
    $display("            Test Summary (FI)");
    $display("========================================");
    $display("  Pass (no-error)        : %0d", pass_count);
    $display("  Fail (no-error)        : %0d", fail_count);
    $display("  Pass (expect error)    : %0d", errpass_count);
    $display("  Fail (expect error)    : %0d", errfail_count);
    $display("----------------------------------------");
    if ((fail_count == 0) && (errfail_count == 0))
        $display("  Result                 : ALL PASSED");
    else
        $display("  Result                 : FAILED");
    $display("========================================\n");

    $finish;
end

//==== Waveform Output ====//
initial
begin
    $dumpfile("epl_ffram02_rtl.vcd");
    $dumpvars(0, epl_testbench_rtl_fi);

`ifdef USE_FSDB
`ifdef RTL_SIMULATION
    $fsdbDumpfile("epl_ffram02_rtl.fsdb");
`elsif POST_SIMULATION
    $fsdbDumpfile("epl_ffram02_post.fsdb");
`else
    $fsdbDumpfile("epl_ffram02_default.fsdb");
`endif
    $fsdbDumpvars(0, epl_testbench_rtl_fi);
`endif
end

//==== SDF Annotation (Post-Simulation) ====//
`ifdef POST_SIMULATION
initial
begin
    $sdf_annotate("chip_syn.sdf", uut);
end
`endif

endmodule













