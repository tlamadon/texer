"""PGFPlots classes for LaTeX figure generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from texer.specs import Spec, Iter, resolve_value
from texer.utils import format_options, indent


@dataclass
class Coordinates:
    """Coordinates for a plot.

    Examples:
        # Static coordinates
        Coordinates([(0, 1), (1, 2), (2, 4)])

        # Dynamic coordinates from data
        Coordinates(Iter(Ref("points"), x=Ref("x"), y=Ref("y")))

        # 3D coordinates
        Coordinates([(0, 0, 1), (1, 1, 2)])
    """

    source: list[tuple[Any, ...]] | Iter | Spec

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render coordinates to LaTeX."""
        if scope is None:
            scope = {}

        # Resolve the source
        if isinstance(self.source, (Iter, Spec)):
            points = self.source.resolve(data, scope)
        else:
            points = self.source

        # Format coordinates
        coord_strs = []
        for point in points:
            if isinstance(point, tuple):
                coord_strs.append(f"({', '.join(str(v) for v in point)})")
            else:
                # Single value (rare case)
                coord_strs.append(f"({point})")

        return "coordinates {" + " ".join(coord_strs) + "}"


@dataclass
class AddPlot:
    """An \\addplot command for PGFPlots.

    Examples:
        AddPlot(
            color="blue",
            mark="*",
            coords=Coordinates([(0, 1), (1, 2)])
        )

        AddPlot(
            style="dashed",
            domain="0:10",
            expression="x^2"
        )
    """

    # Coordinate-based plot
    coords: Coordinates | None = None

    # Expression-based plot
    expression: str | None = None
    domain: str | None = None
    samples: int | None = None

    # Style options
    color: str | None = None
    mark: str | None = None
    style: str | None = None
    line_width: str | None = None
    only_marks: bool = False
    no_marks: bool = False
    smooth: bool = False
    thick: bool = False

    # Plot name for legend
    name: str | None = None

    # 3D options
    surf: bool = False
    mesh: bool = False

    # Error bars
    error_bars: bool = False
    error_bar_style: dict[str, Any] = field(default_factory=dict)

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the addplot command."""
        if scope is None:
            scope = {}

        parts = []

        # Build options
        options = {}
        if self.color:
            options["color"] = self.color
        if self.mark:
            options["mark"] = self.mark
        if self.style:
            options[self.style] = True
        if self.line_width:
            options["line width"] = self.line_width
        if self.only_marks:
            options["only marks"] = True
        if self.no_marks:
            options["mark"] = "none"
        if self.smooth:
            options["smooth"] = True
        if self.thick:
            options["thick"] = True
        if self.domain:
            options["domain"] = self.domain
        if self.samples:
            options["samples"] = self.samples
        if self.surf:
            options["surf"] = True
        if self.mesh:
            options["mesh"] = True

        # 3D variant
        plot_cmd = "\\addplot3" if self.surf or self.mesh else "\\addplot"

        # Format options string
        opts_str = format_options(options, self._raw_options)
        if opts_str:
            parts.append(f"{plot_cmd}[{opts_str}]")
        else:
            parts.append(plot_cmd)

        # Add coordinates or expression
        if self.coords is not None:
            parts.append(self.coords.render(data, scope))
        elif self.expression is not None:
            parts.append(f"{{{self.expression}}}")

        return " ".join(parts) + ";"

    def __repr__(self) -> str:
        return f"AddPlot(color={self.color!r}, mark={self.mark!r}, ...)"


@dataclass
class Legend:
    """Legend entries for a plot.

    Examples:
        Legend(["Series A", "Series B"])
        Legend([Ref("legend_label")])
    """

    entries: list[Any]

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render legend command."""
        if scope is None:
            scope = {}

        from texer.eval import _evaluate_impl

        resolved = []
        for entry in self.entries:
            resolved.append(_evaluate_impl(entry, data, scope, escape=False))

        return "\\legend{" + ", ".join(resolved) + "}"


