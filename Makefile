TB   = epl_testbench_rtl_fi
OUT  = sim.out

SRCS = \
  epl_testbench_rtl_fi.v \
  epl_FFRAM02_top_fi.v \
  epl_Column_Access_sub.v epl_Column_Decode_sub.v epl_Control_Circuit_sub.v \
  epl_Ffbit_n_sub.v epl_FiRdDist_sub.v epl_FiWrFail_sub.v \
  epl_Memory_Array_sub.v epl_Read_Mux_sub.v epl_Row_Decode_sub.v epl_Row_Selection_sub.v \
  epl_ecc_encoder.v epl_ecc_decoder.v


all: run

build:
	iverilog -g2012 -I . -o $(OUT) $(EPL_DEFS) $(SRCS)

run: build
	vvp $(OUT)

clean:
	rm -f $(OUT) *.vcd *.fst *.fsdb pattern.avc
