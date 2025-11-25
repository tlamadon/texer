# Data-Driven Plots

Generate plots dynamically from data using **Ref** and **Iter** specs. This separates plot structure from data, making it easy to generate multiple plots from different datasets.

## Core Concepts

- **`Ref("path")`** - Extract values from data (e.g., `Ref("xlabel")`)
- **`Iter(source, template=...)`** - Loop over collections to generate plots
- **Separation of structure and data** - Define once, render with different data

## Using Ref for Labels

Replace static strings with dynamic references:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("plot_title"),
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates([(0, 1), (1, 2), (2, 4)]),
            )
        ],
    )
)

data = {
    "x_label": "Time (hours)",
    "y_label": "Temperature (°C)",
    "plot_title": "Temperature Over Time",
}

print(evaluate(plot, data))
```

This produces a plot with labels pulled from the data dictionary.

## Dynamic Coordinates with Iter

Use `Iter` to generate coordinates from a list of data points:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Value",
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates(
                    Iter(Ref("measurements"), x=Ref("time"), y=Ref("value"))
                ),
            )
        ],
    )
)

data = {
    "measurements": [
        {"time": 0, "value": 1.2},
        {"time": 1, "value": 2.5},
        {"time": 2, "value": 4.1},
        {"time": 3, "value": 7.8},
    ]
}

print(evaluate(plot, data))
```

The `Iter` spec:
1. Takes `Ref("measurements")` as the source (list of dicts)
2. For each item, extracts `x=Ref("time")` and `y=Ref("value")`
3. Generates coordinates from the data

## Complete Example

Combine `Ref` and `Iter` for fully data-driven plots:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        grid=True,
        xmin=Ref("x_min"),
        xmax=Ref("x_max"),
        plots=[
            AddPlot(
                color=Ref("color"),
                mark=Ref("marker"),
                coords=Coordinates(
                    Iter(Ref("data_points"), x=Ref("x"), y=Ref("y"))
                ),
            )
        ],
        legend=[Ref("series_name")],
        legend_pos="north west",
    )
)

data = {
    "title": "Experimental Results",
    "x_label": "Time (h)",
    "y_label": "Concentration (mol/L)",
    "x_min": 0,
    "x_max": 10,
    "color": "blue",
    "marker": "*",
    "series_name": "Experiment A",
    "data_points": [
        {"x": 0, "y": 0.5},
        {"x": 2, "y": 1.2},
        {"x": 4, "y": 2.1},
        {"x": 6, "y": 3.5},
        {"x": 8, "y": 5.2},
        {"x": 10, "y": 7.8},
    ],
}

latex_code = evaluate(plot, data)
print(latex_code)
```

Now you can render the same plot with different datasets:

```python
# Different experiment
data2 = {
    "title": "Experimental Results - Trial 2",
    "x_label": "Time (h)",
    "y_label": "Concentration (mol/L)",
    "x_min": 0,
    "x_max": 10,
    "color": "red",
    "marker": "square*",
    "series_name": "Experiment B",
    "data_points": [
        {"x": 0, "y": 0.3},
        {"x": 2, "y": 0.9},
        {"x": 4, "y": 1.8},
        {"x": 6, "y": 3.2},
        {"x": 8, "y": 5.0},
        {"x": 10, "y": 7.5},
    ],
}

latex_code2 = evaluate(plot, data2)
```

## Nested References

Access nested data using dot notation:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("config.labels.x"),
        ylabel=Ref("config.labels.y"),
        plots=[
            AddPlot(
                color=Ref("config.style.color"),
                coords=Coordinates(
                    Iter(Ref("experiment.results"), x=Ref("t"), y=Ref("val"))
                ),
            )
        ],
    )
)

data = {
    "config": {
        "labels": {"x": "Time", "y": "Value"},
        "style": {"color": "blue"},
    },
    "experiment": {
        "results": [
            {"t": 0, "val": 1},
            {"t": 1, "val": 2},
            {"t": 2, "val": 4},
        ]
    },
}

print(evaluate(plot, data))
```

