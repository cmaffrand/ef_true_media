-------------------------------------------------------------------------------
-- tb_pipeline_reg_sl.vhd
-- Self-checking testbench for pipeline_reg_sl (single-bit version).
--
-- Tested configurations:
--   1. NUM_STAGES = 1 - basic single-stage operation
--   2. NUM_STAGES = 4 - multi-stage latency verification
--   3. NUM_STAGES = 0 - pass-through (combinational)
--   4. Clock-enable hold behaviour
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity tb_pipeline_reg_sl is
end entity tb_pipeline_reg_sl;

architecture sim of tb_pipeline_reg_sl is

    constant CLK_PERIOD : time := 10 ns;

    ---------------------------------------------------------------------------
    -- Configuration 1: 1 stage
    ---------------------------------------------------------------------------
    signal clk_1   : std_logic := '0';
    signal rst_n_1 : std_logic := '0';
    signal en_1    : std_logic := '1';
    signal d_1     : std_logic := '0';
    signal q_1     : std_logic;

    ---------------------------------------------------------------------------
    -- Configuration 2: 4 stages
    ---------------------------------------------------------------------------
    signal clk_4   : std_logic := '0';
    signal rst_n_4 : std_logic := '0';
    signal en_4    : std_logic := '1';
    signal d_4     : std_logic := '0';
    signal q_4     : std_logic;

    ---------------------------------------------------------------------------
    -- Configuration 3: 0 stages (pass-through)
    ---------------------------------------------------------------------------
    signal d_0 : std_logic := '0';
    signal q_0 : std_logic;

    signal test_done : boolean := false;

begin

    ---------------------------------------------------------------------------
    -- Clocks
    ---------------------------------------------------------------------------
    clk_1   <= not clk_1   after CLK_PERIOD / 2 when not test_done else '0';
    clk_4   <= not clk_4   after CLK_PERIOD / 2 when not test_done else '0';

    ---------------------------------------------------------------------------
    -- DUT instances
    ---------------------------------------------------------------------------

    -- 1-stage
    dut_1st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 1)
        port map (sys_clk_i => clk_1, sys_rstn_i => rst_n_1, enable_i => en_1, datain_i => d_1, dataout_o => q_1);

    -- 4-stage
    dut_4st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 4)
        port map (sys_clk_i => clk_4, sys_rstn_i => rst_n_4, enable_i => en_4, datain_i => d_4, dataout_o => q_4);

    -- 0-stage pass-through
    dut_0st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 0)
        port map (sys_clk_i => '0', sys_rstn_i => '1', enable_i => '1', datain_i => d_0, dataout_o => q_0);

    ---------------------------------------------------------------------------
    -- Stimulus & checking
    ---------------------------------------------------------------------------
    stim : process is

        procedure wait_clk(signal c : in std_logic; n : positive := 1) is
        begin
            for i in 1 to n loop
                wait until rising_edge(c);
            end loop;
            wait for 1 ns;
        end procedure;

        procedure check(actual, expected : std_logic; msg : string) is
        begin
            assert actual = expected
                report "FAIL - " & msg &
                       ": expected " & std_logic'image(expected) &
                       " got "       & std_logic'image(actual)
                severity failure;
        end procedure;

    begin

        -- ----------------------------------------------------------------
        -- Test 1: 1-stage latency
        -- ----------------------------------------------------------------
        rst_n_1 <= '0';
        wait_clk(clk_1, 2);
        rst_n_1 <= '1';

        d_1 <= '1';
        wait_clk(clk_1);
        check(q_1, '1', "T1 - 1-stage, q after 1 clk");

        d_1 <= '0';
        wait_clk(clk_1);
        check(q_1, '0', "T1 - 1-stage, q toggled back");

        -- ----------------------------------------------------------------
        -- Test 2: Clock-enable hold on 1-stage
        -- ----------------------------------------------------------------
        d_1  <= '1';
        en_1 <= '0';
        wait_clk(clk_1, 3);
        check(q_1, '0', "T2 - CE=0, output holds previous ('0')");

        en_1 <= '1';
        wait_clk(clk_1);
        check(q_1, '1', "T2 - CE=1, '1' captured");

        -- ----------------------------------------------------------------
        -- Test 3: 4-stage latency
        -- ----------------------------------------------------------------
        rst_n_4 <= '0';
        wait_clk(clk_4, 2);
        rst_n_4 <= '1';

        d_4 <= '1';
        wait_clk(clk_4, 1); check(q_4, '0', "T3 - 4-stage, clk1 (not yet)");
        wait_clk(clk_4, 1); check(q_4, '0', "T3 - 4-stage, clk2 (not yet)");
        wait_clk(clk_4, 1); check(q_4, '0', "T3 - 4-stage, clk3 (not yet)");
        wait_clk(clk_4, 1); check(q_4, '1', "T3 - 4-stage, clk4 (arrived)");

        -- ----------------------------------------------------------------
        -- Test 4: 0-stage pass-through
        -- ----------------------------------------------------------------
        d_0 <= '1';
        wait for 1 ns;
        check(q_0, '1', "T4 - pass-through '1'");

        d_0 <= '0';
        wait for 1 ns;
        check(q_0, '0', "T4 - pass-through '0'");

        -- ----------------------------------------------------------------
        -- Done
        -- ----------------------------------------------------------------
        report "tb_pipeline_reg_sl: All tests PASSED." severity note;
        test_done <= true;
        wait;

    end process stim;

end architecture sim;
