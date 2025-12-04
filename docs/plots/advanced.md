# Advanced Plot Options

Complete reference for all plot customization options.

## Cycle Lists

PGFPlots cycle lists define a sequence of styles that are automatically applied to successive `\addplot` commands. This is useful for maintaining consistent styling across multiple plots without manually specifying colors and markers for each one.

!!! note "Automatic `\addplot+` Generation"
    When you create an `AddPlot` without explicit styling options (color, mark, style, or line_width), texer automatically generates `\addplot+` instead of `\addplot`. The `+` tells PGFPlots to use the next style from the cycle list. If you specify any explicit styling, texer generates `\addplot` to override the cycle list for that specific plot.

### Using Predefined Cycle Lists

PGFPlots comes with several built-in cycle lists. You can reference them by name:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        title="Using Predefined Cycle List",
        cycle_list_name="color list",  # Built-in PGFPlots cycle list
        plots=[
            AddPlot(coords=Coordinates([(0, 0), (1, 1), (2, 4)])),
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 3)])),
            AddPlot(coords=Coordinates([(0, 2), (1, 1.5), (2, 2)])),
        ],
        legend=["Series 1", "Series 2", "Series 3"],
    )
)

print(plot.render({}))
```

Common predefined cycle lists include:
- `"color list"` - Cycles through colors
- `"mark list"` - Cycles through marker styles
- `"exotic"` - A predefined color scheme
- `"black white"` - Grayscale styles

### Custom Cycle Lists with Dictionaries

Define your own cycle list with complete style specifications:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Value",
        title="Custom Cycle List",
        cycle_list=[
            {"color": "blue", "mark": "*", "line width": "2pt"},
            {"color": "red", "mark": "square*", "line width": "2pt"},
            {"color": "green", "mark": "triangle*", "line width": "2pt"},
        ],
        plots=[
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 4)])),
            AddPlot(coords=Coordinates([(0, 2), (1, 3), (2, 5)])),
            AddPlot(coords=Coordinates([(0, 0.5), (1, 1.5), (2, 3)])),
        ],
        legend=["Experiment 1", "Experiment 2", "Experiment 3"],
        legend_pos="north west",
    )
)

print(plot.render({}))
```

Each dictionary in the cycle list can contain any valid PGFPlots plot options:
- `color` - Line/marker color
- `mark` - Marker style (`*`, `square*`, `triangle*`, etc.)
- `line width` - Line thickness
- `style` - Line style (`solid`, `dashed`, `dotted`, etc.)
- And many more PGFPlots options

### Simple Color Cycles

For quick color-only cycles, use a list of color names:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        title="Simple Color Cycle",
        cycle_list=["blue", "red", "green", "orange"],
        plots=[
            AddPlot(coords=Coordinates([(0, i), (1, i+1), (2, i+2)]))
            for i in range(4)
        ],
    )
)

print(plot.render({}))
```

### Dynamic Cycle Lists with Ref

Cycle lists can be data-driven using `Ref`:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        cycle_list=Ref("plot_styles"),
        plots=[
            AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
        ],
    )
)

data = {
    "plot_styles": [
        {"color": "blue", "mark": "*"},
        {"color": "red", "mark": "square*"},
    ]
}

print(plot.render(data))
```

You can also use `Ref` for cycle list names:

```python
plot = PGFPlot(
    Axis(
        cycle_list_name=Ref("style_name"),
        plots=[...],
    )
)

data = {"style_name": "exotic"}
print(plot.render(data))
```

### Cycle Lists in Group Plots

Cycle lists can be applied globally to all subplots in a `GroupPlot`:

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates

plot = PGFPlot(
    GroupPlot(
        group_size="1 by 2",
        cycle_list=[
            {"color": "blue", "mark": "*"},
            {"color": "red", "mark": "square*"},
        ],
        plots=[
            NextGroupPlot(
                title="Left Plot",
                plots=[
                    AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                    AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
                ]
            ),
            NextGroupPlot(
                title="Right Plot",
                plots=[
                    AddPlot(coords=Coordinates([(0, 0.5), (1, 1.5)])),
                    AddPlot(coords=Coordinates([(0, 1.5), (1, 2.5)])),
                ]
            ),
        ],
    )
)

