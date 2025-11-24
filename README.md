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

**Single Plot:**
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

**Multiple Subplots (GroupPlot):**
```
PGFPlot (tikzpicture wrapper)
└── GroupPlot (grid layout container)
    ├── Group Options (size, spacing, label positioning)
    └── Plots (list of NextGroupPlot)
        └── NextGroupPlot (individual subplot)
            ├── Options (xlabel, ylabel, title, ...)
            ├── Plots (list of AddPlot)
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

### Dynamic Multiple Series with Iter

For more flexibility, you can use `Iter` to dynamically generate multiple `AddPlot` instances from a list of series specifications in your data. This is especially useful when the number of series isn't known ahead of time:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

# Define structure where plots themselves are generated from data
plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        legend_pos="north west",
        grid=True,
        # Iterate over series list to create multiple AddPlot instances
        plots=Iter(
            Ref("series"),  # List of series specifications
            template=AddPlot(
                color=Ref("color"),    # Each series has its own color
                mark=Ref("marker"),    # and marker style
                coords=Coordinates(
                    Iter(Ref("data"), x=Ref("t"), y=Ref("value"))
                ),
            )
        ),
        legend=Iter(Ref("series"), template=Ref("name")),
    )
)

# Data with multiple series
data = {
    "title": "Temperature Sensors",
    "x_label": "Time (hours)",
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
                {"t": 0, "value": 20.1},
                {"t": 1, "value": 22.8},
                {"t": 2, "value": 25.5},
            ],
        },
    ],
}

print(evaluate(plot, data))
```

This pattern scales naturally - adding a fourth sensor is just adding another entry to the `series` list in your data. No changes to the structure needed!

The same approach works with NumPy arrays:

```python
import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$f(x)$",
        grid=True,
        legend_pos="south east",
        plots=Iter(
            Ref("series"),
            template=AddPlot(
                color=Ref("color"),
                no_marks=True,
                thick=True,
                style=Ref("line_style"),
                coords=Coordinates(x=Ref("x"), y=Ref("y")),  # Direct array refs
            )
        ),
        legend=Iter(Ref("series"), template=Ref("label")),
    )
)

# Generate data with NumPy
x = np.linspace(0, 2*np.pi, 100)
data = {
    "series": [
        {"label": r"$\sin(x)$", "color": "blue", "line_style": "solid",
         "x": x, "y": np.sin(x)},
        {"label": r"$\cos(x)$", "color": "red", "line_style": "dashed",
         "x": x, "y": np.cos(x)},
        {"label": r"$\sin(2x)$", "color": "green", "line_style": "dotted",
         "x": x, "y": np.sin(2*x)},
    ]
}

print(evaluate(plot, data))
```

### Using NumPy Arrays

`Coordinates` supports direct creation from NumPy arrays (or plain Python lists) using separate `x` and `y` parameters:

```python
import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

# Generate data with NumPy
x = np.linspace(0, 2*np.pi, 100)
y1 = np.sin(x)
y2 = np.cos(x)

plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$f(x)$",
        grid=True,
        legend_pos="south east",
        plots=[
            AddPlot(
                color="blue",
                thick=True,
                no_marks=True,
                coords=Coordinates(x=x, y=y1),  # Direct from NumPy arrays!
            ),
            AddPlot(
                color="red",
                thick=True,
                no_marks=True,
                style="dashed",
                coords=Coordinates(x=x, y=y2),
            ),
        ],
        legend=[r"$\sin(x)$", r"$\cos(x)$"],
    )
)

print(evaluate(plot, {}))
```

This also works with plain Python lists:

```python
x = [0, 1, 2, 3, 4]
y = [0, 1, 4, 9, 16]
coords = Coordinates(x=x, y=y)
```

And for 3D coordinates:

```python
coords = Coordinates(x=[0, 1, 2], y=[0, 1, 2], z=[0, 1, 4])
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

### GroupPlots: Multiple Subplots

Use `GroupPlot` to create multiple plots in a grid layout:

```python
from texer import PGFPlot, GroupPlot, NextGroupPlot, AddPlot, Coordinates, Ref, Iter, evaluate

