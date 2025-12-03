"""Tests for the spec system."""

import pytest
from texer.specs import Ref, Iter, Format, FormatNumber, Cond, Literal, Raw, Join, Call


class TestRef:
    def test_simple_path(self):
        data = {"name": "Alice"}
        assert Ref("name").resolve(data) == "Alice"

    def test_nested_path(self):
        data = {"user": {"email": "alice@example.com"}}
        assert Ref("user.email").resolve(data) == "alice@example.com"

    def test_list_index(self):
        data = {"items": [{"value": 10}, {"value": 20}]}
        assert Ref("items.0.value").resolve(data) == 10
        assert Ref("items.1.value").resolve(data) == 20

    def test_default_value(self):
        data = {"name": "Alice"}
        assert Ref("missing", default="N/A").resolve(data) == "N/A"

    def test_scope_override(self):
        data = {"name": "Alice"}
        scope = {"name": "Bob"}
        assert Ref("name").resolve(data, scope) == "Bob"


class TestComparisons:
    def test_greater_than(self):
        data = {"x": 10}
        assert (Ref("x") > 5).resolve(data) is True
        assert (Ref("x") > 15).resolve(data) is False

    def test_less_than(self):
        data = {"x": 10}
        assert (Ref("x") < 15).resolve(data) is True
        assert (Ref("x") < 5).resolve(data) is False

    def test_equals(self):
        data = {"status": "active"}
        assert (Ref("status") == "active").resolve(data) is True
        assert (Ref("status") == "inactive").resolve(data) is False

    def test_and_or(self):
        data = {"x": 10, "y": 5}
        assert ((Ref("x") > 5) & (Ref("y") < 10)).resolve(data) is True
        assert ((Ref("x") > 15) | (Ref("y") < 10)).resolve(data) is True


class TestIter:
    def test_iter_with_template(self):
        data = {"items": [{"name": "a"}, {"name": "b"}]}
        result = Iter(Ref("items"), template=Ref("name")).resolve(data)
        assert result == ["a", "b"]

    def test_iter_coordinates(self):
        data = {"points": [{"x": 0, "y": 1}, {"x": 1, "y": 2}]}
        result = Iter(Ref("points"), x=Ref("x"), y=Ref("y")).resolve(data)
        assert result == [(0, 1), (1, 2)]

    def test_iter_3d_coordinates(self):
        data = {"points": [{"x": 0, "y": 1, "z": 2}]}
        result = Iter(Ref("points"), x=Ref("x"), y=Ref("y"), z=Ref("z")).resolve(data)
        assert result == [(0, 1, 2)]


class TestFormat:
    def test_float_format(self):
        data = {"value": 3.14159}
        assert Format(Ref("value"), ".2f").resolve(data) == "3.14"

    def test_percentage_format(self):
        data = {"pct": 0.256}
        # % is escaped for LaTeX compatibility
        assert Format(Ref("pct"), ".1%").resolve(data) == r"25.6\%"

    def test_integer_format(self):
        data = {"num": 42}
        assert Format(Ref("num"), "05d").resolve(data) == "00042"


class TestCond:
    def test_cond_true(self):
        data = {"x": 10}
        result = Cond(Ref("x") > 5, "big", "small").resolve(data)
        assert result == "big"

    def test_cond_false(self):
        data = {"x": 3}
        result = Cond(Ref("x") > 5, "big", "small").resolve(data)
        assert result == "small"

    def test_cond_with_specs(self):
        data = {"active": True, "status": "OK", "alt": "ERR"}
        result = Cond(Ref("active"), Ref("status"), Ref("alt")).resolve(data)
        assert result == "OK"


class TestLiteralAndRaw:
    def test_literal(self):
        data = {}
        assert Literal("hello").resolve(data) == "hello"
        assert Literal(42).resolve(data) == 42

    def test_raw(self):
        data = {}
        raw = Raw(r"\textbf{bold}")
        assert raw.resolve(data) == r"\textbf{bold}"
        assert raw.is_raw is True


class TestJoin:
    def test_join_strings(self):
        data = {"first": "John", "last": "Doe"}
        result = Join([Ref("first"), Ref("last")], " ").resolve(data)
        assert result == "John Doe"


class TestCall:
    def test_call_len(self):
        data = {"items": [1, 2, 3, 4, 5]}
        result = Call(len, (Ref("items"),)).resolve(data)
        assert result == 5

    def test_call_max(self):
        data = {"values": [3, 1, 4, 1, 5]}
        result = Call(max, (Ref("values"),)).resolve(data)
        assert result == 5


