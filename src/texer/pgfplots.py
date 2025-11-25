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

        # Control precision (default 6 significant figures)
        Coordinates(x=[0.123456789], y=[0.987654321])  # Outputs (0.123457, 0.987654)
        Coordinates(x=[0.123456789], y=[0.987654321], precision=3)  # Outputs (0.123, 0.988)
        Coordinates(x=[0.123456789], y=[0.987654321], precision=None)  # No rounding
    """

    source: list[tuple[Any, ...]] | Iter | Spec | None = None
    x: Any = None
    y: Any = None
    z: Any = None
    precision: int | None = 6  # Number of significant figures (None = no rounding)

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
            # Resolve x, y, z if they are Specs
            x_resolved = resolve_value(self.x, data, scope)
            y_resolved = resolve_value(self.y, data, scope)
            z_resolved = resolve_value(self.z, data, scope) if self.z is not None else None
            points = self._arrays_to_points_resolved(x_resolved, y_resolved, z_resolved)
        # Resolve the source
        elif isinstance(self.source, (Iter, Spec)):
            points = self.source.resolve(data, scope)
        else:
            points = self.source  # type: ignore[assignment]

        # Format coordinates
        coord_strs = []
        for point in points:
            if isinstance(point, tuple):
                formatted_values = [self._format_value(v) for v in point]
                coord_strs.append(f"({', '.join(formatted_values)})")
            else:
                # Single value (rare case)
                coord_strs.append(f"({self._format_value(point)})")

        return "coordinates {" + " ".join(coord_strs) + "}"

    def _arrays_to_points_resolved(self, x: Any, y: Any, z: Any = None) -> list[tuple[Any, ...]]:
        """Convert resolved x, y, z arrays to list of tuples."""
        # Convert to lists if numpy arrays
        x_list = self._to_list(x)
        y_list = self._to_list(y)

        if z is not None:
            z_list = self._to_list(z)
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
            result: list[Any] = arr.tolist()
            return result
        # Already a list or tuple
        elif isinstance(arr, (list, tuple)):
            return list(arr)
        else:
            raise TypeError(f"Expected array-like object, got {type(arr)}")

    def _format_value(self, value: Any) -> str:
        """Format a numeric value with specified precision."""
        # If precision is None, no rounding
        if self.precision is None:
            return str(value)

        # Try to format as float with significant figures
        try:
            val = float(value)
            # Handle special cases
            if val == 0:
                return "0"

            # Use the 'g' format specifier which uses significant figures
            # and automatically switches between fixed and scientific notation
            format_str = f"{{:.{self.precision}g}}"
            return format_str.format(val)
        except (ValueError, TypeError):
            # Not a number, return as-is
            return str(value)


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
    expression: str | Spec | None = None
    domain: str | Spec | None = None
    samples: int | Spec | None = None

    # Style options
    color: ColorName | str | Spec | None = None
    mark: MarkStyle | str | Spec | None = None
    style: LineStyle | str | Spec | None = None
    line_width: str | Spec | None = None
    only_marks: bool | Spec = False
    no_marks: bool | Spec = False
    smooth: bool | Spec = False
    thick: bool | Spec = False

    # Plot name for legend
    name: str | Spec | None = None

    # 3D options
    surf: bool = False
    mesh: bool = False

    # Error bars
    error_bars: bool = False
    error_bar_style: dict[str, Any] = field(default_factory=dict)

    # Cycle list option
    use_cycle_list: bool = False

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the addplot command."""
        if scope is None:
            scope = {}

        parts = []

        # Build options (resolve Specs like Ref)
        options = {}
        if self.color:
            options["color"] = resolve_value(self.color, data, scope)
        if self.mark:
            options["mark"] = resolve_value(self.mark, data, scope)
        if self.style:
            resolved_style = resolve_value(self.style, data, scope)
            options[resolved_style] = True
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
        base_cmd = "\\addplot3" if self.surf or self.mesh else "\\addplot"

        # Check if we should use cycle list automatically
        # Use + if use_cycle_list is explicitly set, OR if there are no color/mark/style options
        has_style_options = bool(self.color or self.mark or self.style or self.line_width)
        should_use_cycle = self.use_cycle_list or not has_style_options

        # Add + for cycle list usage
        plot_cmd = base_cmd + "+" if should_use_cycle else base_cmd

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

    entries: list[Any] | Iter | Spec

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render legend command."""
        if scope is None:
            scope = {}

        from texer.eval import _evaluate_impl

        # Resolve entries if it's a Spec (like Iter)
        entries = resolve_value(self.entries, data, scope)

        resolved = []
        for entry in entries:
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

    plots: list[AddPlot] | Iter | Spec = field(default_factory=list)

    # Axis labels
    xlabel: str | Spec | None = None
    ylabel: str | Spec | None = None
    zlabel: str | Spec | None = None
    title: str | Spec | None = None

    # Axis limits
    xmin: float | Spec | None = None
    xmax: float | Spec | None = None
    ymin: float | Spec | None = None
    ymax: float | Spec | None = None
    zmin: float | Spec | None = None
    zmax: float | Spec | None = None

    # Legend
    legend: list[Any] | Legend | Iter | Spec | None = None
    legend_pos: LegendPos | str | Spec | None = None
    legend_style: str | Spec | None = None
    legend_cell_align: Literal["left", "center", "right"] | str | Spec | None = None
    legend_columns: int | Spec | None = None
    transpose_legend: bool | Spec | None = None

    # Grid
    grid: GridStyle | bool | Spec | None = None

    # Axis type
    axis_type: Literal["axis", "semilogxaxis", "semilogyaxis", "loglogaxis"] = "axis"

    # Scale
    width: str | Spec | None = None
    height: str | Spec | None = None

    # Other common options
    enlargelimits: bool | float | Spec | None = None
    clip: bool | Spec | None = None
    axis_lines: AxisLines | str | Spec | None = None

    # Cycle list options
    cycle_list_name: str | Spec | None = None
    cycle_list: list[dict[str, Any]] | list[str] | Spec | None = None

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the axis environment."""
        if scope is None:
            scope = {}

        from texer.eval import _evaluate_impl

        # Build options
        options: dict[str, Any] = {}

        # Labels (resolve if Spec)
        if self.xlabel is not None:
            options["xlabel"] = _evaluate_impl(self.xlabel, data, scope, escape=False)
        if self.ylabel is not None:
            options["ylabel"] = _evaluate_impl(self.ylabel, data, scope, escape=False)
        if self.zlabel is not None:
            options["zlabel"] = _evaluate_impl(self.zlabel, data, scope, escape=False)
        if self.title is not None:
            options["title"] = _evaluate_impl(self.title, data, scope, escape=False)

        # Limits (resolve if Spec)
        if self.xmin is not None:
            options["xmin"] = resolve_value(self.xmin, data, scope)
        if self.xmax is not None:
            options["xmax"] = resolve_value(self.xmax, data, scope)
        if self.ymin is not None:
            options["ymin"] = resolve_value(self.ymin, data, scope)
        if self.ymax is not None:
            options["ymax"] = resolve_value(self.ymax, data, scope)
        if self.zmin is not None:
            options["zmin"] = resolve_value(self.zmin, data, scope)
        if self.zmax is not None:
            options["zmax"] = resolve_value(self.zmax, data, scope)

        # Legend options (resolve if Spec)
        if self.legend_pos is not None:
            options["legend pos"] = resolve_value(self.legend_pos, data, scope)
        if self.legend_style is not None:
            options["legend style"] = resolve_value(self.legend_style, data, scope)
        if self.legend_cell_align is not None:
            options["legend cell align"] = resolve_value(self.legend_cell_align, data, scope)
        if self.legend_columns is not None:
            options["legend columns"] = resolve_value(self.legend_columns, data, scope)
        if self.transpose_legend is not None:
            transpose_value = resolve_value(self.transpose_legend, data, scope)
            if transpose_value:
                options["transpose legend"] = True

        # Grid (resolve if Spec)
        grid_value = resolve_value(self.grid, data, scope) if isinstance(self.grid, Spec) else self.grid
        if grid_value is True:
            options["grid"] = "major"
        elif grid_value:
            options["grid"] = grid_value

        # Dimensions (resolve if Spec)
        if self.width is not None:
            options["width"] = resolve_value(self.width, data, scope)
        if self.height is not None:
            options["height"] = resolve_value(self.height, data, scope)

        # Other options (resolve if Spec)
        if self.enlargelimits is not None:
            options["enlargelimits"] = resolve_value(self.enlargelimits, data, scope)
        if self.clip is not None:
            options["clip"] = resolve_value(self.clip, data, scope)
        if self.axis_lines is not None:
            options["axis lines"] = resolve_value(self.axis_lines, data, scope)

        # Cycle list options (resolve if Spec)
        if self.cycle_list_name is not None:
            options["cycle list name"] = resolve_value(self.cycle_list_name, data, scope)
        elif self.cycle_list is not None:
            cycle_list_resolved = resolve_value(self.cycle_list, data, scope)
            # Format cycle list
            cycle_entries = []
            for entry in cycle_list_resolved:
                if isinstance(entry, dict):
                    # Format as key=value pairs wrapped in braces
                    entry_str = format_options(entry, None)
                    cycle_entries.append("{" + entry_str + "}")
                else:
                    # Plain string entry
                    cycle_entries.append(str(entry))
            options["cycle list"] = "{" + ",".join(cycle_entries) + "}"

        # Format options
        opts_str = format_options(options, self._raw_options)

        lines = []

        # Opening
        if opts_str:
            lines.append(f"\\begin{{{self.axis_type}}}[{opts_str}]")
        else:
            lines.append(f"\\begin{{{self.axis_type}}}")

        # Plots (handle Iter specially to preserve scope)
        if isinstance(self.plots, Iter):
            # Resolve the Iter source to get items
            if isinstance(self.plots.source, str):
                import glom  # type: ignore[import-untyped]
                items = glom.glom(data, self.plots.source)
            else:
                items = self.plots.source.resolve(data, scope)

            # For each item, create updated scope and render template
            for item in items:
                item_scope = dict(scope) if scope else {}
                if isinstance(item, dict):
                    item_scope.update(item)
                # Resolve and render the template with the item scope
                plot = resolve_value(self.plots.template, item, item_scope)
                lines.append(f"  {plot.render(data, item_scope)}")
        else:
            # Regular list of plots
            plots = resolve_value(self.plots, data, scope)
            for plot in plots:
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

    plots: list[AddPlot] | Iter | Spec = field(default_factory=list)

    # Axis labels
    xlabel: str | Spec | None = None
    ylabel: str | Spec | None = None
    zlabel: str | Spec | None = None
    title: str | Spec | None = None

    # Axis limits
    xmin: float | Spec | None = None
    xmax: float | Spec | None = None
    ymin: float | Spec | None = None
    ymax: float | Spec | None = None
    zmin: float | Spec | None = None
    zmax: float | Spec | None = None

    # Legend
    legend: list[Any] | Legend | Iter | Spec | None = None
    legend_pos: LegendPos | str | Spec | None = None
    legend_style: str | Spec | None = None
    legend_cell_align: Literal["left", "center", "right"] | str | Spec | None = None
    legend_columns: int | Spec | None = None
    transpose_legend: bool | Spec | None = None

    # Grid
    grid: GridStyle | bool | Spec | None = None

    # Other options
    enlargelimits: bool | float | Spec | None = None
    clip: bool | Spec | None = None
    axis_lines: AxisLines | str | Spec | None = None

    # Cycle list options
    cycle_list_name: str | Spec | None = None
    cycle_list: list[dict[str, Any]] | list[str] | Spec | None = None

    # Raw options escape hatch
    _raw_options: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the nextgroupplot command and its contents."""
        if scope is None:
            scope = {}

        from texer.eval import _evaluate_impl

        # Build options
        options: dict[str, Any] = {}

        # Labels (resolve if Spec)
        if self.xlabel is not None:
            options["xlabel"] = _evaluate_impl(self.xlabel, data, scope, escape=False)
        if self.ylabel is not None:
            options["ylabel"] = _evaluate_impl(self.ylabel, data, scope, escape=False)
        if self.zlabel is not None:
            options["zlabel"] = _evaluate_impl(self.zlabel, data, scope, escape=False)
        if self.title is not None:
            options["title"] = _evaluate_impl(self.title, data, scope, escape=False)

        # Limits (resolve if Spec)
        if self.xmin is not None:
            options["xmin"] = resolve_value(self.xmin, data, scope)
        if self.xmax is not None:
            options["xmax"] = resolve_value(self.xmax, data, scope)
        if self.ymin is not None:
            options["ymin"] = resolve_value(self.ymin, data, scope)
        if self.ymax is not None:
            options["ymax"] = resolve_value(self.ymax, data, scope)
        if self.zmin is not None:
            options["zmin"] = resolve_value(self.zmin, data, scope)
        if self.zmax is not None:
            options["zmax"] = resolve_value(self.zmax, data, scope)

        # Legend options (resolve if Spec)
        if self.legend_pos is not None:
            options["legend pos"] = resolve_value(self.legend_pos, data, scope)
        if self.legend_style is not None:
            options["legend style"] = resolve_value(self.legend_style, data, scope)
        if self.legend_cell_align is not None:
            options["legend cell align"] = resolve_value(self.legend_cell_align, data, scope)
        if self.legend_columns is not None:
            options["legend columns"] = resolve_value(self.legend_columns, data, scope)
        if self.transpose_legend is not None:
            transpose_value = resolve_value(self.transpose_legend, data, scope)
            if transpose_value:
                options["transpose legend"] = True

        # Grid (resolve if Spec)
        grid_value = resolve_value(self.grid, data, scope) if isinstance(self.grid, Spec) else self.grid
        if grid_value is True:
            options["grid"] = "major"
        elif grid_value:
            options["grid"] = grid_value

        # Other options (resolve if Spec)
        if self.enlargelimits is not None:
            options["enlargelimits"] = resolve_value(self.enlargelimits, data, scope)
        if self.clip is not None:
            options["clip"] = resolve_value(self.clip, data, scope)
        if self.axis_lines is not None:
            options["axis lines"] = resolve_value(self.axis_lines, data, scope)

        # Cycle list options (resolve if Spec)
        if self.cycle_list_name is not None:
            options["cycle list name"] = resolve_value(self.cycle_list_name, data, scope)
        elif self.cycle_list is not None:
            cycle_list_resolved = resolve_value(self.cycle_list, data, scope)
            # Format cycle list
            cycle_entries = []
            for entry in cycle_list_resolved:
                if isinstance(entry, dict):
                    # Format as key=value pairs wrapped in braces
                    entry_str = format_options(entry, None)
                    cycle_entries.append("{" + entry_str + "}")
                else:
                    # Plain string entry
                    cycle_entries.append(str(entry))
            options["cycle list"] = "{" + ",".join(cycle_entries) + "}"

        # Format options
        opts_str = format_options(options, self._raw_options)

        lines = []

        # Opening
        if opts_str:
            lines.append(f"\\nextgroupplot[{opts_str}]")
        else:
            lines.append("\\nextgroupplot")

        # Plots (handle Iter specially to preserve scope)
        if isinstance(self.plots, Iter):
            # Resolve the Iter source to get items
            if isinstance(self.plots.source, str):
                import glom
                items = glom.glom(data, self.plots.source)
            else:
                items = self.plots.source.resolve(data, scope)

            # For each item, create updated scope and render template
            for item in items:
                item_scope = dict(scope) if scope else {}
                if isinstance(item, dict):
                    item_scope.update(item)
                # Resolve and render the template with the item scope
                plot = resolve_value(self.plots.template, item, item_scope)
                lines.append(f"  {plot.render(data, item_scope)}")
        else:
            # Regular list of plots
            plots = resolve_value(self.plots, data, scope)
            for plot in plots:
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

    plots: list[NextGroupPlot] | Iter | Spec = field(default_factory=list)

    # Group style options
    group_size: str | Spec | None = None  # e.g., "2 by 2"
    horizontal_sep: str | Spec | None = None
    vertical_sep: str | Spec | None = None
    xlabels_at: str | Spec | None = None  # e.g., "edge bottom"
    ylabels_at: str | Spec | None = None  # e.g., "edge left"
    xticklabels_at: str | Spec | None = None
    yticklabels_at: str | Spec | None = None

    # Common axis options (applied to all subplots)
    width: str | Spec | None = None
    height: str | Spec | None = None
    xmin: float | Spec | None = None
    xmax: float | Spec | None = None
    ymin: float | Spec | None = None
    ymax: float | Spec | None = None

    # Cycle list options (applied to all subplots)
    cycle_list_name: str | Spec | None = None
    cycle_list: list[dict[str, Any]] | list[str] | Spec | None = None

    # Raw options escape hatch
    _raw_options: str | None = None
    _raw_group_style: str | None = None

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render the groupplot environment."""
        if scope is None:
            scope = {}

        # Build group style options (resolve if Spec)
        group_style_opts = {}
        if self.group_size is not None:
            group_style_opts["group size"] = resolve_value(self.group_size, data, scope)
        if self.horizontal_sep is not None:
            group_style_opts["horizontal sep"] = resolve_value(self.horizontal_sep, data, scope)
        if self.vertical_sep is not None:
            group_style_opts["vertical sep"] = resolve_value(self.vertical_sep, data, scope)
        if self.xlabels_at is not None:
            group_style_opts["xlabels at"] = resolve_value(self.xlabels_at, data, scope)
        if self.ylabels_at is not None:
            group_style_opts["ylabels at"] = resolve_value(self.ylabels_at, data, scope)
        if self.xticklabels_at is not None:
            group_style_opts["xticklabels at"] = resolve_value(self.xticklabels_at, data, scope)
        if self.yticklabels_at is not None:
            group_style_opts["yticklabels at"] = resolve_value(self.yticklabels_at, data, scope)

        # Build main options
        options = {}

        # Add group style if present
        group_style_str = format_options(group_style_opts, self._raw_group_style)
        if group_style_str:
            options["group style"] = f"{{{group_style_str}}}"

        # Common options (resolve if Spec)
        if self.width is not None:
            options["width"] = resolve_value(self.width, data, scope)
        if self.height is not None:
            options["height"] = resolve_value(self.height, data, scope)
        if self.xmin is not None:
            options["xmin"] = resolve_value(self.xmin, data, scope)
        if self.xmax is not None:
            options["xmax"] = resolve_value(self.xmax, data, scope)
        if self.ymin is not None:
            options["ymin"] = resolve_value(self.ymin, data, scope)
        if self.ymax is not None:
            options["ymax"] = resolve_value(self.ymax, data, scope)

        # Cycle list options (resolve if Spec)
        if self.cycle_list_name is not None:
            options["cycle list name"] = resolve_value(self.cycle_list_name, data, scope)
        elif self.cycle_list is not None:
            cycle_list_resolved = resolve_value(self.cycle_list, data, scope)
            # Format cycle list
            cycle_entries = []
            for entry in cycle_list_resolved:
                if isinstance(entry, dict):
                    # Format as key=value pairs wrapped in braces
                    entry_str = format_options(entry, None)
                    cycle_entries.append("{" + entry_str + "}")
                else:
                    # Plain string entry
                    cycle_entries.append(str(entry))
            options["cycle list"] = "{" + ",".join(cycle_entries) + "}"

        # Format options
        opts_str = format_options(options, self._raw_options)

        lines = []

        # Opening
        if opts_str:
            lines.append(f"\\begin{{groupplot}}[{opts_str}]")
        else:
            lines.append("\\begin{groupplot}")

        # Render each plot (resolve if Spec)
        plots = resolve_value(self.plots, data, scope)
        for plot in plots:
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
    scale: float | Spec | None = None
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

    def with_preamble(self, data: Any = None) -> str:
        """Return LaTeX code including package imports for standalone use.

        Args:
            data: Optional data dict for rendering (default: empty dict).
        """
        if data is None:
            data = {}

        preamble = [
            "\\documentclass{standalone}",
            "\\usepackage{pgfplots}",
            "\\pgfplotsset{compat=1.18}",
            "\\usepgfplotslibrary{groupplots}",
            "",
            "\\begin{document}",
        ]
        content = self.render(data)
        closing = ["\\end{document}"]

        return "\n".join(preamble + [content] + closing)

    def save_to_file(
        self,
        file_path: str,
        data: Any = None,
        with_preamble: bool = True,
    ) -> None:
        """Save the LaTeX code to a file.

        Args:
            file_path: Path to the output .tex file.
            data: Optional data dict for rendering (default: empty dict).
            with_preamble: Whether to include document preamble for standalone compilation (default: True).

        Examples:
            # Save with preamble for standalone compilation
            plot.save_to_file("my_plot.tex")

            # Save just the tikzpicture content
            plot.save_to_file("my_plot.tex", with_preamble=False)

            # Save with data
            plot.save_to_file("my_plot.tex", data=my_data)
        """
        if data is None:
            data = {}

        if with_preamble:
            latex_code = self.with_preamble(data)
        else:
            latex_code = self.render(data)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

    def compile_to_pdf(
        self,
        tex_file_path: str,
        data: Any = None,
        output_dir: str | None = None,
    ) -> str:
        """Save to .tex file and compile to PDF using pdflatex.

        Args:
            tex_file_path: Path to save the .tex file (e.g., "my_plot.tex").
            data: Optional data dict for rendering (default: empty dict).
            output_dir: Optional output directory for compilation (default: same as .tex file).

        Returns:
            Path to the generated PDF file.

        Raises:
            RuntimeError: If pdflatex is not available or compilation fails.

        Examples:
            # Simple compilation
            pdf_path = plot.compile_to_pdf("my_plot.tex")

            # With data
            pdf_path = plot.compile_to_pdf("my_plot.tex", data=my_data)

            # Specify output directory
            pdf_path = plot.compile_to_pdf("my_plot.tex", output_dir="/tmp")
        """
        import subprocess
        import shutil
        from pathlib import Path

        # Check if pdflatex is available
        if shutil.which("pdflatex") is None:
            raise RuntimeError(
                "pdflatex not found. Please install a LaTeX distribution (e.g., TeX Live, MiKTeX)."
            )

        # Save to file
        self.save_to_file(tex_file_path, data=data, with_preamble=True)

        # Determine paths
        tex_path = Path(tex_file_path).resolve()
        output_path: Path
        if output_dir is None:
            output_path = tex_path.parent
        else:
            output_path = Path(output_dir).resolve()

        # Run pdflatex
        try:
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    f"-output-directory={output_path}",
                    str(tex_path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"pdflatex compilation failed:\n{e.stderr}\n\nOutput:\n{e.stdout}"
            ) from e

        # Return path to PDF
        pdf_path = output_path / tex_path.with_suffix(".pdf").name
        return str(pdf_path)


