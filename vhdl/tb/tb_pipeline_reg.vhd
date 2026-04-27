-------------------------------------------------------------------------------
-- tb_pipeline_reg.vhd
-- Self-checking testbench for pipeline_reg.
--
-- Tested configurations:
--   1. NUM_STAGES = 1, DATA_WIDTH = 8   - basic single-stage operation
--   2. NUM_STAGES = 3, DATA_WIDTH = 16  - multi-stage latency check
--   3. NUM_STAGES = 0, DATA_WIDTH = 8   - pass-through (zero stages)
--   4. Clock-enable behaviour (en = '0' holds the pipeline)
--   5. Synchronous reset clears all stages
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_pipeline_reg is
end entity tb_pipeline_reg;

architecture sim of tb_pipeline_reg is

    ---------------------------------------------------------------------------
    -- Constants
    ---------------------------------------------------------------------------
    constant CLK_PERIOD : time := 10 ns;

    ---------------------------------------------------------------------------
    -- DUT signals - configuration 1 (1 stage, 8 bit)
    ---------------------------------------------------------------------------
    signal clk_s1   : std_logic := '0';
    signal rst_n_s1 : std_logic := '0';
    signal en_s1    : std_logic := '1';
    signal d_s1     : std_logic_vector(7 downto 0) := (others => '0');
    signal q_s1     : std_logic_vector(7 downto 0);

    ---------------------------------------------------------------------------
    -- DUT signals - configuration 2 (3 stages, 16 bit)
    ---------------------------------------------------------------------------
    signal clk_s3   : std_logic := '0';
    signal rst_n_s3 : std_logic := '0';
    signal en_s3    : std_logic := '1';
    signal d_s3     : std_logic_vector(15 downto 0) := (others => '0');
    signal q_s3     : std_logic_vector(15 downto 0);

    ---------------------------------------------------------------------------
    -- DUT signals - configuration 3 (0 stages, 8 bit  → pass-through)
    ---------------------------------------------------------------------------
    signal d_s0 : std_logic_vector(7 downto 0) := (others => '0');
    signal q_s0 : std_logic_vector(7 downto 0);

    ---------------------------------------------------------------------------
    -- Shared test state
    ---------------------------------------------------------------------------
    signal test_done : boolean := false;