print(plot.render({}))
```

Individual `NextGroupPlot` instances can also have their own cycle lists:

```python
plot = PGFPlot(
    GroupPlot(
        group_size="1 by 2",
        plots=[
            NextGroupPlot(
                title="Custom Styles",
                cycle_list=[{"color": "purple", "mark": "diamond*"}],
                plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))]
            ),
            NextGroupPlot(
                title="Default Styles",
                plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3)]))]
            ),
        ],
    )
)
```

### Overriding Cycle List Styles

You can selectively override the cycle list for specific plots by providing explicit styling:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        cycle_list=[
            {"color": "blue", "mark": "*"},
            {"color": "red", "mark": "square*"},
            {"color": "green", "mark": "triangle*"},
        ],
        plots=[
            # Uses cycle list (generates \addplot+)
            AddPlot(coords=Coordinates([(0, 0), (1, 1)])),
            # Overrides with explicit styling (generates \addplot)
            AddPlot(color="purple", mark="x", coords=Coordinates([(0, 1), (1, 2)])),
            # Uses cycle list again (generates \addplot+)
            AddPlot(coords=Coordinates([(0, 0.5), (1, 1.5)])),
        ],
    )
)
```

In this example, the first and third plots use `\addplot+` to pick styles from the cycle list (blue and green respectively), while the second plot uses `\addplot` with explicit purple color to override the cycle list.

### Priority Rules

If both `cycle_list_name` and `cycle_list` are specified, `cycle_list_name` takes precedence:

```python
axis = Axis(
    cycle_list_name="color list",  # This will be used
    cycle_list=["blue", "red"],     # This will be ignored
    plots=[...],
)
```

### Complete Example

Here's a complete example combining cycle lists with dynamic data:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        cycle_list=Ref("styles"),
        plots=Iter(
            Ref("experiments"),
            template=AddPlot(
                coords=Coordinates(
                    Iter(Ref("data"), x=Ref("x"), y=Ref("y"))
                )
            )
        ),
        legend=Iter(Ref("experiments"), template=Ref("name")),
        legend_pos="north west",
    )
)

data = {
    "title": "Experimental Results",
    "x_label": "Time (h)",
    "y_label": "Temperature (°C)",
    "styles": [
        {"color": "blue", "mark": "*", "line width": "1.5pt"},
        {"color": "red", "mark": "square*", "line width": "1.5pt"},
        {"color": "green", "mark": "triangle*", "line width": "1.5pt"},
    ],
    "experiments": [
        {
            "name": "Sensor 1",
            "data": [{"x": 0, "y": 20.5}, {"x": 1, "y": 22.3}, {"x": 2, "y": 25.1}],
        },
        {
            "name": "Sensor 2",
            "data": [{"x": 0, "y": 19.8}, {"x": 1, "y": 21.5}, {"x": 2, "y": 24.2}],
        },
        {
            "name": "Sensor 3",
            "data": [{"x": 0, "y": 21.2}, {"x": 1, "y": 23.1}, {"x": 2, "y": 26.0}],
        },
    ],
}

print(plot.render(data))
```

This produces a plot where each experiment automatically gets the next style from the cycle list, maintaining visual consistency across all data series.

## Legend Customization

Beyond basic legend positioning, texer supports comprehensive legend customization options.

### Legend Cell Alignment

Control the horizontal alignment of text within legend cells:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        legend_cell_align="left",  # "left", "center", or "right"
        plots=[
            AddPlot(color="blue", mark="*", coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(color="red", mark="square*", coords=Coordinates([(0, 2), (1, 3)])),
        ],
        legend=["Short", "A Very Long Legend Entry"],
    )
)
```

### Legend Columns

Arrange legend entries in multiple columns:

```python
plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        legend_columns=2,  # Number of columns
        plots=[
            AddPlot(color="blue", coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(color="red", coords=Coordinates([(0, 2), (1, 3)])),
            AddPlot(color="green", coords=Coordinates([(0, 3), (1, 4)])),
            AddPlot(color="orange", coords=Coordinates([(0, 4), (1, 5)])),
        ],
        legend=["Series A", "Series B", "Series C", "Series D"],
    )
)
```

This creates a 2-column legend with entries arranged as:
```
Series A    Series B
Series C    Series D
```

### Transpose Legend

By default, multi-column legends fill horizontally (left-to-right, then next row). Use `transpose_legend` to fill vertically instead:

