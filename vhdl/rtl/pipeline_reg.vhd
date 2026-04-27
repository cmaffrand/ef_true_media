-------------------------------------------------------------------------------
-- pipeline_reg.vhd
-- Generic pipeline register (retiming register) for std_logic_vector signals.
--
-- Generics
--   DATA_WIDTH  : Width of the data bus (bits).  Default = 8.
--   NUM_STAGES  : Number of pipeline / retiming stages.  Default = 1.
--                 When set to 0 the input is passed straight through to the
--                 output with no registers (combinational path).
--   RESET_VALUE : Value applied to every bit of every stage on reset.
--                 '0' (default) → reset to all-zeros.
--                 '1'           → reset to all-ones.
--
-- Ports
--   clk   : Clock input (rising-edge triggered).
--   rst_n : Active-low synchronous reset.
--   en    : Clock enable.  When '0' the pipeline holds its current value.
--   d     : Data input  (DATA_WIDTH bits).
--   q     : Data output (DATA_WIDTH bits), delayed by NUM_STAGES clock cycles.
--
-- Usage example (three-stage retiming register, 16 bits wide):
--
--   u_pipe : entity work.pipeline_reg
--     generic map (
--       DATA_WIDTH => 16,
--       NUM_STAGES => 3
--     )
--     port map (
--       clk   => clk,
--       rst_n => rst_n,
--       en    => '1',
--       d     => data_in,
--       q     => data_out
--     );
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity pipeline_reg is
    generic (
        DATA_WIDTH  : positive  := 8;
        NUM_STAGES  : natural   := 1;
        RESET_VALUE : std_logic := '0'
    );
    port (
        clk   : in  std_logic;
        rst_n : in  std_logic;
        en    : in  std_logic;
        d     : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        q     : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end entity pipeline_reg;

architecture rtl of pipeline_reg is

    -- Internal shift register: index 0 is closest to the input,
    -- index NUM_STAGES-1 is the output stage.
    type pipe_t is array (0 to NUM_STAGES - 1)
        of std_logic_vector(DATA_WIDTH - 1 downto 0);

    signal pipe : pipe_t := (others => (others => RESET_VALUE));

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
                    -- Synchronous reset: clear all stages
                    pipe <= (others => (others => RESET_VALUE));
                elsif en = '1' then
                    -- Shift data through the pipeline
                    pipe(0) <= d;
                    for i in 1 to NUM_STAGES - 1 loop
                        pipe(i) <= pipe(i - 1);
                    end loop;
                end if;
            end if;
        end process;

        -- Connect the last stage to the output
        q <= pipe(NUM_STAGES - 1);

    end generate gen_pipeline;

end architecture rtl;