class TestFormatNumber:
    """Tests for FormatNumber spec with sig, decimals, and thousands separator support."""

    def test_significant_figures(self):
        """Test formatting with significant figures."""
        data = {"value": 1.234567}
        assert FormatNumber(Ref("value"), sig=2).resolve(data) == "1.2"
        assert FormatNumber(Ref("value"), sig=3).resolve(data) == "1.23"
        assert FormatNumber(Ref("value"), sig=4).resolve(data) == "1.235"

    def test_decimal_places(self):
        """Test formatting with fixed decimal places."""
        data = {"value": 1.234567}
        assert FormatNumber(Ref("value"), decimals=2).resolve(data) == "1.23"
        assert FormatNumber(Ref("value"), decimals=3).resolve(data) == "1.235"
        assert FormatNumber(Ref("value"), decimals=0).resolve(data) == "1"

    def test_negative_zero_stripping(self):
        """Test that -0.00 is converted to 0.00."""
        data = {"value": -0.001}
        # With 2 decimal places, -0.001 rounds to -0.00
        assert FormatNumber(Ref("value"), decimals=2).resolve(data) == "0.00"

        # Explicit negative zero
        data2 = {"value": -0.0}
        assert FormatNumber(Ref("value"), decimals=2).resolve(data2) == "0.00"

    def test_thousands_separator_default(self):
        """Test thousands separator with default comma."""
        data = {"value": 2000}
        assert FormatNumber(Ref("value"), thousands_sep=True).resolve(data) == "2,000"

        data = {"value": 1234567}
        assert FormatNumber(Ref("value"), thousands_sep=True).resolve(data) == "1,234,567"

    def test_thousands_separator_custom(self):
        """Test thousands separator with custom character."""
        data = {"value": 2000}
        assert FormatNumber(Ref("value"), thousands_sep=" ").resolve(data) == "2 000"

        data = {"value": 1234567}
        assert FormatNumber(Ref("value"), thousands_sep="_").resolve(data) == "1_234_567"

    def test_thousands_separator_with_decimals(self):
        """Test thousands separator combined with decimal places."""
        data = {"value": 1234.567}
        result = FormatNumber(Ref("value"), decimals=2, thousands_sep=True).resolve(data)
        assert result == "1,234.57"

    def test_thousands_separator_with_sig(self):
        """Test thousands separator combined with significant figures."""
        data = {"value": 1234.567}
        result = FormatNumber(Ref("value"), sig=5, thousands_sep=True).resolve(data)
        assert result == "1,234.6"

    def test_string_passthrough(self):
        """Test that strings pass through unchanged."""
        data = {"value": "hello"}
        assert FormatNumber(Ref("value")).resolve(data) == "hello"

        data = {"value": "N/A"}
        assert FormatNumber(Ref("value"), sig=2).resolve(data) == "N/A"

    def test_numeric_string_conversion(self):
        """Test that numeric strings are converted and formatted."""
        data = {"value": "1234.567"}
        assert FormatNumber(Ref("value"), sig=3).resolve(data) == "1.23e+03"

    def test_zero_handling(self):
        """Test that zero is handled correctly."""
        data = {"value": 0}
        assert FormatNumber(Ref("value"), sig=2).resolve(data) == "0"
        assert FormatNumber(Ref("value"), decimals=2).resolve(data) == "0.00"

    def test_negative_numbers(self):
        """Test negative number formatting."""
        data = {"value": -1234.567}
        assert FormatNumber(Ref("value"), decimals=2).resolve(data) == "-1234.57"

        result = FormatNumber(Ref("value"), decimals=2, thousands_sep=True).resolve(data)
        assert result == "-1,234.57"

    def test_large_numbers(self):
        """Test large number formatting."""
        data = {"value": 1000000}
        result = FormatNumber(Ref("value"), thousands_sep=True).resolve(data)
        assert result == "1,000,000"

    def test_small_numbers_scientific(self):
        """Test that very small numbers work with sig."""
        data = {"value": 0.00001234}
        result = FormatNumber(Ref("value"), sig=2).resolve(data)
        assert result == "1.2e-05"

    def test_cannot_specify_both_sig_and_decimals(self):
        """Test that specifying both sig and decimals raises an error."""
        data = {"value": 1.234}
        with pytest.raises(ValueError, match="Cannot specify both"):
            FormatNumber(Ref("value"), sig=2, decimals=2).resolve(data)

    def test_direct_value_not_ref(self):
        """Test using a direct value instead of Ref."""
        data = {}
        assert FormatNumber(1234.567, sig=3).resolve(data) == "1.23e+03"
        assert FormatNumber(2000, thousands_sep=True).resolve(data) == "2,000"

    def test_strip_negative_zero_disabled(self):
        """Test that negative zero stripping can be disabled."""
        data = {"value": -0.001}
        # With strip_negative_zero=False, should keep the minus sign
        result = FormatNumber(Ref("value"), decimals=2, strip_negative_zero=False).resolve(data)
        assert result == "-0.00"