```python
plot = PGFPlot(
    Axis(
        legend_columns=2,
        transpose_legend=True,  # Fill columns vertically
        plots=[
            AddPlot(color="blue", coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(color="red", coords=Coordinates([(0, 2), (1, 3)])),
            AddPlot(color="green", coords=Coordinates([(0, 3), (1, 4)])),
            AddPlot(color="orange", coords=Coordinates([(0, 4), (1, 5)])),
        ],
        legend=["A", "B", "C", "D"],
    )
)
```

With `transpose_legend=True`, entries are arranged as:
```
A    C
B    D
```

### Combining Legend Options

All legend options can be combined for full control:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Value",
        # Position
        legend_pos="south east",
        # Alignment
        legend_cell_align="left",
        # Layout
        legend_columns=2,
        transpose_legend=True,
        plots=[
            AddPlot(color="blue", mark="*", coords=Coordinates([(0, 0), (1, 1)])),
            AddPlot(color="red", mark="square*", coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(color="green", mark="triangle*", coords=Coordinates([(0, 0.5), (1, 1.5)])),
        ],
        legend=["Experiment 1", "Experiment 2", "Experiment 3"],
    )
)
```

### Dynamic Legend Options

Like other plot options, legend settings can be data-driven using `Ref`:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        legend_cell_align=Ref("align"),
        legend_columns=Ref("cols"),
        plots=[
            AddPlot(color="blue", coords=Coordinates([(0, 1), (1, 2)])),
            AddPlot(color="red", coords=Coordinates([(0, 2), (1, 3)])),
        ],
        legend=["Data 1", "Data 2"],
    )
)

data = {
    "align": "center",
    "cols": 2,
}

print(plot.render(data))
```

### Available Legend Options

| Option | Type | Description |
|--------|------|-------------|
| `legend_pos` | str | Position of legend box (`"north west"`, `"south east"`, etc.) |
| `legend_style` | str | Raw LaTeX style options for the legend |
| `legend_cell_align` | str | Text alignment within cells (`"left"`, `"center"`, `"right"`) |
| `legend_columns` | int | Number of columns in legend layout |
| `transpose_legend` | bool | Fill legend vertically (by column) instead of horizontally |

## Tick Customization

Control the positions and labels of axis ticks using `xtick`, `ytick`, `ztick` (for 3D plots) and their corresponding label options.

### Setting Tick Positions

Specify exact positions for tick marks:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        xtick=[0, 1, 2, 3, 4],  # Explicit x tick positions
        ytick=[0, 0.5, 1.0],    # Explicit y tick positions
        plots=[
            AddPlot(
                color="blue",
                coords=Coordinates([(0, 0), (1, 0.5), (2, 0.8), (3, 0.9), (4, 1.0)]),
            )
        ],
    )
)
```

This generates:

```latex
\begin{axis}[xlabel={X}, ylabel={Y}, xtick={0,1,2,3,4}, ytick={0,0.5,1.0}]
```

### Custom Tick Labels

Override the default tick labels with custom text:

```python
plot = PGFPlot(
    Axis(
        xlabel="Quarter",
        ylabel="Sales",
        xtick=[1, 2, 3, 4],
        xticklabels=["Q1", "Q2", "Q3", "Q4"],  # Custom labels for each tick
        plots=[
            AddPlot(
                color="blue",
                coords=Coordinates([(1, 100), (2, 150), (3, 200), (4, 180)]),
            )
        ],
    )
)
```

### Using Raw LaTeX Strings

For more control, use raw LaTeX strings:

```python
plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$f(x)$",
        xtick="{0, 0.5*pi, pi, 1.5*pi, 2*pi}",  # Raw LaTeX expression
        xticklabels="{$0$, $\\frac{\\pi}{2}$, $\\pi$, $\\frac{3\\pi}{2}$, $2\\pi$}",
        plots=[
            AddPlot(
                expression="sin(deg(x))",
                domain="0:2*pi",
                samples=100,
            )
        ],
    )
)
```

### Dynamic Ticks with Ref

Tick positions and labels can be data-driven:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref

plot = PGFPlot(
    Axis(
        xlabel="Category",
        ylabel="Value",
        xtick=Ref("tick_positions"),
        xticklabels=Ref("tick_labels"),
        plots=[
            AddPlot(
                color="blue",
                coords=Coordinates(Ref("data")),
            )
        ],
    )
)

data = {
    "tick_positions": [1, 2, 3],
    "tick_labels": ["Low", "Medium", "High"],
    "data": [(1, 10), (2, 25), (3, 15)],
}

print(plot.render(data))
```

