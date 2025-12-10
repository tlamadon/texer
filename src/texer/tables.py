"""Table classes for LaTeX table generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from texer.specs import Spec, resolve_value, Iter
from texer.utils import escape_latex, format_options, indent


@dataclass
class Cell:
    """A table cell with optional formatting.

    Examples:
        Cell(Ref("value"))
        Cell(Ref("value"), bold=True)
        Cell(Format(Ref("price"), ".2f"), align="r")
        Cell(Ref("name"), bold=Cond(Ref("important"), True, False))
    """

    content: Any
    bold: bool | Spec = False
    italic: bool | Spec = False
    align: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the cell to LaTeX."""
        from texer.eval import _evaluate_impl, evaluate_value

        content = _evaluate_impl(self.content, data, scope or {}, escape=False)

        # Resolve bold/italic if they are Specs
        bold = evaluate_value(self.bold, data, scope) if isinstance(self.bold, Spec) else self.bold
        italic = evaluate_value(self.italic, data, scope) if isinstance(self.italic, Spec) else self.italic

        if bold:
            content = f"\\textbf{{{content}}}"
        if italic:
            content = f"\\textit{{{content}}}"

        return content


@dataclass
class MultiColumn:
    """A cell spanning multiple columns.

    Examples:
        MultiColumn(3, "c", "Header Title")
    """

    ncols: int
    align: str
    content: Any

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the multicolumn cell."""
        from texer.eval import _evaluate_impl

        content = _evaluate_impl(self.content, data, scope or {}, escape=False)
        return f"\\multicolumn{{{self.ncols}}}{{{self.align}}}{{{content}}}"


@dataclass
class MultiRow:
    """A cell spanning multiple rows.

    Examples:
        MultiRow(2, "Category")
    """

    nrows: int
    content: Any
    width: str = "*"

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the multirow cell."""
        from texer.eval import _evaluate_impl

        content = _evaluate_impl(self.content, data, scope or {}, escape=False)
        return f"\\multirow{{{self.nrows}}}{{{self.width}}}{{{content}}}"


