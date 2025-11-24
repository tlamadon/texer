# texer

Generate LaTeX tables and figures (PGFPlots) with Python using a glom-style spec system.

## Installation

```bash
pip install -e .
```

## Mental Model

texer follows a simple principle: **describe your LaTeX structure once, then fill it with any data**.

Instead of writing string templates or manually building LaTeX, you define:
1. The **structure** of your table or plot using Python classes
2. **Specs** that describe where data comes from
3. Your **data** as plain Python dicts/lists

texer then evaluates the specs against your data to produce valid LaTeX.

```
Structure + Specs + Data → LaTeX
```

## Core Concepts

### Specs: Describing Data Access

Specs are lazy descriptors that tell texer how to extract and transform data.

```python
from texer import Ref, Iter, Format, Cond, Raw

# Ref: Access data by path (glom-style dot notation)
Ref("name")              # data["name"]
Ref("user.email")        # data["user"]["email"]
Ref("items.0.value")     # data["items"][0]["value"]
Ref("x", default=0)      # with default value

# Iter: Loop over collections
Iter(Ref("rows"), template=Row(...))  # iterate and apply template
Iter(Ref("points"), x=Ref("x"), y=Ref("y"))  # extract coordinates

# Format: Python format specs
Format(Ref("price"), ".2f")   # "3.14"
Format(Ref("ratio"), ".1%")   # "25.0%"

# Cond: Conditional logic
Cond(Ref("x") > 5, "high", "low")
Cond(Ref("active"), Raw(r"\checkmark"), "")

# Raw: Unescaped LaTeX
Raw(r"\textbf{bold}")
Raw(r"\hline")
```

### The Evaluation Flow

```
1. You define structure with Specs embedded
2. Call evaluate(structure, data)
3. texer walks the structure, resolving Specs against data
4. LaTeX strings are produced with proper escaping
```

---

## Building Tables

### Mental Model for Tables

Think of tables as nested structures:

```
Table (floating environment)
└── Tabular (the actual grid)
    ├── Header (Row)
    └── Body (list of Rows or Iter)
        └── Cells (values, Refs, or Cell objects)
```

### Basic Table

```python
from texer import Table, Tabular, Row, evaluate

# Define structure
table = Table(
    Tabular(
        columns="lcc",  # left, center, center
        header=Row("Name", "Value", "Unit"),
        rows=[
            Row("Length", "42", "m"),
            Row("Mass", "100", "kg"),
        ],
        toprule=True,
        bottomrule=True,
    ),
    caption="Physical Properties",
    label="tab:properties",
)

# Generate LaTeX (no data needed for static tables)
print(evaluate(table, {}))
```

Output:
```latex
\begin{table}[htbp]
  \centering
  \caption{Physical Properties}
  \label{tab:properties}
  \begin{tabular}{lcc}
    \toprule
    Name & Value & Unit \\
    \midrule
    Length & 42 & m \\
    Mass & 100 & kg \\
    \bottomrule
  \end{tabular}
\end{table}
```

### Data-Driven Table

The power comes from using Specs to pull data dynamically:

```python
from texer import Table, Tabular, Row, Ref, Iter, Format, evaluate

# Define structure with Specs
table = Table(
    Tabular(
        columns="lcc",
        header=Row("Experiment", "Result", "Error"),
        rows=Iter(
            Ref("experiments"),  # iterate over data["experiments"]
            template=Row(
                Ref("name"),                    # each item's "name"
                Format(Ref("result"), ".3f"),   # formatted number
                Format(Ref("error"), ".1%"),    # as percentage
            )
        ),
        toprule=True,
        bottomrule=True,
    ),
    caption=Ref("table_title"),  # dynamic caption
    label="tab:results",
)

# Provide data
data = {
    "table_title": "Experimental Results",
    "experiments": [
        {"name": "Trial A", "result": 3.14159, "error": 0.023},
        {"name": "Trial B", "result": 2.71828, "error": 0.015},
        {"name": "Trial C", "result": 1.41421, "error": 0.042},
    ]
}

print(evaluate(table, data))
```

### Conditional Formatting

Use `Cond` for conditional styling:

```python
from texer import Tabular, Row, Cell, Ref, Iter, Cond, Raw, Format, evaluate

table = Tabular(
    columns="lcc",
    header=Row("Test", "Score", "Status"),
    rows=Iter(
        Ref("tests"),
        template=Row(
            Ref("name"),
            Format(Ref("score"), ".1f"),
            # Conditional: green PASS if score >= 70, else red FAIL
            Cond(
                Ref("score") >= 70,
                Raw(r"\textcolor{green}{PASS}"),
                Raw(r"\textcolor{red}{FAIL}"),
            ),
        )
    ),
    toprule=True,
    bottomrule=True,
)

data = {
    "tests": [
        {"name": "Unit Tests", "score": 95.5},
        {"name": "Integration", "score": 62.0},
        {"name": "E2E Tests", "score": 88.2},
    ]
}

print(evaluate(table, data))
```

### Cell Formatting

Use `Cell` for fine-grained control:

```python
from texer import Row, Cell, Ref, Cond

Row(
    Cell(Ref("name"), bold=True),                    # always bold
    Cell(Ref("value"), italic=True),                 # always italic
    Cell(Ref("x"), bold=Cond(Ref("important"), True, False)),  # conditional bold
)
```

### Multi-column and Multi-row

```python
from texer import Row, MultiColumn, MultiRow

# Spanning columns
Row(MultiColumn(3, "c", "Header Spanning 3 Columns"))

# Spanning rows (requires multirow package)
Row(MultiRow(2, "Category"), "Value 1", "Unit 1")
```