### Tick Options in GroupPlots

`NextGroupPlot` also supports tick customization for individual subplots:

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates

plot = PGFPlot(
    GroupPlot(
        group_size="2 by 1",
        plots=[
            NextGroupPlot(
                title="First Plot",
                xtick=[0, 1, 2],
                xticklabels=["A", "B", "C"],
                plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 1.5)]))]
            ),
            NextGroupPlot(
                title="Second Plot",
                xtick=[0, 1, 2],
                xticklabels=["X", "Y", "Z"],
                plots=[AddPlot(coords=Coordinates([(0, 2), (1, 1), (2, 3)]))]
            ),
        ],
    )
)
```

### Available Tick Options

| Option | Type | Description |
|--------|------|-------------|
| `xtick` | list or str | X-axis tick positions |
| `ytick` | list or str | Y-axis tick positions |
| `ztick` | list or str | Z-axis tick positions (3D plots) |
| `xticklabels` | list or str | Custom labels for x-axis ticks |
| `yticklabels` | list or str | Custom labels for y-axis ticks |
| `zticklabels` | list or str | Custom labels for z-axis ticks (3D plots) |

All tick options accept:
- A Python list: `[0, 1, 2, 3]` or `["A", "B", "C"]`
- A raw LaTeX string: `"{0, 0.5, 1}"` or `"{$\\alpha$, $\\beta$}"`
- A `Ref` spec for data-driven values

## Marker Size Control

Control the size of plot markers either uniformly across all points or individually based on your data. This is useful for creating bubble charts where marker size represents a third dimension of data.

### Static Marker Sizes

Set a uniform marker size for all points in a plot using the `mark_size` parameter:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        title="Static Marker Size",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                mark_size=5,  # All markers will be 5pt
                only_marks=True,
                coords=Coordinates(x=[1, 2, 3, 4, 5], y=[2, 4, 3, 5, 4]),
            )
        ],
    )
)

print(plot.render({}))
```

The `mark_size` parameter accepts:
- Numeric values (automatically converted to pt units): `mark_size=5` → `5pt`
- String values with units: `mark_size="3mm"` or `mark_size="0.5cm"`

### Multiple Series with Different Sizes

Create plots with multiple series, each having different marker sizes:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        title="Multiple Series with Different Sizes",
        legend_pos="north west",
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                mark_size=3,
                only_marks=True,
                coords=Coordinates(x=[1, 2, 3, 4, 5], y=[2, 4, 3, 5, 4]),
            ),
            AddPlot(
                color="red",
                mark="square*",
                mark_size=6,
                only_marks=True,
                coords=Coordinates(x=[1, 2, 3, 4, 5], y=[3, 2, 4, 3, 5]),
            ),
            AddPlot(
                color="green",
                mark="triangle*",
                mark_size=9,
                only_marks=True,
                coords=Coordinates(x=[1, 2, 3, 4, 5], y=[4, 5, 2, 4, 3]),
            ),
        ],
        legend=["Small (3pt)", "Medium (6pt)", "Large (9pt)"],
    )
)

print(plot.render({}))
```

### Data-Driven Marker Sizes (Bubble Charts)

For bubble charts, control each marker's size individually based on your data. This requires enabling scatter mode:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X Position",
        ylabel="Y Position",
        title="Bubble Chart",
        grid=True,
        plots=[
            AddPlot(
                color="red",
                mark="*",
                only_marks=True,
                scatter=True,  # Enable scatter mode
                coords=Coordinates(
                    x=[1, 2, 3, 4, 5],
                    y=[2, 4, 3, 5, 4],
                    marker_size=[5, 10, 15, 20, 25]  # Different size for each point
                ),
            )
        ],
    )
)

print(plot.render({}))
```

This generates coordinates with bracket notation for the marker size (meta data):

```latex
\addplot[..., scatter, point meta=explicit,
  visualization depends on={\pgfplotspointmeta \as \perpointmarksize},
  scatter/@pre marker code/.append style={/tikz/mark size=\perpointmarksize}
] coordinates {(1, 2) [5] (2, 4) [10] (3, 3) [15] (4, 5) [20] (5, 4) [25]};
```

### Quick Bubble Charts with scatter_plot()

Use the convenience function for creating bubble charts with minimal code:

