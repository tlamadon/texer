# Basic Plots

## Mental Model for Plots

Think of plots as nested structures:

```
PGFPlot (tikzpicture wrapper)
└── Axis (the coordinate system)
    ├── Options (xlabel, ylabel, limits, grid, ...)
    ├── Plots (list of AddPlot)
    │   └── AddPlot
    │       ├── Style (color, mark, line style)
    │       └── Data (Coordinates or expression)
    └── Legend
```

- **PGFPlot**: The tikzpicture wrapper
- **Axis**: The coordinate system with labels and limits
- **AddPlot**: A single plot/series
- **Coordinates**: Data points or mathematical expression

## Your First Plot

Let's create a simple scatter plot with static data:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Distance (m)",
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates([(0, 0), (1, 2), (2, 8), (3, 18)]),
            )
        ],
    )
)

print(evaluate(plot, {}))
```

**Output:**

```latex
\begin{tikzpicture}
  \begin{axis}[xlabel={Time (s)}, ylabel={Distance (m)}]
    \addplot[color=blue, mark=*] coordinates {(0, 0) (1, 2) (2, 8) (3, 18)};
  \end{axis}
\end{tikzpicture}
```

## Understanding the Parts

### Axis Options

```python
Axis(
    # Labels
    xlabel="X Axis",
    ylabel="Y Axis",
    title="Plot Title",

    # Limits
    xmin=0, xmax=10,
    ymin=-5, ymax=5,

    # Grid
    grid=True,              # Show grid

    # Dimensions
    width="10cm",
    height="6cm",

    # Plots and legend
    plots=[...],
    legend=["Series 1", "Series 2"],
    legend_pos="north west",
)
```

### AddPlot Style Options

```python
AddPlot(
    # Color
    color="blue",           # or "red", "green", "black", etc.

    # Markers
    mark="*",              # *, o, square*, triangle*, etc.
    mark_size="2pt",

    # Lines
    style="dashed",        # solid, dashed, dotted, dashdotted
    line_width="1pt",
    thick=True,            # Shorthand for thick line

    # Mark control
    only_marks=True,       # Scatter plot (no lines)
    no_marks=True,         # Line plot (no markers)

    # Data
    coords=Coordinates(...),
)
```

### Common Marker Types

| Mark | Appearance |
|------|------------|
| `*` | Filled star |
| `o` | Circle |
| `square*` | Filled square |
| `triangle*` | Filled triangle |
| `diamond*` | Filled diamond |
| `+` | Plus sign |
| `x` | Cross |

## Plot Types

### Scatter Plot

```python
plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        plots=[
            AddPlot(
                color="red",
                mark="o",
                only_marks=True,  # No connecting lines
                coords=Coordinates([(1, 2), (2, 4), (3, 3), (4, 5)]),
            )
        ],
    )
)
```

### Line Plot

```python
plot = PGFPlot(
    Axis(
        xlabel="Time",
        ylabel="Value",
        plots=[
            AddPlot(
                color="blue",
                thick=True,
                no_marks=True,  # No markers, just line
                coords=Coordinates([(0, 1), (1, 2), (2, 4), (3, 8)]),
            )
        ],
    )
)
```

### Line + Markers

```python
plot = PGFPlot(
    Axis(
        plots=[
            AddPlot(
                color="green",
                mark="square*",
                coords=Coordinates([(0, 0), (1, 1), (2, 4), (3, 9)]),
            )
        ],
    )
)
```

## Using NumPy Arrays

You can pass NumPy arrays directly:

```python
import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

# Generate data
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$\\sin(x)$",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                thick=True,
                no_marks=True,
                coords=Coordinates(x=x, y=y),  # Direct from NumPy!
            )
        ],
    )
)

print(evaluate(plot, {}))
```

## Grid and Styling

```python
plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Voltage (V)",
        title="Sensor Readings",
        grid=True,               # Show grid
        width="12cm",
        height="8cm",
        xmin=0, xmax=10,
        ymin=0, ymax=5,
        plots=[...],
    )
)
```

## Multiple Series

Add multiple `AddPlot` instances with a legend:

```python
plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates([(0, 0), (1, 1), (2, 4)]),
            ),
            AddPlot(
                color="red",
                mark="square*",
                style="dashed",
                coords=Coordinates([(0, 1), (1, 2), (2, 3)]),
            ),
        ],
        legend=["Series A", "Series B"],
        legend_pos="north west",
    )
)
```

### Legend Positions

| Position | Location |
|----------|----------|
| `north west` | Top left |
| `north east` | Top right |
| `south west` | Bottom left |
| `south east` | Bottom right |
| `outer north east` | Outside plot area, right side |

## Mathematical Expressions

Plot mathematical functions directly:

```python
plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$f(x)$",
        xmin=-5, xmax=5,
        ymin=-1.5, ymax=1.5,
        grid=True,
        plots=[
            AddPlot(
                expression="sin(deg(x))",
                domain="-5:5",
                samples=100,
                color="blue",
                thick=True,
                no_marks=True,
            ),
        ],
    )
)
```

!!! note "Trigonometric Functions"
    PGFPlots expects angles in degrees. Use `deg(x)` to convert radians to degrees.

## Next Steps

- [Data-Driven Plots](data-driven.md) - Use specs for dynamic plots
- [Multiple Series](multiple-series.md) - Complex multi-series plots
- [GroupPlots](groupplots.md) - Multiple subplots in a grid
- [Advanced Options](advanced.md) - Complete reference for plot options
