"""Tests for the spec system."""

import pytest
from texer.specs import Ref, Iter, Format, Cond, Literal, Raw, Join, Call


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
