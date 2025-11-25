# Multiple Series Plots

Create plots with multiple data series using `Iter` to dynamically generate plots from data collections.

## Static Multiple Series

The simplest approach - define each series explicitly:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Time (h)",
        ylabel="Temperature (°C)",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates([(0, 20), (1, 22), (2, 25)]),
            ),
            AddPlot(
                color="red",
                mark="square*",
                coords=Coordinates([(0, 19), (1, 21), (2, 24)]),
            ),
            AddPlot(
                color="green",
                mark="triangle*",
                coords=Coordinates([(0, 21), (1, 23), (2, 26)]),
            ),
        ],
        legend=["Sensor 1", "Sensor 2", "Sensor 3"],
        legend_pos="north west",
    )
)

print(evaluate(plot, {}))
```

## Dynamic Multiple Series with Iter

Generate multiple plot series dynamically from data:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        grid=True,
        plots=Iter(
            Ref("series"),
            template=AddPlot(
                color=Ref("color"),
                mark=Ref("marker"),
                coords=Coordinates(
                    Iter(Ref("data"), x=Ref("t"), y=Ref("value"))
                ),
            )
        ),
        legend=Iter(Ref("series"), template=Ref("name")),
        legend_pos="north west",
    )
)

data = {
    "title": "Multi-Sensor Temperature Monitoring",
    "x_label": "Time (h)",
    "y_label": "Temperature (°C)",
    "series": [
        {
            "name": "Sensor 1",
            "color": "blue",
            "marker": "*",
            "data": [
                {"t": 0, "value": 20.5},
                {"t": 1, "value": 22.3},
                {"t": 2, "value": 25.1},
            ],
        },
        {
            "name": "Sensor 2",
            "color": "red",
            "marker": "square*",
            "data": [
                {"t": 0, "value": 19.8},
                {"t": 1, "value": 21.5},
                {"t": 2, "value": 24.2},
            ],
        },
        {
            "name": "Sensor 3",
            "color": "green",
            "marker": "triangle*",
            "data": [
                {"t": 0, "value": 21.2},
                {"t": 1, "value": 23.1},
                {"t": 2, "value": 26.0},
            ],
        },
    ],
}

print(evaluate(plot, data))
```

## How Iter Works for Plots

The `Iter` spec for plots works in two places:

### 1. Generating Multiple AddPlot Instances

```python
plots=Iter(
    Ref("series"),       # Source: list of series
    template=AddPlot(    # Template to instantiate for each item
        color=Ref("color"),
        coords=Coordinates(...),
    )
)
```

For each item in `series`, it creates an `AddPlot` with values from that item.

### 2. Generating Legend Entries

```python
legend=Iter(
    Ref("series"),      # Same source
    template=Ref("name") # Extract 'name' from each item
)
```

This creates a legend entry for each series.

## With NumPy Arrays

Combine `Iter` with NumPy for computational plots:

```python
import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$y$",
        title="Polynomial Functions",
        grid=True,
        xmin=-2,
        xmax=2,
        plots=Iter(
            Ref("functions"),
            template=AddPlot(
                color=Ref("color"),
                thick=True,
                no_marks=True,
                coords=Coordinates(x=Ref("x"), y=Ref("y")),
            )
        ),
        legend=Iter(Ref("functions"), template=Ref("label")),
    )
)

# Generate data
x = np.linspace(-2, 2, 100)

data = {
    "functions": [
        {"label": "$x$", "color": "blue", "x": x, "y": x},
        {"label": "$x^2$", "color": "red", "x": x, "y": x**2},
        {"label": "$x^3$", "color": "green", "x": x, "y": x**3},
    ]
}

print(evaluate(plot, data))
```

## Accessing Root-Level Data

Each series can reference both local data and root-level configuration:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("shared_xlabel"),  # From root
        ylabel=Ref("shared_ylabel"),  # From root
        title=Ref("title"),           # From root
        xmin=Ref("x_range.min"),      # From root
        xmax=Ref("x_range.max"),      # From root
        plots=Iter(
            Ref("experiments"),
            template=AddPlot(
                color=Ref("color"),     # From current experiment
                mark=Ref("marker"),     # From current experiment
                coords=Coordinates(
                    x=Ref("x"),         # From current experiment
                    y=Ref("y")          # From current experiment
                ),
            )
        ),
        legend=Iter(Ref("experiments"), template=Ref("name")),
    )
)

data = {
    # Root-level shared configuration
    "title": "All Experiments",
    "shared_xlabel": "Time (s)",
    "shared_ylabel": "Value",
    "x_range": {"min": 0, "max": 10},

    # Per-experiment data
    "experiments": [
        {
            "name": "Exp 1",
            "color": "blue",
            "marker": "*",
            "x": [0, 1, 2],
            "y": [1, 2, 4],
        },
        {
            "name": "Exp 2",
            "color": "red",
            "marker": "square*",
            "x": [0, 1, 2],
            "y": [2, 3, 5],
        },
    ],
}

