-------------------------------------------------------------------------------
-- pipeline_reg_sl.vhd
-- Generic pipeline register (retiming register) for std_logic (single-bit)
-- signals such as control or valid flags.
--
-- Generics
--   NUM_STAGES  : Number of pipeline / retiming stages.  Default = 1.
--                 When set to 0 the input is passed straight through to the
--                 output with no registers (combinational path).
--   RESET_VALUE : Value driven on every stage when the reset is active.
--                 '0' (default) → reset to low.
--                 '1'           → reset to high.
--
-- Ports
--   clk   : Clock input (rising-edge triggered).
--   rst_n : Active-low synchronous reset.
--   en    : Clock enable.  When '0' the pipeline holds its current value.
--   d     : Single-bit data input.
--   q     : Single-bit data output, delayed by NUM_STAGES clock cycles.
--
-- Usage example (two-stage retiming for a valid flag):
--
--   u_pipe_sl : entity work.pipeline_reg_sl
--     generic map (
--       NUM_STAGES  => 2,
--       RESET_VALUE => '0'
--     )
--     port map (
--       clk   => clk,
--       rst_n => rst_n,
--       en    => '1',
--       d     => valid_in,
--       q     => valid_out
--     );
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity pipeline_reg_sl is
    generic (
        NUM_STAGES  : natural   := 1;
        RESET_VALUE : std_logic := '0'
    );
    port (
        clk   : in  std_logic;
        rst_n : in  std_logic;
        en    : in  std_logic;
        d     : in  std_logic;
        q     : out std_logic
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
        q <= d;
    end generate gen_passthrough;

    ---------------------------------------------------------------------------
    -- One or more pipeline stages
    ---------------------------------------------------------------------------
    gen_pipeline : if NUM_STAGES > 0 generate

        process(clk) is
        begin
            if rising_edge(clk) then
                if rst_n = '0' then
                    pipe <= (others => RESET_VALUE);
                elsif en = '1' then
                    pipe(0) <= d;
                    for i in 1 to NUM_STAGES - 1 loop
                        pipe(i) <= pipe(i - 1);
                    end loop;
                end if;
            end if;
        end process;

        q <= pipe(NUM_STAGES - 1);

    end generate gen_pipeline;

end architecture rtl;