@dataclass
class Axis:
    """A PGFPlots axis environment.

    Examples:
        Axis(
            xlabel="Time (s)",
            ylabel="Temperature (K)",
            plots=[AddPlot(...)],
            legend=["Data"]
        )
    """

    plots: list[AddPlot] = field(default_factory=list)

    # Axis labels
    xlabel: str | Spec | None = None
    ylabel: str | Spec | None = None
    zlabel: str | Spec | None = None
    title: str | Spec | None = None

    # Axis limits
    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None
    zmin: float | None = None
    zmax: float | None = None

    # Legend
    legend: list[Any] | Legend | None = None
    legend_pos: str | None = None
    legend_style: str | None = None

    # Grid
    grid: str | bool | None = None  # "major", "minor", "both", True, False

    # Axis type
    axis_type: str = "axis"  # "axis", "semilogxaxis", "semilogyaxis", "loglogaxis"

    # Scale
    width: str | None = None
    height: str | None = None

    # Other common options
    enlargelimits: bool | float | None = None
    clip: bool | None = None
    axis_lines: str | None = None  # "left", "center", "right", "box"

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the axis environment."""
        if scope is None:
            scope = {}

        from texer.eval import _evaluate_impl

        # Build options
        options = {}

        # Labels (resolve if Spec)
        if self.xlabel is not None:
            options["xlabel"] = _evaluate_impl(self.xlabel, data, scope, escape=False)
        if self.ylabel is not None:
            options["ylabel"] = _evaluate_impl(self.ylabel, data, scope, escape=False)
        if self.zlabel is not None:
            options["zlabel"] = _evaluate_impl(self.zlabel, data, scope, escape=False)
        if self.title is not None:
            options["title"] = _evaluate_impl(self.title, data, scope, escape=False)

        # Limits
        if self.xmin is not None:
            options["xmin"] = self.xmin
        if self.xmax is not None:
            options["xmax"] = self.xmax
        if self.ymin is not None:
            options["ymin"] = self.ymin
        if self.ymax is not None:
            options["ymax"] = self.ymax
        if self.zmin is not None:
            options["zmin"] = self.zmin
        if self.zmax is not None:
            options["zmax"] = self.zmax

        # Legend position
        if self.legend_pos is not None:
            options["legend pos"] = self.legend_pos
        if self.legend_style is not None:
            options["legend style"] = self.legend_style

        # Grid
        if self.grid is True:
            options["grid"] = "major"
        elif self.grid:
            options["grid"] = self.grid

        # Dimensions
        if self.width is not None:
            options["width"] = self.width
        if self.height is not None:
            options["height"] = self.height

        # Other options
        if self.enlargelimits is not None:
            options["enlargelimits"] = self.enlargelimits
        if self.clip is not None:
            options["clip"] = self.clip
        if self.axis_lines is not None:
            options["axis lines"] = self.axis_lines

        # Format options
        opts_str = format_options(options, self._raw_options)

        lines = []

        # Opening
        if opts_str:
            lines.append(f"\\begin{{{self.axis_type}}}[{opts_str}]")
        else:
            lines.append(f"\\begin{{{self.axis_type}}}")

        # Plots
        for plot in self.plots:
            lines.append(f"  {plot.render(data, scope)}")

        # Legend
        if self.legend is not None:
            if isinstance(self.legend, Legend):
                lines.append(f"  {self.legend.render(data, scope)}")
            else:
                legend = Legend(self.legend)
                lines.append(f"  {legend.render(data, scope)}")

        # Closing
        lines.append(f"\\end{{{self.axis_type}}}")

        return "\n".join(lines)


@dataclass
class PGFPlot:
    """A complete PGFPlots tikzpicture.

    Examples:
        PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[AddPlot(coords=Coordinates([...]))]
            )
        )
    """

    axis: Axis
    preamble: list[str] = field(default_factory=list)
    scale: float | None = None
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the complete tikzpicture."""
        if scope is None:
            scope = {}

        lines = []

        # Preamble (for standalone use)
        for line in self.preamble:
            lines.append(line)

        # Build tikzpicture options
        options = {}
        if self.scale is not None:
            options["scale"] = self.scale

        opts_str = format_options(options, self._raw_options)

        # Opening
        if opts_str:
            lines.append(f"\\begin{{tikzpicture}}[{opts_str}]")
        else:
            lines.append("\\begin{tikzpicture}")

        # Axis content
        axis_lines = self.axis.render(data, scope)
        for line in axis_lines.split("\n"):
            lines.append(f"  {line}" if line else line)

        # Closing
        lines.append("\\end{tikzpicture}")

        return "\n".join(lines)

    def with_preamble(self) -> str:
        """Return LaTeX code including package imports for standalone use."""
        preamble = [
            "\\documentclass{standalone}",
            "\\usepackage{pgfplots}",
            "\\pgfplotsset{compat=1.18}",
            "",
            "\\begin{document}",
        ]
        content = self.render({})
        closing = ["\\end{document}"]

        return "\n".join(preamble + [content] + closing)


# Convenience classes for specialized axis types
@dataclass
class SemiLogXAxis(Axis):
    """A semi-logarithmic axis (log scale on x-axis)."""

    axis_type: str = "semilogxaxis"


@dataclass
class SemiLogYAxis(Axis):
    """A semi-logarithmic axis (log scale on y-axis)."""

    axis_type: str = "semilogyaxis"


@dataclass
class LogLogAxis(Axis):
    """A log-log axis (log scale on both axes)."""

    axis_type: str = "loglogaxis"


# Helper for creating simple line plots
def simple_plot(
    x: list[float],
    y: list[float],
    xlabel: str = "x",
    ylabel: str = "y",
    title: str | None = None,
    color: str = "blue",
    mark: str = "*",
) -> PGFPlot:
    """Create a simple line plot from x and y data.

    Args:
        x: X-axis data points.
        y: Y-axis data points.
        xlabel: Label for x-axis.
        ylabel: Label for y-axis.
        title: Optional plot title.
        color: Line/marker color.
        mark: Marker style.

    Returns:
        A PGFPlot object ready for rendering.
    """
    coords = Coordinates(list(zip(x, y)))

    return PGFPlot(
        Axis(
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            plots=[AddPlot(color=color, mark=mark, coords=coords)],
        )
    )
