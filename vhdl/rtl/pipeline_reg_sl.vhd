-------------------------------------------------------------------------------
-- pipeline_reg_sl.vhd
-- Generic pipeline register (retiming register) for std_logic (single-bit)
-- signals such as control or valid flags.
--
-- Generics
--   NUM_STAGES   : Number of pipeline / retiming stages.  Default = 1.
--                  When set to 0 the input is passed straight through to the
--                  output with no registers (combinational path).
--   RESET_VALUE  : Value driven on every stage when the reset is active.
--                  '0' (default) -> reset to low.
--                  '1'           -> reset to high.
--   RST_POLARITY : Active level of sys_rstn_i that triggers the reset.
--                  '0' (default) -> active-low reset (negated reset, sys_rstn_i = '0' resets).
--                  '1'           -> active-high reset (sys_rstn_i = '1' resets).
--
-- Ports
--   sys_clk_i  : Clock input (rising-edge triggered).
--   sys_rstn_i : Synchronous reset (polarity set by RST_POLARITY, default active-low).
--   enable_i   : Clock enable.  When '0' the pipeline holds its current value.
--   datain_i   : Single-bit data input.
--   dataout_o  : Single-bit data output, delayed by NUM_STAGES clock cycles.
--
-- Usage example (two-stage retiming for a valid flag):
--
--   u_pipe_sl : entity work.pipeline_reg_sl
--     generic map (
--       NUM_STAGES  => 2,
--       RESET_VALUE => '0'
--     )
--     port map (
--       sys_clk_i  => clk,
--       sys_rstn_i => rst_n,
--       enable_i   => '1',
--       datain_i   => valid_in,
--       dataout_o  => valid_out
--     );
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity pipeline_reg_sl is
    generic (
        NUM_STAGES   : natural   := 1;
        RESET_VALUE  : std_logic := '0';
        RST_POLARITY : std_logic := '0'
    );
    port (
        sys_clk_i  : in  std_logic;
        sys_rstn_i : in  std_logic;
        enable_i   : in  std_logic;
        datain_i   : in  std_logic;
        dataout_o  : out std_logic
    );
end entity pipeline_reg_sl;

architecture rtl of pipeline_reg_sl is

    -- Shift-register array: index 0 is closest to the input.
    type pipe_t is array (0 to NUM_STAGES - 1) of std_logic;

    signal pipe : pipe_t := (others => RESET_VALUE);

begin

    ---------------------------------------------------------------------------
    -- Zero-stage pass-through (combinational)
    ---------------------------------------------------------------------------
    gen_passthrough : if NUM_STAGES = 0 generate
        dataout_o <= datain_i;
    end generate gen_passthrough;

    ---------------------------------------------------------------------------
    -- One or more pipeline stages
    ---------------------------------------------------------------------------
    gen_pipeline : if NUM_STAGES > 0 generate

        process(sys_clk_i) is
        begin
            if rising_edge(sys_clk_i) then
                if sys_rstn_i = RST_POLARITY then
                    pipe <= (others => RESET_VALUE);
                elsif enable_i = '1' then
                    pipe(0) <= datain_i;
                    for i in 1 to NUM_STAGES - 1 loop
                        pipe(i) <= pipe(i - 1);
                    end loop;
                end if;
            end if;
        end process;

        dataout_o <= pipe(NUM_STAGES - 1);

    end generate gen_pipeline;

end architecture rtl;
