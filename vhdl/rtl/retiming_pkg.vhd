-------------------------------------------------------------------------------
-- retiming_pkg.vhd
-- Package for the Retiming VHDL Library.
--
-- Provides common array types and utility functions used by the retiming
-- components (pipeline_reg, pipeline_reg_sl, etc.).
--
-- VHDL standard: VHDL-2008
-------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

package retiming_pkg is

    ---------------------------------------------------------------------------
    -- Array types
    ---------------------------------------------------------------------------

    -- Unconstrained array of std_logic_vector (requires VHDL-2008).
    -- Each element is a std_logic_vector whose width is determined at the
    -- instantiation point.
    type slv_array_t is array (natural range <>) of std_logic_vector;

    -- Unconstrained array of std_logic (one-dimensional shift register).
    type sl_array_t is array (natural range <>) of std_logic;

    ---------------------------------------------------------------------------
    -- Utility functions
    ---------------------------------------------------------------------------

    -- Returns ceil(log2(n)).  Useful for computing address-bus widths.
    -- log2_ceil(1) = 0, log2_ceil(2) = 1, log2_ceil(3) = 2, …
    function log2_ceil(n : positive) return natural;

    -- Returns the maximum of two naturals.
    function max(a, b : natural) return natural;

    -- Returns the minimum of two naturals.
    function min(a, b : natural) return natural;

end package retiming_pkg;

-------------------------------------------------------------------------------
-- Package body
-------------------------------------------------------------------------------
package body retiming_pkg is

    function log2_ceil(n : positive) return natural is
        variable result : natural := 0;
        variable value  : positive := 1;
    begin
        while value < n loop
            value  := value * 2;
            result := result + 1;
        end loop;
        return result;
    end function log2_ceil;

    function max(a, b : natural) return natural is
    begin
        if a >= b then
            return a;
        else
            return b;
        end if;
    end function max;

    function min(a, b : natural) return natural is
    begin
        if a <= b then
            return a;
        else
            return b;
        end if;
    end function min;

end package body retiming_pkg;
