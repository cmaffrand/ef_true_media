-------------------------------------------------------------------------------
-- tb_pipeline_reg_sl.vhd
-- Self-checking testbench for pipeline_reg_sl (single-bit version).
--
-- Tested configurations:
--   1. NUM_STAGES = 1 - basic single-stage operation
--   2. NUM_STAGES = 4 - multi-stage latency verification
--   3. NUM_STAGES = 0 - pass-through (combinational)
--   4. Clock-enable hold behaviour
--   5. Synchronous reset with RESET_VALUE = '1'
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

    ---------------------------------------------------------------------------
    -- Configuration 4: 2 stages, RESET_VALUE = '1'
    ---------------------------------------------------------------------------
    signal clk_r1   : std_logic := '0';
    signal rst_n_r1 : std_logic := '0';
    signal en_r1    : std_logic := '1';
    signal d_r1     : std_logic := '0';
    signal q_r1     : std_logic;

    signal test_done : boolean := false;

begin

    ---------------------------------------------------------------------------
    -- Clocks
    ---------------------------------------------------------------------------
    clk_1   <= not clk_1   after CLK_PERIOD / 2 when not test_done else '0';
    clk_4   <= not clk_4   after CLK_PERIOD / 2 when not test_done else '0';
    clk_r1  <= not clk_r1  after CLK_PERIOD / 2 when not test_done else '0';

    ---------------------------------------------------------------------------
    -- DUT instances
    ---------------------------------------------------------------------------

    -- 1-stage
    dut_1st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 1, RESET_VALUE => '0')
        port map (clk => clk_1, rst_n => rst_n_1, en => en_1, d => d_1, q => q_1);

    -- 4-stage
    dut_4st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 4, RESET_VALUE => '0')
        port map (clk => clk_4, rst_n => rst_n_4, en => en_4, d => d_4, q => q_4);

    -- 0-stage pass-through
    dut_0st : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 0, RESET_VALUE => '0')
        port map (clk => '0', rst_n => '1', en => '1', d => d_0, q => q_0);

    -- 2-stage, reset-to-one
    dut_rst1 : entity work.pipeline_reg_sl
        generic map (NUM_STAGES => 2, RESET_VALUE => '1')
        port map (clk => clk_r1, rst_n => rst_n_r1, en => en_r1, d => d_r1, q => q_r1);

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
        -- Test 5: RESET_VALUE = '1' → output is '1' after reset
        -- ----------------------------------------------------------------
        rst_n_r1 <= '0';
        d_r1     <= '0';
        wait_clk(clk_r1, 2);
        check(q_r1, '1', "T5 - reset_value='1', q='1' during reset");
        rst_n_r1 <= '1';

        -- After reset release, '0' should propagate through 2 stages
        wait_clk(clk_r1, 2);
        check(q_r1, '0', "T5 - reset released, '0' propagated");

        -- ----------------------------------------------------------------
        -- Done
        -- ----------------------------------------------------------------
        report "tb_pipeline_reg_sl: All tests PASSED." severity note;
        test_done <= true;
        wait;

    end process stim;

end architecture sim;
