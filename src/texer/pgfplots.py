"""PGFPlots classes for LaTeX figure generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from texer.specs import Spec, Iter, resolve_value
from texer.utils import format_options, indent

# Type aliases for common PGF options
MarkStyle = Literal[
    "*", "x", "+", "-", "|", "o", "asterisk", "star",
    "10-pointed star", "oplus", "oplus*", "otimes", "otimes*",
    "square", "square*", "triangle", "triangle*",
    "diamond", "diamond*", "pentagon", "pentagon*",
    "Mercedes star", "Mercedes star flipped",
    "halfcircle", "halfcircle*", "halfsquare*", "halfdiamond*"
]

LineStyle = Literal[
    "solid", "dotted", "densely dotted", "loosely dotted",
    "dashed", "densely dashed", "loosely dashed",
    "dashdotted", "densely dashdotted", "loosely dashdotted",
    "dashdotdotted", "densely dashdotdotted", "loosely dashdotdotted"
]

ColorName = Literal[
    "red", "green", "blue", "cyan", "magenta", "yellow",
    "black", "gray", "white", "darkgray", "lightgray",
    "brown", "lime", "olive", "orange", "pink", "purple", "teal", "violet"
]

LegendPos = Literal[
    "north west", "north east", "south west", "south east",
    "north", "south", "east", "west",
    "outer north east"
]

AxisLines = Literal["left", "center", "right", "box", "middle", "none"]

GridStyle = Literal["major", "minor", "both", "none"]


@dataclass
class Coordinates:
    """Coordinates for a plot.

    Examples:
        # Static coordinates (list of tuples)
        Coordinates([(0, 1), (1, 2), (2, 4)])

        # From separate x, y arrays (numpy arrays or lists)
        Coordinates(x=[0, 1, 2], y=[1, 2, 4])
        Coordinates(x=np.array([0, 1, 2]), y=np.array([1, 2, 4]))

        # 3D coordinates
        Coordinates([(0, 0, 1), (1, 1, 2)])
        Coordinates(x=[0, 1], y=[0, 1], z=[1, 2])

        # Dynamic coordinates from data
        Coordinates(Iter(Ref("points"), x=Ref("x"), y=Ref("y")))
    """

    source: list[tuple[Any, ...]] | Iter | Spec | None = None
    x: Any = None
    y: Any = None
    z: Any = None

    def __post_init__(self) -> None:
        """Validate that either source or x/y are provided."""
        if self.source is None and self.x is None:
            raise ValueError("Either 'source' or 'x' and 'y' must be provided")
        if self.source is not None and (self.x is not None or self.y is not None):
            raise ValueError("Cannot specify both 'source' and 'x'/'y' parameters")
        if self.x is not None and self.y is None:
            raise ValueError("If 'x' is provided, 'y' must also be provided")

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render coordinates to LaTeX."""
        if scope is None:
            scope = {}

        # Handle x, y, z arrays
        if self.x is not None:
            points = self._arrays_to_points()
        # Resolve the source
        elif isinstance(self.source, (Iter, Spec)):
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

    def _arrays_to_points(self) -> list[tuple[Any, ...]]:
        """Convert x, y, z arrays to list of tuples."""
        # Convert to lists if numpy arrays
        x_list = self._to_list(self.x)
        y_list = self._to_list(self.y)

        if self.z is not None:
            z_list = self._to_list(self.z)
            if not (len(x_list) == len(y_list) == len(z_list)):
                raise ValueError(f"x, y, and z must have the same length (got {len(x_list)}, {len(y_list)}, {len(z_list)})")
            return list(zip(x_list, y_list, z_list))
        else:
            if len(x_list) != len(y_list):
                raise ValueError(f"x and y must have the same length (got {len(x_list)}, {len(y_list)})")
            return list(zip(x_list, y_list))

    @staticmethod
    def _to_list(arr: Any) -> list[Any]:
        """Convert array-like to list, handling numpy arrays."""
        # Check if it's a numpy array
        if hasattr(arr, '__array__') or hasattr(arr, 'tolist'):
            return arr.tolist()
        # Already a list or tuple
        elif isinstance(arr, (list, tuple)):
            return list(arr)
        else:
            raise TypeError(f"Expected array-like object, got {type(arr)}")


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
    color: ColorName | str | None = None
    mark: MarkStyle | str | None = None
    style: LineStyle | str | None = None
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
    legend_pos: LegendPos | str | None = None
    legend_style: str | None = None

    # Grid
    grid: GridStyle | bool | None = None

    # Axis type
    axis_type: Literal["axis", "semilogxaxis", "semilogyaxis", "loglogaxis"] = "axis"

    # Scale
    width: str | None = None
    height: str | None = None

    # Other common options
    enlargelimits: bool | float | None = None
    clip: bool | None = None
    axis_lines: AxisLines | str | None = None

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
class NextGroupPlot:
    """A \\nextgroupplot command within a groupplot environment.

    Examples:
        NextGroupPlot(
            title="Plot 1",
            xlabel="X",
            plots=[AddPlot(...)]
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
    legend_pos: LegendPos | str | None = None
    legend_style: str | None = None

    # Grid
    grid: GridStyle | bool | None = None

    # Other options
    enlargelimits: bool | float | None = None
    clip: bool | None = None
    axis_lines: AxisLines | str | None = None

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the nextgroupplot command and its contents."""
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
            lines.append(f"\\nextgroupplot[{opts_str}]")
        else:
            lines.append("\\nextgroupplot")

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

        return "\n".join(lines)


