# Bar Charts

Create bar charts using the `_raw_options` parameter with `ybar` (vertical bars) or `xbar` (horizontal bars).

## Vertical Bar Chart

The most common bar chart type uses vertical bars.

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Region",
        ylabel="Sales (M\$)",
        ymin=0,
        xtick=[0, 1, 2, 3],
        xticklabels=["North", "South", "East", "West"],
        width="10cm",
        height="7cm",
        plots=[
            AddPlot(
                color="blue!60",
                coords=Coordinates([(0, 25), (1, 40), (2, 35), (3, 50)]),
                _raw_options="ybar, fill=blue!60"
            )
        ],
    )
)

print(evaluate(plot, {}))
```

![Vertical Bar Chart](../assets/images/plots/bar_vertical.png)

## Horizontal Bar Chart

For horizontal bars, use `xbar` instead.

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Revenue (M\$)",
        ylabel="Product",
        xmin=0,
        ytick=[0, 1, 2, 3],
        yticklabels=["Product A", "Product B", "Product C", "Product D"],
        width="10cm",
        height="7cm",
        plots=[
            AddPlot(
                color="red!60",
                coords=Coordinates([(25, 0), (40, 1), (35, 2), (50, 3)]),
                _raw_options="xbar, fill=red!60"
            )
        ],
    )
)

print(evaluate(plot, {}))
```

![Horizontal Bar Chart](../assets/images/plots/bar_horizontal.png)

## Grouped Bar Chart

Create grouped bars by plotting multiple series with appropriate bar width and positioning.

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Quarter",
        ylabel="Revenue (M\$)",
        ymin=0,
        xtick=[0, 1, 2, 3],
        xticklabels=["Q1", "Q2", "Q3", "Q4"],
        legend=["Product A", "Product B", "Product C"],
        legend_pos="north west",
        width="12cm",
        height="8cm",
        plots=[
            AddPlot(
                color="blue!60",
                coords=Coordinates([(0, 20), (1, 30), (2, 25), (3, 35)]),
                _raw_options="ybar, fill=blue!60, bar width=7pt"
            ),
            AddPlot(
                color="red!60",
                coords=Coordinates([(0, 15), (1, 25), (2, 30), (3, 28)]),
                _raw_options="ybar, fill=red!60, bar width=7pt"
            ),
            AddPlot(
                color="green!60",
                coords=Coordinates([(0, 18), (1, 22), (2, 28), (3, 32)]),
                _raw_options="ybar, fill=green!60, bar width=7pt"
            ),
        ],
    )
)

print(evaluate(plot, {}))
```

![Grouped Bar Chart](../assets/images/plots/bar_grouped.png)

## Stacked Bar Chart

Create stacked bars using the `stack plots` option.

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Quarter",
        ylabel="Revenue (M\$)",
        ymin=0,
        xtick=[0, 1, 2, 3],
        xticklabels=["Q1", "Q2", "Q3", "Q4"],
        legend=["Hardware", "Software", "Services"],
        legend_pos="north west",
        width="10cm",
        height="7cm",
        _raw_options="ybar stacked, bar width=15pt",
        plots=[
            AddPlot(
                color="blue!60",
                coords=Coordinates([(0, 20), (1, 25), (2, 22), (3, 28)]),
                _raw_options="fill=blue!60"
            ),
            AddPlot(
                color="red!60",
                coords=Coordinates([(0, 15), (1, 18), (2, 20), (3, 22)]),
                _raw_options="fill=red!60"
            ),
            AddPlot(
                color="green!60",
                coords=Coordinates([(0, 10), (1, 12), (2, 15), (3, 18)]),
                _raw_options="fill=green!60"
            ),
        ],
    )
)

print(evaluate(plot, {}))
```

![Stacked Bar Chart](../assets/images/plots/bar_stacked.png)

## Dynamic Bar Charts with Data

Use `Iter` and `Ref` for data-driven bar charts.

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Iter, Ref, evaluate

plot = PGFPlot(
    Axis(
        xlabel="Category",
        ylabel=Ref("ylabel"),
        title=Ref("title"),
        ymin=0,
        xtick=Ref("xtick_positions"),
        xticklabels=Ref("categories"),
        width="10cm",
        height="7cm",
        plots=[
            AddPlot(
                color="purple!60",
                coords=Coordinates(
                    Iter(Ref("data"), x=Ref("x"), y=Ref("y"))
                ),
                _raw_options="ybar, fill=purple!60, bar width=12pt"
            )
        ],
    )
)

data = {
    "title": "Monthly Performance",
    "ylabel": "Score",
    "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
    "xtick_positions": [0, 1, 2, 3, 4],
    "data": [
        {"x": 0, "y": 85},
        {"x": 1, "y": 92},
        {"x": 2, "y": 78},
        {"x": 3, "y": 95},
        {"x": 4, "y": 88},
    ],
}

print(evaluate(plot, data))
```

![Dynamic Bar Chart](../assets/images/plots/bar_dynamic.png)

## Key Options

### Bar Width
Control bar width with the `bar width` option:
```python
_raw_options="ybar, bar width=10pt"
```

### Bar Spacing
For grouped bars, adjust spacing with `bar shift`:
```python
_raw_options="ybar, bar shift=-5pt"  # Shift left
_raw_options="ybar, bar shift=5pt"   # Shift right
```

### Fill and Border
Customize appearance:
```python
_raw_options="ybar, fill=blue!60, draw=blue!80!black"
```

### Stacked Bars
Use `ybar stacked` or `xbar stacked` on the Axis:
```python
Axis(
    _raw_options="ybar stacked, bar width=15pt",
    # ...
)
```

## Tips

1. **Set minimum to 0**: Bar charts typically start at 0, use `ymin=0` or `xmin=0`
2. **Use custom tick labels**: Control category names with `xticklabels` or `yticklabels`
3. **Add grid**: Include `grid=True` for better readability
4. **Choose good colors**: Use color blends like `blue!60` for professional appearance
5. **Adjust bar width**: Default may be too wide/narrow for your data