---

## Building PGFPlots

### Mental Model for Plots

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

### Basic Plot with Static Data

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

Output:
```latex
\begin{tikzpicture}
  \begin{axis}[xlabel={Time (s)}, ylabel={Distance (m)}]
    \addplot[color=blue, mark=*] coordinates {(0, 0) (1, 2) (2, 8) (3, 18)};
  \end{axis}
\end{tikzpicture}
```

### Data-Driven Plot

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        legend_pos="north west",
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
        {"time": 3, "value": 23.8},
    ]
}

print(evaluate(plot, data))
```

### Multiple Series

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        legend_pos="south east",
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates(
                    Iter(Ref("series_a"), x=Ref("x"), y=Ref("y"))
                ),
            ),
            AddPlot(
                color="red",
                mark="square*",
                style="dashed",
                coords=Coordinates(
                    Iter(Ref("series_b"), x=Ref("x"), y=Ref("y"))
                ),
            ),
        ],
        legend=["Series A", "Series B"],
    )
)

data = {
    "series_a": [{"x": 0, "y": 1}, {"x": 1, "y": 4}, {"x": 2, "y": 9}],
    "series_b": [{"x": 0, "y": 2}, {"x": 1, "y": 3}, {"x": 2, "y": 5}],
}

print(evaluate(plot, data))
```

### Mathematical Expressions

For function plots, use expressions instead of coordinates:

```python
from texer import PGFPlot, Axis, AddPlot, evaluate

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
            AddPlot(
                expression="cos(deg(x))",
                domain="-5:5",
                samples=100,
                color="red",
                style="dashed",
                no_marks=True,
            ),
        ],
        legend=[r"$\sin(x)$", r"$\cos(x)$"],
    )
)

print(evaluate(plot, {}))
```

### Axis Options Reference

```python
Axis(
    # Labels
    xlabel="X Label",
    ylabel="Y Label",
    zlabel="Z Label",      # for 3D
    title="Plot Title",

    # Limits
    xmin=0, xmax=10,
    ymin=-5, ymax=5,

    # Legend
    legend=["A", "B"],
    legend_pos="north west",  # north west, south east, outer north east, etc.

    # Grid
    grid=True,              # or "major", "minor", "both"

    # Dimensions
    width="10cm",
    height="6cm",

    # Axis type
    axis_type="axis",       # or "semilogxaxis", "semilogyaxis", "loglogaxis"

    # Raw options escape hatch
    _raw_options="some pgfplots option=value",
)
```

### AddPlot Options Reference

```python
AddPlot(
    # Data source (one of these)
    coords=Coordinates([...]),
    expression="x^2",

    # Expression options
    domain="0:10",
    samples=100,

    # Style
    color="blue",
    mark="*",               # *, o, square*, triangle*, etc.
    style="dashed",         # dashed, dotted, etc.
    line_width="1pt",
    thick=True,

    # Mark control
    only_marks=True,        # scatter plot
    no_marks=True,          # line only
    smooth=True,            # smooth curve

    # 3D
    surf=True,              # surface plot
    mesh=True,              # mesh plot

    # Raw options escape hatch
    _raw_options="some option",
)
```

---

## Escape Hatches

When you need raw LaTeX control:

```python
# Raw LaTeX in content
Raw(r"\textbf{bold} and \textit{italic}")

# Raw options on any element
Axis(..., _raw_options="extra pgf option=value")
AddPlot(..., _raw_options="mark options={fill=white}")
Tabular(..., _raw_options="@{}l@{}")
```

---

## Quick Reference

### Specs

| Spec | Purpose | Example |
|------|---------|---------|
| `Ref(path)` | Access data | `Ref("user.name")` |
| `Iter(source, template=...)` | Loop over list | `Iter(Ref("items"), template=Row(...))` |
| `Iter(source, x=..., y=...)` | Extract coordinates | `Iter(Ref("points"), x=Ref("x"), y=Ref("y"))` |
| `Format(value, fmt)` | Format value | `Format(Ref("x"), ".2f")` |
| `Cond(test, if_true, if_false)` | Conditional | `Cond(Ref("x") > 0, "pos", "neg")` |
| `Raw(latex)` | Unescaped LaTeX | `Raw(r"\hline")` |

### Comparison Operators (for Cond)

```python
Ref("x") > 5      # greater than
Ref("x") < 5      # less than
Ref("x") >= 5     # greater or equal
Ref("x") <= 5     # less or equal
Ref("x") == 5     # equal
Ref("x") != 5     # not equal

# Combine with & (and) and | (or)
(Ref("x") > 0) & (Ref("x") < 10)
(Ref("x") < 0) | (Ref("x") > 10)
```

### Table Classes

| Class | Purpose |
|-------|---------|
| `Table` | Floating table environment |
| `Tabular` | The tabular grid |
| `Row` | A table row |
| `Cell` | A cell with formatting options |
| `MultiColumn` | Cell spanning columns |
| `MultiRow` | Cell spanning rows |

### Plot Classes

| Class | Purpose |
|-------|---------|
| `PGFPlot` | tikzpicture wrapper |
| `Axis` | Axis environment |
| `AddPlot` | A single plot/series |
| `Coordinates` | Data points for a plot |
| `Legend` | Legend entries |

---

## Required LaTeX Packages

For tables with rules:
```latex
\usepackage{booktabs}
```

For colored text:
```latex
\usepackage{xcolor}
```

For plots:
```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
```

For multirow cells:
```latex
\usepackage{multirow}
```
