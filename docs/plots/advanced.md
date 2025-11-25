# Advanced Plot Options

Complete reference for all plot customization options.

## Cycle Lists

PGFPlots cycle lists define a sequence of styles that are automatically applied to successive `\addplot` commands. This is useful for maintaining consistent styling across multiple plots without manually specifying colors and markers for each one.

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

**Output:**

![Cycle list example](../assets/images/plots/cycle_list.png)

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