print(evaluate(plot, data))
```

## Different Data Lengths

Each series can have different numbers of points:

```python
data = {
    "title": "Variable-Length Series",
    "x_label": "X",
    "y_label": "Y",
    "series": [
        {
            "name": "Short Series",
            "color": "blue",
            "marker": "*",
            "data": [{"x": 0, "y": 1}, {"x": 1, "y": 2}],  # 2 points
        },
        {
            "name": "Long Series",
            "color": "red",
            "marker": "square*",
            "data": [
                {"x": 0, "y": 1},
                {"x": 0.5, "y": 1.5},
                {"x": 1, "y": 2},
                {"x": 1.5, "y": 2.5},
                {"x": 2, "y": 3},
            ],  # 5 points
        },
    ],
}
```

## Mixed Static and Dynamic Series

Combine predefined series with dynamic ones:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        plots=[
            # Static baseline series
            AddPlot(
                color="gray",
                style="dashed",
                no_marks=True,
                coords=Coordinates([(0, 0), (10, 10)]),
            ),
            # Dynamic data series
            *Iter(
                Ref("measurements"),
                template=AddPlot(
                    color=Ref("color"),
                    mark="*",
                    coords=Coordinates(
                        Iter(Ref("points"), x=Ref("x"), y=Ref("y"))
                    ),
                )
            ),
        ],
        legend=["Baseline", *Iter(Ref("measurements"), template=Ref("label"))],
    )
)
```

!!! note "Using * with Iter"
    When mixing static and dynamic content, you can use Python's unpacking operator `*` with `Iter`.

## Different Series Types

Mix scatter plots, line plots, and other styles:

```python
data = {
    "title": "Mixed Plot Types",
    "x_label": "X",
    "y_label": "Y",
    "series": [
        {
            "name": "Measurements",
            "color": "blue",
            "marker": "o",
            "plot_type": "scatter",
            "data": [{"x": i, "y": i**2 + np.random.normal(0, 0.5)}
                     for i in range(10)],
        },
        {
            "name": "Trend",
            "color": "red",
            "marker": "none",
            "plot_type": "line",
            "data": [{"x": i, "y": i**2} for i in range(10)],
        },
    ],
}

# In template, use Cond to set only_marks based on plot_type
from texer import Cond

plots=Iter(
    Ref("series"),
    template=AddPlot(
        color=Ref("color"),
        mark=Ref("marker"),
        only_marks=Cond(Ref("plot_type") == "scatter", True, False),
        coords=Coordinates(Iter(Ref("data"), x=Ref("x"), y=Ref("y"))),
    )
)
```

## Real-World Example: CSV with Multiple Columns

```python
import pandas as pd
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

# Read CSV with multiple measurement columns
df = pd.read_csv("sensors.csv")  # Columns: time, sensor1, sensor2, sensor3

# Prepare data
time = df['time'].values
series = [
    {
        "name": "Sensor 1",
        "color": "blue",
        "marker": "*",
        "x": time,
        "y": df['sensor1'].values,
    },
    {
        "name": "Sensor 2",
        "color": "red",
        "marker": "square*",
        "x": time,
        "y": df['sensor2'].values,
    },
    {
        "name": "Sensor 3",
        "color": "green",
        "marker": "triangle*",
        "x": time,
        "y": df['sensor3'].values,
    },
]

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Value",
        title="Multi-Sensor Data",
        grid=True,
        plots=Iter(
            Ref("series"),
            template=AddPlot(
                color=Ref("color"),
                mark=Ref("marker"),
                coords=Coordinates(x=Ref("x"), y=Ref("y")),
            )
        ),
        legend=Iter(Ref("series"), template=Ref("name")),
        legend_pos="outer north east",
    )
)

data = {"series": series}
print(evaluate(plot, data))
```

## Automatic Color/Marker Assignment

Use cycle lists for automatic styling (see [Advanced Options](advanced.md#cycle-lists)):

```python
plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        cycle_list=[
            {"color": "blue", "mark": "*"},
            {"color": "red", "mark": "square*"},
            {"color": "green", "mark": "triangle*"},
        ],
        plots=Iter(
            Ref("datasets"),
            template=AddPlot(
                # No color/mark needed - cycle list applies automatically
                coords=Coordinates(Iter(Ref("points"), x=Ref("x"), y=Ref("y"))),
            )
        ),
        legend=Iter(Ref("datasets"), template=Ref("name")),
    )
)
```

## Performance Considerations

For many series (>20), consider:

1. **Sampling**: Reduce data points per series
2. **Cycle lists**: Avoid specifying colors individually
3. **no_marks**: Disable markers for smoother rendering

```python
# Sample every 10th point
sampled_data = data[::10]

# Or use cycle list for automatic styling
cycle_list=["blue", "red", "green", "orange", "purple"]
```

## Next Steps

- [GroupPlots](groupplots.md) - Multiple subplots in a grid
- [Advanced Options](advanced.md) - Cycle lists and advanced styling
- [Iter Spec](../specs/iter.md) - Deep dive into Iter functionality
