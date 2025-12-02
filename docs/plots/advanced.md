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
