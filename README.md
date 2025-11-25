# texer

Generate LaTeX tables and figures (PGFPlots) with Python using a glom-style spec system.

## Installation

```bash
pip install texer
```

## Quick Start

### Tables

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

### Plots

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
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

### Cycle Lists

PGFPlots cycle lists allow you to define a sequence of styles that are automatically applied to successive `\addplot` commands:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates

# Using a predefined cycle list
plot = PGFPlot(
    Axis(
        cycle_list_name="color list",
        plots=[
            AddPlot(coords=Coordinates([(0, 0), (1, 1), (2, 4)])),
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 3)])),
        ],
    )
)

# Custom cycle list with style dictionaries
plot = PGFPlot(
    Axis(
        cycle_list=[
            {"color": "blue", "mark": "*", "line width": "2pt"},
            {"color": "red", "mark": "square*", "line width": "2pt"},
            {"color": "green", "mark": "triangle*", "line width": "2pt"},
        ],
        plots=[
            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 4)])),
            AddPlot(coords=Coordinates([(0, 2), (1, 3), (2, 5)])),
        ],
    )
)

# Simple color cycle
plot = PGFPlot(
    Axis(
        cycle_list=["blue", "red", "green"],
        plots=[
            AddPlot(coords=Coordinates([(0, 0), (1, 1)])),
            AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
        ],
    )
)
```

## Documentation

For complete documentation, visit: **[Documentation Site](https://your-docs-url.com)**

Or build the docs locally:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open http://127.0.0.1:8000

## Key Features

- **Data-driven**: Separate structure from data
- **Type-safe**: Full type hints and mypy support
- **Glom-style specs**: Familiar pattern for data extraction
- **LaTeX best practices**: Automatic escaping, booktabs tables
- **NumPy integration**: Direct support for NumPy arrays
- **PDF compilation**: Built-in `compile_to_pdf()` method

## Core Concepts

texer uses **specs** to describe how to extract and transform data:

- **`Ref("path")`** - Access data by path (e.g., `Ref("user.name")`)
- **`Iter(source, template=...)`** - Loop over collections
- **`Format(value, ".2f")`** - Format values
- **`Cond(test, if_true, if_false)`** - Conditional logic
- **`Raw(r"\textbf{bold}")`** - Unescaped LaTeX

See the [Core Concepts](docs/getting-started/core-concepts.md) guide for details.

## LaTeX Requirements

For PDF compilation, you need a LaTeX distribution:

- **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-pictures`
- **macOS**: `brew install --cask mactex`
- **Windows**: [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src
```

## License

MIT
