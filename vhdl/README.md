# Retiming VHDL Library

This directory contains a VHDL library of configurable pipeline (retiming)
registers and utility components, implemented in **VHDL-2008**.

## Directory layout

```
vhdl/
├── rtl/                        RTL source files
│   ├── retiming_pkg.vhd        Common types and utility functions
│   ├── pipeline_reg.vhd        Generic pipeline register (std_logic_vector)
│   └── pipeline_reg_sl.vhd     Single-bit pipeline register (std_logic)
└── tb/                         Testbenches
    ├── tb_pipeline_reg.vhd     Testbench for pipeline_reg
    └── tb_pipeline_reg_sl.vhd  Testbench for pipeline_reg_sl
```

---

## Components

### `retiming_pkg`

A shared package that provides:

| Symbol | Description |
|---|---|
| `slv_array_t` | Unconstrained array of `std_logic_vector` |
| `sl_array_t`  | Unconstrained array of `std_logic` |
| `log2_ceil(n)` | Returns ⌈log₂(n)⌉ |
| `max(a, b)` | Returns the larger of two naturals |
| `min(a, b)` | Returns the smaller of two naturals |

### `pipeline_reg` — Multi-bit pipeline register

| Generic | Type | Default | Description |
|---|---|---|---|
| `DATA_WIDTH` | `positive` | `8` | Width of the data bus in bits |
| `NUM_STAGES` | `natural` | `1` | Number of pipeline stages (0 = pass-through) |
| `RST_POLARITY` | `std_logic` | `'0'` | Active level of `sys_rstn_i` that triggers reset (`'0'` = active-low, `'1'` = active-high) |

| Port | Direction | Width | Description |
|---|---|---|---|
| `sys_clk_i` | in | 1 | Clock (rising-edge triggered) |
| `sys_rstn_i` | in | 1 | Synchronous reset (polarity set by `RST_POLARITY`, default active-low) |
| `enable_i` | in | 1 | Clock enable (`'0'` holds the pipeline) |
| `datain_i` | in | `DATA_WIDTH` | Data input |
| `dataout_o` | out | `DATA_WIDTH` | Data output (delayed by `NUM_STAGES` clock cycles) |

**Instantiation example (3-stage, 16-bit):**

```vhdl
u_pipe : entity work.pipeline_reg
  generic map (
    DATA_WIDTH => 16,
    NUM_STAGES => 3
  )
  port map (
    sys_clk_i  => clk,
    sys_rstn_i => rst_n,
    enable_i   => '1',
    datain_i   => data_in,
    dataout_o  => data_out
  );
```

### `pipeline_reg_sl` — Single-bit pipeline register

Same behaviour as `pipeline_reg` but for `std_logic` control signals (e.g.
`valid`, `start`, `done` flags).

| Generic | Type | Default | Description |
|---|---|---|---|
| `NUM_STAGES` | `natural` | `1` | Number of pipeline stages (0 = pass-through) |
| `RST_POLARITY` | `std_logic` | `'0'` | Active level of `sys_rstn_i` that triggers reset (`'0'` = active-low, `'1'` = active-high) |

| Port | Direction | Description |
|---|---|---|
| `sys_clk_i` | in | Clock (rising-edge triggered) |
| `sys_rstn_i` | in | Synchronous reset (polarity set by `RST_POLARITY`, default active-low) |
| `enable_i` | in | Clock enable |
| `datain_i` | in | Single-bit input |
| `dataout_o` | out | Single-bit output (delayed by `NUM_STAGES` cycles) |

**Instantiation example (2-stage valid-flag delay):**

```vhdl
u_valid_pipe : entity work.pipeline_reg_sl
  generic map (NUM_STAGES => 2)
  port map (
    sys_clk_i  => clk,
    sys_rstn_i => rst_n,
    enable_i   => '1',
    datain_i   => valid_in,
    dataout_o  => valid_out
  );
```

---

## Retiming overview

**Retiming** is a sequential optimization technique that moves registers
across combinational logic to balance pipeline stage delays and improve the
maximum operating frequency (Fmax) without changing the circuit's overall
input/output behaviour.

Most modern synthesis tools (Vivado, Quartus, Design Compiler, etc.) support
automatic retiming. To enable it, instantiate one or more `pipeline_reg` /
`pipeline_reg_sl` stages around timing-critical combinational paths and turn
on the retiming option in your synthesis settings.

Key synthesis pragmas for common tools:

| Tool | Pragma / attribute |
|---|---|
| Vivado | `set_property RETIMING true [get_cells ...]` or `-retiming` in `synth_design` |
| Quartus | `set_instance_assignment -name AUTO_SHIFT_REGISTER_RECOGNITION OFF` (disable SRL mapping) + Enable Fitter retiming |
| Design Compiler | `set_optimize_registers true -design ...` |

---

## Simulation

The testbenches are self-checking: they use VHDL `assert` statements with
`severity failure` to report mismatches and print a final PASSED message on
success.

### Running with GHDL

```bash
# From the vhdl/ directory:

# 1. Analyse sources (compile order matters)
ghdl -a --std=08 rtl/retiming_pkg.vhd
ghdl -a --std=08 rtl/pipeline_reg.vhd
ghdl -a --std=08 rtl/pipeline_reg_sl.vhd

# 2. Analyse testbenches
ghdl -a --std=08 tb/tb_pipeline_reg.vhd
ghdl -a --std=08 tb/tb_pipeline_reg_sl.vhd

# 3. Elaborate and run
ghdl -e --std=08 tb_pipeline_reg
ghdl -r --std=08 tb_pipeline_reg

ghdl -e --std=08 tb_pipeline_reg_sl
ghdl -r --std=08 tb_pipeline_reg_sl
```

### Running with ModelSim / QuestaSim

```tcl
vcom -2008 rtl/retiming_pkg.vhd
vcom -2008 rtl/pipeline_reg.vhd
vcom -2008 rtl/pipeline_reg_sl.vhd
vcom -2008 tb/tb_pipeline_reg.vhd
vcom -2008 tb/tb_pipeline_reg_sl.vhd

vsim -c tb_pipeline_reg    -do "run -all; quit"
vsim -c tb_pipeline_reg_sl -do "run -all; quit"
```

---

## Synthesis notes

* `NUM_STAGES = 0` generates a pure combinational pass-through — no flip-flops
  are inferred. This is useful to keep the same instantiation template
  throughout a design while toggling retiming on or off via a top-level generic
  or a configuration constant.
* The `enable_i` (clock-enable) port maps directly to the CE pin of target
  flip-flops, enabling efficient power gating on FPGAs without additional
  logic.
* `RST_POLARITY` selects whether `sys_rstn_i` is active-low (`'0'`, default)
  or active-high (`'1'`), avoiding the need to invert the reset signal outside
  the component.