# Convenience classes for specialized axis types
@dataclass
class SemiLogXAxis(Axis):
    """A semi-logarithmic axis (log scale on x-axis)."""

    axis_type: Literal["axis", "semilogxaxis", "semilogyaxis", "loglogaxis"] = "semilogxaxis"


@dataclass
class SemiLogYAxis(Axis):
    """A semi-logarithmic axis (log scale on y-axis)."""

    axis_type: Literal["axis", "semilogxaxis", "semilogyaxis", "loglogaxis"] = "semilogyaxis"


@dataclass
class LogLogAxis(Axis):
    """A log-log axis (log scale on both axes)."""

    axis_type: Literal["axis", "semilogxaxis", "semilogyaxis", "loglogaxis"] = "loglogaxis"


# Helper for creating simple line plots
def simple_plot(
    x: list[float],
    y: list[float],
    xlabel: str = "x",
    ylabel: str = "y",
    title: str | None = None,
    color: str = "blue",
    mark: str = "*",
    precision: int | None = 6,
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
        precision: Number of significant figures for coordinates (default: 6, None for no rounding).

    Returns:
        A PGFPlot object ready for rendering.
    """
    coords = Coordinates(list(zip(x, y)), precision=precision)

    return PGFPlot(
        Axis(
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            plots=[AddPlot(color=color, mark=mark, coords=coords)],
        )
    )