## From NumPy Arrays

Coordinates work seamlessly with NumPy arrays:

```python
import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                thick=True,
                no_marks=True,
                coords=Coordinates(x=Ref("x_data"), y=Ref("y_data")),
            )
        ],
    )
)

# Generate data
x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

data = {
    "x_label": "$x$",
    "y_label": "$\\sin(x)$",
    "x_data": x,
    "y_data": y,
}

print(evaluate(plot, data))
```

## Multiple Datasets from Lists

Use `Ref` to select from lists:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        plots=[
            AddPlot(
                color=Ref("datasets.0.color"),
                coords=Coordinates(
                    Iter(Ref("datasets.0.points"), x=Ref("x"), y=Ref("y"))
                ),
            ),
            AddPlot(
                color=Ref("datasets.1.color"),
                coords=Coordinates(
                    Iter(Ref("datasets.1.points"), x=Ref("x"), y=Ref("y"))
                ),
            ),
        ],
        legend=[Ref("datasets.0.name"), Ref("datasets.1.name")],
    )
)

data = {
    "datasets": [
        {
            "name": "Series A",
            "color": "blue",
            "points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 4}],
        },
        {
            "name": "Series B",
            "color": "red",
            "points": [{"x": 0, "y": 1}, {"x": 1, "y": 2}, {"x": 2, "y": 3}],
        },
    ]
}

print(evaluate(plot, data))
```

## Default Values

Provide fallback values with `Ref`:

```python
from texer import Ref

Axis(
    xlabel=Ref("x_label", default="X Axis"),  # Uses "X Axis" if not in data
    ylabel=Ref("y_label", default="Y Axis"),
    plots=[...],
)
```

## Combining Static and Dynamic

Mix static configuration with dynamic data:

```python
plot = PGFPlot(
    Axis(
        # Static configuration
        grid=True,
        width="10cm",
        height="6cm",
        legend_pos="north west",

        # Dynamic labels
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),

        # Dynamic plots
        plots=[
            AddPlot(
                color="blue",  # Static color
                mark="*",       # Static marker
                coords=Coordinates(
                    Iter(Ref("points"), x=Ref("x"), y=Ref("y"))  # Dynamic data
                ),
            )
        ],
        legend=[Ref("legend_text")],
    )
)
```

## Real-World Example: CSV Data

```python
import pandas as pd
from texer import PGFPlot, Axis, AddPlot, Coordinates, Iter, Ref, evaluate

# Read CSV
df = pd.read_csv("experiment_data.csv")

# Convert to list of dicts
data_points = df.to_dict('records')

plot = PGFPlot(
    Axis(
        xlabel="Time (s)",
        ylabel="Temperature (K)",
        title="Temperature Measurements",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates(
                    Iter(Ref("measurements"), x=Ref("time"), y=Ref("temp"))
                ),
            )
        ],
    )
)

data = {"measurements": data_points}

latex_code = evaluate(plot, data)
print(latex_code)
```

## Benefits

**Reusability**: Define the plot structure once, use with multiple datasets

```python
# Same plot definition
for experiment in experiments:
    data = load_experiment_data(experiment)
    latex = evaluate(plot, data)
    save_plot(latex, f"{experiment}.tex")
```

**Testability**: Easy to test with mock data

```python
test_data = {
    "x_label": "Test X",
    "y_label": "Test Y",
    "data_points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}],
}
latex = evaluate(plot, test_data)
assert "Test X" in latex
```

**Maintainability**: Change plot structure without touching data loading code

## Next Steps

- [Multiple Series](multiple-series.md) - Generate multiple plot series from data
- [Format Spec](../specs/format.md) - Format numbers and values
- [Cond Spec](../specs/cond.md) - Conditional logic in plots
