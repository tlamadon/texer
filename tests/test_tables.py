"""Tests for table generation."""

import pytest
from texer import Table, Tabular, Row, Cell, MultiColumn, Ref, Iter, evaluate


class TestRow:
    def test_simple_row(self):
        row = Row("A", "B", "C")
        result = row.render({})
        assert result == "A & B & C \\\\"

    def test_row_with_ref(self):
        row = Row(Ref("name"), Ref("value"))
        data = {"name": "Test", "value": 42}
        result = row.render(data)
        assert result == "Test & 42 \\\\"


class TestCell:
    def test_bold_cell(self):
        cell = Cell("text", bold=True)
        result = cell.render({})
        assert result == "\\textbf{text}"

    def test_italic_cell(self):
        cell = Cell("text", italic=True)
        result = cell.render({})
        assert result == "\\textit{text}"

    def test_bold_italic_cell(self):
        cell = Cell("text", bold=True, italic=True)
        result = cell.render({})
        assert result == "\\textit{\\textbf{text}}"


class TestMultiColumn:
    def test_multicolumn(self):
        mc = MultiColumn(3, "c", "Header")
        result = mc.render({})
        assert result == "\\multicolumn{3}{c}{Header}"


class TestTabular:
    def test_simple_tabular(self):
        tabular = Tabular(
            columns="lcc",
            header=Row("Name", "Value 1", "Value 2"),
            rows=[Row("Item", "10", "20")],
        )
        result = tabular.render({})
        assert "\\begin{tabular}{lcc}" in result
        assert "Name & Value 1 & Value 2 \\\\" in result
        assert "Item & 10 & 20 \\\\" in result
        assert "\\end{tabular}" in result

    def test_tabular_with_booktabs(self):
        tabular = Tabular(
            columns="lc",
            header=Row("A", "B"),
            rows=[Row("1", "2")],
            toprule=True,
            bottomrule=True,
        )
        result = tabular.render({})
        assert "\\toprule" in result
        assert "\\midrule" in result
        assert "\\bottomrule" in result

    def test_tabular_with_iter(self):
        tabular = Tabular(
            columns="lc",
            header=Row("Name", "Value"),
            rows=Iter(Ref("data"), template=Row(Ref("name"), Ref("value"))),
        )
        data = {
            "data": [
                {"name": "Item 1", "value": 10},
                {"name": "Item 2", "value": 20},
            ]
        }
        result = tabular.render(data)
        assert "Item 1 & 10 \\\\" in result
        assert "Item 2 & 20 \\\\" in result

    def test_tabular_with_iter_and_static_rows(self):
        """Test combining Iter with static Row objects in a list."""
        tabular = Tabular(
            columns="lc",
            header=Row("Name", "Value"),
            rows=[
                Row("Static First", "0"),
                Iter(Ref("data"), template=Row(Ref("name"), Ref("value"))),
                Row("Static Last", "100"),
            ],
        )
        data = {
            "data": [
                {"name": "Dynamic 1", "value": 10},
                {"name": "Dynamic 2", "value": 20},
            ]
        }
        result = tabular.render(data)
        # Static row before Iter
        assert "Static First & 0 \\\\" in result
        # Dynamic rows from Iter
        assert "Dynamic 1 & 10 \\\\" in result
        assert "Dynamic 2 & 20 \\\\" in result
        # Static row after Iter
        assert "Static Last & 100 \\\\" in result


class TestTable:
    def test_table_environment(self):
        table = Table(
            Tabular(columns="lc", rows=[Row("A", "B")]),
            caption="My Table",
            label="tab:test",
        )
        result = table.render({})
        assert "\\begin{table}[htbp]" in result
        assert "\\centering" in result
        assert "\\caption{My Table}" in result
        assert "\\label{tab:test}" in result
        assert "\\end{table}" in result


class TestEvaluate:
    def test_evaluate_table(self):
        table = Table(
            Tabular(
                columns="lcc",
                header=Row("Name", "V1", "V2"),
                rows=Iter(
                    Ref("items"),
                    template=Row(Ref("name"), Ref("v1"), Ref("v2")),
                ),
                toprule=True,
                bottomrule=True,
            ),
            caption=Ref("title"),
            label="tab:data",
        )
        data = {
            "title": "Results",
            "items": [
                {"name": "A", "v1": 1, "v2": 2},
                {"name": "B", "v1": 3, "v2": 4},
            ],
        }
        result = evaluate(table, data)
        assert "\\caption{Results}" in result
        assert "A & 1 & 2 \\\\" in result
        assert "B & 3 & 4 \\\\" in result