begin

    ---------------------------------------------------------------------------
    -- Clock generation
    ---------------------------------------------------------------------------
    clk_s1 <= not clk_s1 after CLK_PERIOD / 2 when not test_done else '0';
    clk_s3 <= not clk_s3 after CLK_PERIOD / 2 when not test_done else '0';

    ---------------------------------------------------------------------------
    -- DUT instantiations
    ---------------------------------------------------------------------------

    -- Configuration 1: 1 stage, 8-bit
    dut_1stage : entity work.pipeline_reg
        generic map (
            DATA_WIDTH  => 8,
            NUM_STAGES  => 1
        )
        port map (
            sys_clk_i  => clk_s1,
            sys_rstn_i => rst_n_s1,
            enable_i   => en_s1,
            datain_i   => d_s1,
            dataout_o  => q_s1
        );

    -- Configuration 2: 3 stages, 16-bit
    dut_3stage : entity work.pipeline_reg
        generic map (
            DATA_WIDTH  => 16,
            NUM_STAGES  => 3
        )
        port map (
            sys_clk_i  => clk_s3,
            sys_rstn_i => rst_n_s3,
            enable_i   => en_s3,
            datain_i   => d_s3,
            dataout_o  => q_s3
        );

    -- Configuration 3: 0 stages (pass-through)
    dut_0stage : entity work.pipeline_reg
        generic map (
            DATA_WIDTH  => 8,
            NUM_STAGES  => 0
        )
        port map (
            sys_clk_i  => '0',
            sys_rstn_i => '1',
            enable_i   => '1',
            datain_i   => d_s0,
            dataout_o  => q_s0
        );

    ---------------------------------------------------------------------------
    -- Stimulus and checking process
    ---------------------------------------------------------------------------
    stim_proc : process is

        -- Helper: wait for N rising edges then pause 1 ns so that all
        -- delta-cycles triggered by the clock edge (DUT flip-flop updates)
        -- have time to propagate before the caller reads any signal.
        procedure wait_clk(signal c : in std_logic; n : positive := 1) is
        begin
            for i in 1 to n loop
                wait until rising_edge(c);
            end loop;
            wait for 1 ns;
        end procedure;

        procedure check_eq(
            actual   : std_logic_vector;
            expected : std_logic_vector;
            msg      : string
        ) is
        begin
            assert actual = expected
                report "FAIL - " & msg &
                       ": expected 0x" & to_hstring(expected) &
                       " got 0x"      & to_hstring(actual)
                severity failure;
        end procedure;

    begin

        -- ----------------------------------------------------------------
        -- Test 1: Single-stage pipeline, basic latency
        -- ----------------------------------------------------------------
        rst_n_s1 <= '0';
        d_s1     <= x"00";
        wait_clk(clk_s1, 2);
        rst_n_s1 <= '1';

        -- Apply value 0xAB, expect it at q after 1 clock
        d_s1 <= x"AB";
        wait_clk(clk_s1);
        check_eq(q_s1, x"AB", "Test1 - 1-stage, q after 1 clk");

        -- Apply value 0xCD
        d_s1 <= x"CD";
        wait_clk(clk_s1);
        check_eq(q_s1, x"CD", "Test1 - 1-stage, 2nd sample");

        -- ----------------------------------------------------------------
        -- Test 2: Clock-enable hold behaviour (single-stage)
        -- ----------------------------------------------------------------
        d_s1  <= x"FF";
        en_s1 <= '0';           -- disable clock enable
        wait_clk(clk_s1, 3);
        -- q should still be 0xCD (last captured value)
        check_eq(q_s1, x"CD", "Test2 - CE=0, output held");

        en_s1 <= '1';
        wait_clk(clk_s1);
        check_eq(q_s1, x"FF", "Test2 - CE restored, 0xFF captured");

        -- ----------------------------------------------------------------
        -- Test 3: Synchronous reset clears output (single-stage)
        -- ----------------------------------------------------------------
        d_s1     <= x"AA";
        wait_clk(clk_s1);
        rst_n_s1 <= '0';        -- apply reset
        wait_clk(clk_s1);
        check_eq(q_s1, x"00", "Test3 - sync reset, output cleared");
        rst_n_s1 <= '1';

        -- ----------------------------------------------------------------
        -- Test 4: Three-stage pipeline latency
        -- ----------------------------------------------------------------
        rst_n_s3 <= '0';
        d_s3     <= x"0000";
        wait_clk(clk_s3, 2);
        rst_n_s3 <= '1';

        -- Push 0x1234 into the pipeline
        d_s3 <= x"1234";
        wait_clk(clk_s3);

        -- After 1 clock the value is still in transit
        check_eq(q_s3, x"0000", "Test4 - 3-stage, after 1 clk (not yet)");

        wait_clk(clk_s3);
        check_eq(q_s3, x"0000", "Test4 - 3-stage, after 2 clk (not yet)");

        wait_clk(clk_s3);
        check_eq(q_s3, x"1234", "Test4 - 3-stage, after 3 clk (expected)");

        -- Push a second value and make sure it follows 3 cycles later
        d_s3 <= x"BEEF";
        wait_clk(clk_s3, 3);
        check_eq(q_s3, x"BEEF", "Test4 - 3-stage, second value");

        -- ----------------------------------------------------------------
        -- Test 5: Pass-through (zero stages) - combinational
        -- ----------------------------------------------------------------
        d_s0 <= x"5A";
        wait for 1 ns;          -- allow delta-cycles to settle
        check_eq(q_s0, x"5A", "Test5 - 0-stage, pass-through 0x5A");

        d_s0 <= x"A5";
        wait for 1 ns;
        check_eq(q_s0, x"A5", "Test5 - 0-stage, pass-through 0xA5");

        -- ----------------------------------------------------------------
        -- All tests passed
        -- ----------------------------------------------------------------
        report "tb_pipeline_reg: All tests PASSED." severity note;
        test_done <= true;
        wait;

    end process stim_proc;

end architecture sim;