@dataclass
class Row:
    """A table row containing cells.

    Examples:
        Row("Name", "Value", "Unit")
        Row(Ref("name"), Ref("value"), Ref("unit"))
        Row(Cell(Ref("x"), bold=True), Ref("y"))
        Row("A", "B", "C", end=r"\\[4pt]")  # Extra vertical space
        Row("A", "B", "C", end="")  # No line ending
    """

    cells: tuple[Any, ...] = field(default_factory=tuple)
    end: str = field(default=r"\\")
    _raw_options: str | None = None

    def __init__(self, *cells: Any, end: str = r"\\", _raw_options: str | None = None):
        object.__setattr__(self, "cells", cells)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "_raw_options", _raw_options)

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the row to LaTeX."""
        from texer.eval import _evaluate_impl

        rendered_cells = []
        for cell in self.cells:
            if isinstance(cell, (Cell, MultiColumn, MultiRow)):
                rendered_cells.append(cell.render(data, scope))
            else:
                rendered_cells.append(_evaluate_impl(cell, data, scope or {}, escape=False))

        row_content = " & ".join(rendered_cells)
        if self.end:
            return f"{row_content} {self.end}"
        return row_content


@dataclass
class HLine:
    """A horizontal line in a table."""

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        return "\\hline"


@dataclass
class CLine:
    """A partial horizontal line (cline)."""

    start: int
    end: int

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        return f"\\cline{{{self.start}-{self.end}}}"


@dataclass
class Tabular:
    """A LaTeX tabular environment.

    Examples:
        Tabular(
            columns="lcc",
            header=Row("Name", "Value 1", "Value 2"),
            rows=Iter(Ref("data"), template=Row(Ref("name"), Ref("v1"), Ref("v2")))
        )
    """

    columns: str
    header: Row | list[Row] | None = None
    rows: Any = None  # Iter, list of Rows, or single Row
    toprule: bool = False
    midrule: bool = False
    bottomrule: bool = False
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the tabular environment."""
        if scope is None:
            scope = {}

        lines = []

        # Opening
        lines.append(f"\\begin{{tabular}}{{{self.columns}}}")

        # Top rule (booktabs)
        if self.toprule:
            lines.append("  \\toprule")

        # Header
        if self.header is not None:
            if isinstance(self.header, list):
                for h in self.header:
                    lines.append(f"  {h.render(data, scope)}")
            else:
                lines.append(f"  {self.header.render(data, scope)}")

            # Mid rule after header
            if self.midrule or self.toprule:
                lines.append("  \\midrule")

        # Body rows
        if self.rows is not None:
            rendered_rows = self._render_rows(data, scope)
            for row in rendered_rows:
                lines.append(f"  {row}")

        # Bottom rule
        if self.bottomrule:
            lines.append("  \\bottomrule")

        # Closing
        lines.append("\\end{tabular}")

        return "\n".join(lines)

    def _render_iter(self, iter_obj: Iter, data: Any, scope: dict[str, Any]) -> list[str]:
        """Render an Iter object to a list of row strings."""
        # Get the source items
        if isinstance(iter_obj.source, str):
            import glom  # type: ignore[import-untyped]
            items = glom.glom(data, iter_obj.source)
        else:
            items = iter_obj.source.resolve(data, scope)

        if iter_obj.template is not None:
            # Render the template for each item
            results = []
            for item in items:
                if isinstance(iter_obj.template, Row):
                    results.append(iter_obj.template.render(item, scope))
                elif hasattr(iter_obj.template, "render"):
                    results.append(iter_obj.template.render(item, scope))
                else:
                    from texer.eval import _evaluate_impl
                    results.append(_evaluate_impl(iter_obj.template, item, scope, escape=False))
            return results
        else:
            # No template, just resolve
            return [str(item) for item in items]

    def _render_rows(self, data: Any, scope: dict[str, Any]) -> list[str]:
        """Render the body rows."""
        if isinstance(self.rows, Iter):
            return self._render_iter(self.rows, data, scope)
        elif isinstance(self.rows, list):
            results = []
            for row in self.rows:
                if isinstance(row, Iter):
                    results.extend(self._render_iter(row, data, scope))
                else:
                    results.append(row.render(data, scope))
            return results
        elif isinstance(self.rows, Row):
            return [self.rows.render(data, scope)]
        elif isinstance(self.rows, Spec):
            resolved = self.rows.resolve(data, scope)
            if isinstance(resolved, list):
                return [str(r) for r in resolved]
            return [str(resolved)]
        return []


@dataclass
class Table:
    """A LaTeX table environment (floating).

    Examples:
        Table(
            Tabular(...),
            caption="My Table",
            label="tab:mytable",
            position="htbp"
        )
    """

    content: Tabular
    caption: Any = None
    label: str | None = None
    position: str = "htbp"
    centering: bool = True
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the table environment."""
        if scope is None:
            scope = {}

        lines = []

        # Opening
        lines.append(f"\\begin{{table}}[{self.position}]")

        if self.centering:
            lines.append("  \\centering")

        # Caption (before table for some styles)
        if self.caption is not None:
            from texer.eval import _evaluate_impl
            caption_text = _evaluate_impl(self.caption, data, scope, escape=False)
            lines.append(f"  \\caption{{{caption_text}}}")

        # Label
        if self.label is not None:
            lines.append(f"  \\label{{{self.label}}}")

        # Tabular content
        tabular_lines = self.content.render(data, scope)
        for line in tabular_lines.split("\n"):
            lines.append(f"  {line}" if line else line)

        # Closing
        lines.append("\\end{table}")

        return "\n".join(lines)


# Convenience function for simple tables
def simple_table(
    headers: list[str],
    rows: list[list[Any]],
    caption: str | None = None,
    label: str | None = None,
) -> Table:
    """Create a simple table from headers and row data.

    Args:
        headers: List of column headers.
        rows: List of row data (each row is a list of values).
        caption: Optional table caption.
        label: Optional label for referencing.

    Returns:
        A Table object ready for rendering.
    """
    ncols = len(headers)
    columns = "l" + "c" * (ncols - 1)  # First column left, rest centered

    header_row = Row(*headers)
    data_rows = [Row(*row) for row in rows]

    tabular = Tabular(
        columns=columns,
        header=header_row,
        rows=data_rows,
        toprule=True,
        midrule=True,
        bottomrule=True,
    )

    return Table(tabular, caption=caption, label=label)