```python
from texer import scatter_plot

plot = scatter_plot(
    x=[1, 2, 3, 4, 5],
    y=[2, 4, 3, 5, 4],
    marker_size=[5, 10, 15, 20, 25],
    xlabel="X Value",
    ylabel="Y Value",
    title="Easy Bubble Chart",
    color="green",
    mark="o"
)

print(plot.render({}))
```

The `scatter_plot()` helper automatically:
- Enables scatter mode
- Sets `only_marks=True`
- Configures the marker size visualization

### Dynamic Marker Sizes from Data

Marker sizes can be data-driven using `Ref` and `Iter`:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Performance",
        title=Ref("plot_title"),
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                only_marks=True,
                scatter=True,
                coords=Coordinates(
                    Iter(
                        Ref("measurements"),
                        x=Ref("time"),
                        y=Ref("perf"),
                        marker_size=Ref("importance")
                    )
                ),
            )
        ],
    )
)

data = {
    "plot_title": "Performance Over Time (size = importance)",
    "measurements": [
        {"time": 0, "perf": 50, "importance": 5},
        {"time": 1, "perf": 60, "importance": 8},
        {"time": 2, "perf": 55, "importance": 12},
        {"time": 3, "perf": 70, "importance": 15},
        {"time": 4, "perf": 65, "importance": 20},
    ],
}

print(plot.render(data))
```

### Marker Size in 3D Plots

Data-driven marker sizes also work with 3D scatter plots:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        zlabel="Z",
        title="3D Bubble Chart",
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                only_marks=True,
                scatter=True,
                coords=Coordinates(
                    x=[1, 2, 3],
                    y=[1, 2, 3],
                    z=[1, 4, 9],
                    marker_size=[5, 10, 15]
                ),
            )
        ],
    )
)
```

### Complete Example: Multi-Series Bubble Chart

Combine multiple series with data-driven marker sizes:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter

plot = PGFPlot(
    Axis(
        xlabel="Time (hours)",
        ylabel="Temperature (°C)",
        title="Multi-Sensor Temperature Monitoring",
        legend_pos="north west",
        grid=True,
        plots=Iter(
            Ref("sensors"),
            template=AddPlot(
                color=Ref("color"),
                mark="*",
                only_marks=True,
                scatter=True,
                coords=Coordinates(
                    Iter(Ref("readings"), x=Ref("time"), y=Ref("temp"), marker_size=Ref("confidence"))
                ),
            )
        ),
        legend=Iter(Ref("sensors"), template=Ref("name")),
    )
)

data = {
    "sensors": [
        {
            "name": "Sensor A (size = confidence)",
            "color": "blue",
            "readings": [
                {"time": 0, "temp": 20, "confidence": 5},
                {"time": 1, "temp": 22, "confidence": 8},
                {"time": 2, "temp": 25, "confidence": 12},
            ],
        },
        {
            "name": "Sensor B (size = confidence)",
            "color": "red",
            "readings": [
                {"time": 0, "temp": 19, "confidence": 7},
                {"time": 1, "temp": 21, "confidence": 10},
                {"time": 2, "temp": 24, "confidence": 15},
            ],
        },
    ],
}

print(plot.render(data))
```

### Available Marker Size Options

| Option | Context | Type | Description |
|--------|---------|------|-------------|
| `mark_size` | `AddPlot` | float, int, or str | Static marker size for all points |
| `marker_size` | `Coordinates` | list or `Ref` | Individual marker size for each point (requires `scatter=True`) |
| `scatter` | `AddPlot` | bool | Enable scatter mode for data-driven marker sizes |
| `scatter_src` | `AddPlot` | str | Control how marker size data is interpreted (default: `"explicit"`) |

### Notes

- Data-driven marker sizes require `scatter=True` in the `AddPlot`
- The `marker_size` parameter in `Coordinates` adds a third (or fourth for 3D) value to each coordinate
- Marker sizes are specified in LaTeX pt units by default
- Static `mark_size` and data-driven `marker_size` are independent features that can't be combined in the same plot

## Title Style Customization

The `title_style` option allows you to customize the appearance of plot titles with LaTeX/PGFPlots styling options. This is useful for controlling font size, color, alignment, and other typographic properties.

### Basic Title Styling

Apply custom styling to plot titles:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        title="My Styled Title",
        title_style="font=\\Large,text=blue",
        plots=[
            AddPlot(
                color="blue",
                coords=Coordinates([(0, 0), (1, 1), (2, 4)]),
            )
        ],
    )
)
```