@dataclass
class GroupPlot:
    """A groupplot environment for creating multiple plots in a grid layout.

    Examples:
        GroupPlot(
            group_style={"group size": "2 by 2"},
            plots=[
                NextGroupPlot(title="Plot 1", plots=[...]),
                NextGroupPlot(title="Plot 2", plots=[...]),
                NextGroupPlot(title="Plot 3", plots=[...]),
                NextGroupPlot(title="Plot 4", plots=[...]),
            ]
        )
    """

    plots: list[NextGroupPlot] = field(default_factory=list)

    # Group style options
    group_size: str | None = None  # e.g., "2 by 2"
    horizontal_sep: str | None = None
    vertical_sep: str | None = None
    xlabels_at: str | None = None  # e.g., "edge bottom"
    ylabels_at: str | None = None  # e.g., "edge left"
    xticklabels_at: str | None = None
    yticklabels_at: str | None = None

    # Common axis options (applied to all subplots)
    width: str | None = None
    height: str | None = None
    xmin: float | None = None
    xmax: float | None = None
    ymin: float | None = None
    ymax: float | None = None

    # Raw options escape hatch
    _raw_options: str | None = None
    _raw_group_style: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the groupplot environment."""
        if scope is None:
            scope = {}

        # Build group style options
        group_style_opts = {}
        if self.group_size is not None:
            group_style_opts["group size"] = self.group_size
        if self.horizontal_sep is not None:
            group_style_opts["horizontal sep"] = self.horizontal_sep
        if self.vertical_sep is not None:
            group_style_opts["vertical sep"] = self.vertical_sep
        if self.xlabels_at is not None:
            group_style_opts["xlabels at"] = self.xlabels_at
        if self.ylabels_at is not None:
            group_style_opts["ylabels at"] = self.ylabels_at
        if self.xticklabels_at is not None:
            group_style_opts["xticklabels at"] = self.xticklabels_at
        if self.yticklabels_at is not None:
            group_style_opts["yticklabels at"] = self.yticklabels_at

        # Build main options
        options = {}

        # Add group style if present
        group_style_str = format_options(group_style_opts, self._raw_group_style)
        if group_style_str:
            options["group style"] = f"{{{group_style_str}}}"

        # Common options
        if self.width is not None:
            options["width"] = self.width
        if self.height is not None:
            options["height"] = self.height
        if self.xmin is not None:
            options["xmin"] = self.xmin
        if self.xmax is not None:
            options["xmax"] = self.xmax
        if self.ymin is not None:
            options["ymin"] = self.ymin
        if self.ymax is not None:
            options["ymax"] = self.ymax

        # Format options
        opts_str = format_options(options, self._raw_options)

        lines = []

        # Opening
        if opts_str:
            lines.append(f"\\begin{{groupplot}}[{opts_str}]")
        else:
            lines.append("\\begin{groupplot}")

        # Render each plot
        for plot in self.plots:
            plot_lines = plot.render(data, scope)
            for line in plot_lines.split("\n"):
                lines.append(f"  {line}" if line else line)

        # Closing
        lines.append("\\end{groupplot}")

        return "\n".join(lines)


@dataclass
class PGFPlot:
    """A complete PGFPlots tikzpicture.

    Examples:
        # Single axis
        PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[AddPlot(coords=Coordinates([...]))]
            )
        )

        # Multiple plots in a grid with groupplot
        PGFPlot(
            GroupPlot(
                group_size="2 by 2",
                plots=[
                    NextGroupPlot(...),
                    NextGroupPlot(...),
                ]
            )
        )
    """

    axis: Axis | GroupPlot
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
            "\\usepgfplotslibrary{groupplots}",
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
