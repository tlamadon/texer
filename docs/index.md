# texer

Generate LaTeX tables and figures (PGFPlots) with Python using a glom-style spec system.

## What is texer?

texer is a Python library that makes it easy to generate LaTeX tables and PGFPlots programmatically. Instead of writing string templates or manually building LaTeX code, you:

1. **Define the structure** of your table or plot using Python classes
2. **Create specs** that describe where data comes from
3. **Provide your data** as plain Python dicts/lists

texer then evaluates the specs against your data to produce valid LaTeX.

```
Structure + Specs + Data → LaTeX
```

## Quick Example

=== "Tables"

    ```python
    from texer import Table, Tabular, Row, Ref, Iter, Format, evaluate

    # Define structure with specs
    table = Table(
        Tabular(
            columns="lcc",
            header=Row("Experiment", "Result", "Error"),
            rows=Iter(
                Ref("experiments"),
                template=Row(
                    Ref("name"),
                    Format(Ref("result"), ".3f"),
                    Format(Ref("error"), ".1%"),
                )
            ),
            toprule=True,
            bottomrule=True,
        ),
        caption=Ref("table_title"),
        label="tab:results",
    )

    # Provide data
    data = {
        "table_title": "Experimental Results",
        "experiments": [
            {"name": "Trial A", "result": 3.14159, "error": 0.023},
            {"name": "Trial B", "result": 2.71828, "error": 0.015},
        ]
    }

    print(evaluate(table, data))
    ```

=== "Plots"

    ```python
    from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

    plot = PGFPlot(
        Axis(
            xlabel=Ref("x_label"),
            ylabel=Ref("y_label"),
            title=Ref("title"),
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    coords=Coordinates(
                        Iter(Ref("measurements"), x=Ref("time"), y=Ref("value"))
                    ),
                )
            ],
            legend=[Ref("series_name")],
        )
    )

    data = {
        "title": "Temperature Over Time",
        "x_label": "Time (hours)",
        "y_label": "Temperature (°C)",
        "series_name": "Sensor 1",
        "measurements": [
            {"time": 0, "value": 20.5},
            {"time": 1, "value": 22.3},
            {"time": 2, "value": 25.1},
        ]
    }

    print(evaluate(plot, data))
    ```

## Features

- **Data-driven**: Separate structure from data for maximum flexibility
- **Type-safe**: Full type hints and mypy support
- **Glom-style specs**: Familiar pattern for data extraction and transformation
- **LaTeX best practices**: Automatic escaping, booktabs-style tables, proper PGFPlots formatting
- **NumPy integration**: Direct support for NumPy arrays in plots
- **Compile to PDF**: Built-in support for compiling directly to PDF

## Next Steps

- [Installation](getting-started/installation.md) - Get texer installed
- [Mental Model](getting-started/mental-model.md) - Understand how texer works
- [Core Concepts](getting-started/core-concepts.md) - Learn about specs and evaluation
- [Basic Tables](tables/basic.md) - Create your first table
- [Basic Plots](plots/basic.md) - Create your first plot