plot = PGFPlot(
    GroupPlot(
        group_size="2 by 2",  # 2x2 grid
        width="5cm",
        height="4cm",
        horizontal_sep="1.5cm",
        vertical_sep="1.5cm",
        plots=[
            NextGroupPlot(
                title="Temperature",
                xlabel="Time (s)",
                ylabel="Temp (K)",
                grid=True,
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates(
                            Iter(Ref("temp_data"), x=Ref("t"), y=Ref("temp"))
                        ),
                    )
                ],
            ),
            NextGroupPlot(
                title="Pressure",
                xlabel="Time (s)",
                ylabel="Pressure (Pa)",
                grid=True,
                plots=[
                    AddPlot(
                        color="red",
                        mark="square*",
                        coords=Coordinates(
                            Iter(Ref("pressure_data"), x=Ref("t"), y=Ref("p"))
                        ),
                    )
                ],
            ),
            NextGroupPlot(
                title="Volume",
                plots=[...],
            ),
            NextGroupPlot(
                title="Density",
                plots=[...],
            ),
        ],
    )
)

data = {
    "temp_data": [{"t": 0, "temp": 300}, {"t": 1, "temp": 320}],
    "pressure_data": [{"t": 0, "p": 101325}, {"t": 1, "p": 102000}],
}

print(evaluate(plot, data))
```

#### GroupPlot Options

```python
GroupPlot(
    # Grid layout
    group_size="2 by 2",  # "columns by rows"

    # Spacing
    horizontal_sep="1cm",
    vertical_sep="1cm",

    # Label positioning (to avoid repetition)
    xlabels_at="edge bottom",  # only show x labels at bottom edge
    ylabels_at="edge left",    # only show y labels at left edge

    # Common options for all subplots
    width="6cm",
    height="4cm",
    xmin=0, xmax=10,

    # List of subplots
    plots=[NextGroupPlot(...), NextGroupPlot(...), ...],
)
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
    # Data source (choose one)
    coords=Coordinates([...]),           # List of tuples
    coords=Coordinates(x=[...], y=[...]),  # Separate arrays (NumPy or lists)
    expression="x^2",                    # Mathematical expression

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

### Coordinates Options

```python
# From list of tuples (original method)
Coordinates([(0, 1), (1, 2), (2, 4)])

# From separate x, y arrays (NumPy or lists)
Coordinates(x=[0, 1, 2], y=[1, 2, 4])
Coordinates(x=np.array([...]), y=np.array([...]))

# 3D coordinates
Coordinates([(0, 0, 1), (1, 1, 2)])
Coordinates(x=[0, 1], y=[0, 1], z=[1, 2])

# Dynamic from data
Coordinates(Iter(Ref("points"), x=Ref("x"), y=Ref("y")))
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

## Saving and Compiling

### Save to File

Save LaTeX code to a `.tex` file:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates
import numpy as np

# Create a plot
x = np.linspace(0, 2*np.pi, 100)
plot = PGFPlot(
    Axis(
        xlabel="$x$",
        ylabel="$f(x)$",
        plots=[AddPlot(coords=Coordinates(x=x, y=np.sin(x)))],
    )
)

# Save with preamble (for standalone compilation)
plot.save_to_file("my_plot.tex")

# Save without preamble (for inclusion in larger document)
plot.save_to_file("my_plot_content.tex", with_preamble=False)

# Save with data
plot.save_to_file("my_plot.tex", data=my_data)
```

### Compile to PDF

Compile directly to PDF using `pdflatex`:

```python
# Compile to PDF (saves .tex and compiles in one step)
pdf_path = plot.compile_to_pdf("my_plot.tex")
print(f"PDF saved to: {pdf_path}")

# With data
pdf_path = plot.compile_to_pdf("my_plot.tex", data=my_data)

# Specify output directory
pdf_path = plot.compile_to_pdf("my_plot.tex", output_dir="/tmp")
```

**Requirements for PDF compilation:**
- `pdflatex` must be installed on your system
- Install a LaTeX distribution:
  - **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-pictures`
  - **macOS**: `brew install --cask mactex`
  - **Windows**: Download [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

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
| `Axis` | Axis environment (single plot) |
| `GroupPlot` | Group of plots in a grid layout |
| `NextGroupPlot` | Individual subplot within a GroupPlot |
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

For groupplots (multiple subplots):
```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{groupplots}
```

For multirow cells:
```latex
\usepackage{multirow}
```