This generates:

```latex
\begin{axis}[xlabel={X}, ylabel={Y}, title={My Styled Title}, title style={font=\Large,text=blue}]
```

### Common Title Style Options

You can use any valid PGFPlots/TikZ style options in `title_style`:

```python
plot = PGFPlot(
    Axis(
        title="Experimental Results",
        title_style="font=\\huge,color=red,align=center",
        xlabel="Time (s)",
        ylabel="Value",
        plots=[
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 4)])),
        ],
    )
)
```

Common style options include:

- **Font size**: `font=\\tiny`, `font=\\small`, `font=\\normalsize`, `font=\\large`, `font=\\Large`, `font=\\LARGE`, `font=\\huge`, `font=\\Huge`
- **Color**: `color=blue`, `text=red`, `text=black!50` (50% black)
- **Alignment**: `align=center`, `align=left`, `align=right`
- **Font style**: `font=\\bfseries` (bold), `font=\\itshape` (italic)
- **Multiple options**: Combine with commas: `font=\\Large\\bfseries,color=blue,align=center`

### Dynamic Title Styling with Ref

Title styles can be data-driven using `Ref`:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref

plot = PGFPlot(
    Axis(
        title=Ref("plot_title"),
        title_style=Ref("title_styling"),
        xlabel="X",
        ylabel="Y",
        plots=[
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 4)])),
        ],
    )
)

data = {
    "plot_title": "Dynamic Title",
    "title_styling": "font=\\huge,color=red",
}

print(plot.render(data))
```

### Title Styling in GroupPlots

Each subplot in a `GroupPlot` can have its own title style:

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates

plot = PGFPlot(
    GroupPlot(
        group_size="1 by 2",
        plots=[
            NextGroupPlot(
                title="Left Plot",
                title_style="font=\\Large,color=blue",
                plots=[
                    AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                ]
            ),
            NextGroupPlot(
                title="Right Plot",
                title_style="font=\\Large,color=red",
                plots=[
                    AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
                ]
            ),
        ],
    )
)
```

### Advanced Examples

#### Consistent Title Styling Across Multiple Plots

Use a consistent style for all plot titles:

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates, Ref

# Common style definition
TITLE_STYLE = "font=\\Large\\bfseries,color=black!80,align=center"

plot = PGFPlot(
    GroupPlot(
        group_size="2 by 2",
        plots=[
            NextGroupPlot(
                title="Plot A",
                title_style=TITLE_STYLE,
                plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))]
            ),
            NextGroupPlot(
                title="Plot B",
                title_style=TITLE_STYLE,
                plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3)]))]
            ),
            NextGroupPlot(
                title="Plot C",
                title_style=TITLE_STYLE,
                plots=[AddPlot(coords=Coordinates([(0, 3), (1, 4)]))]
            ),
            NextGroupPlot(
                title="Plot D",
                title_style=TITLE_STYLE,
                plots=[AddPlot(coords=Coordinates([(0, 4), (1, 5)]))]
            ),
        ],
    )
)
```

#### Data-Driven Title Styling for Multiple Subplots

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates, Ref, Iter

plot = PGFPlot(
    GroupPlot(
        group_size="1 by 2",
        plots=Iter(
            Ref("subplots"),
            template=NextGroupPlot(
                title=Ref("title"),
                title_style=Ref("style"),
                plots=[
                    AddPlot(
                        coords=Coordinates(
                            Iter(Ref("data"), x=Ref("x"), y=Ref("y"))
                        )
                    )
                ],
            ),
        ),
    )
)

data = {
    "subplots": [
        {
            "title": "Dataset 1",
            "style": "font=\\Large,color=blue",
            "data": [{"x": 0, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 4}],
        },
        {
            "title": "Dataset 2",
            "style": "font=\\Large,color=red",
            "data": [{"x": 0, "y": 2}, {"x": 1, "y": 3}, {"x": 2, "y": 5}],
        },
    ],
}

print(plot.render(data))
```

### Available Title Options

| Option | Type | Description |
|--------|------|-------------|
| `title` | str or Ref | The title text |
| `title_style` | str or Ref | LaTeX/PGFPlots styling options for the title |

Both options work in `Axis` and `NextGroupPlot` contexts and support:
- Static strings
- `Ref` specs for data-driven values
- Any valid PGFPlots/TikZ style options
