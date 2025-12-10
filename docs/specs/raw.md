# Raw

The `Raw` spec allows you to insert raw LaTeX code that should not be escaped or processed. It works universally across all contexts: tables, plots, cells, and more.

## Basic Usage

```python
from texer import Raw

# Simple raw LaTeX
Raw(r"\textbf{bold text}")
Raw(r"\hline")
Raw(r"\cmidrule{2-4}")
```

## Universal Compatibility

`Raw` can be used anywhere in texer structures:

### In Table Rows

Insert raw LaTeX commands between rows:

```python
from texer import Tabular, Row, Raw, evaluate

table = Tabular(
    columns="lcc",
    rows=[
        Row("Header 1", "Header 2", "Header 3"),
        Raw(r"\midrule"),
        Row("A", "B", "C"),
        Raw(r"\cmidrule{2-3}"),
        Row("D", "E", "F"),
    ],
    toprule=True,
    bottomrule=True,
)

print(evaluate(table, {}))
```

**Output:**
```latex
\begin{tabular}{lcc}
  \toprule
  Header 1 & Header 2 & Header 3 \\
  \midrule
  A & B & C \\
  \cmidrule{2-3}
  D & E & F \\
  \bottomrule
\end{tabular}
```

### In Cell Content

Use raw LaTeX inside cells:

```python
from texer import Row, Raw

row = Row(
    "Name",
    Raw(r"\textcolor{red}{Important}"),
    Raw(r"$\alpha + \beta$"),
)
```

### In Plots

Add custom TikZ/PGF commands to plots:

```python
from texer import Axis, AddPlot, Coordinates, Raw, evaluate

axis = Axis(
    plots=[
        AddPlot(Coordinates([(0, 0), (1, 1), (2, 4)])),
        Raw(r"\draw[red, dashed] (axis cs:0,0) -- (axis cs:2,4);"),
        Raw(r"\node at (axis cs:1,2) {Midpoint};"),
    ],
    xlabel="x",
    ylabel="y",
)

print(evaluate(axis, {}))
```

**Output:**
```latex
\begin{axis}[xlabel={x}, ylabel={y}]
  \addplot+ coordinates {(0, 0) (1, 1) (2, 4)};
  \draw[red, dashed] (axis cs:0,0) -- (axis cs:2,4);
  \node at (axis cs:1,2) {Midpoint};
\end{axis}
```

### With Conditionals

Combine `Raw` with `Cond` for conditional LaTeX:

```python
from texer import Cond, Ref, Raw

# Conditional separator
Cond(
    Ref("show_rule"),
    Raw(r"\midrule"),
    Raw(""),  # Empty if condition is false
)
```

## Common Use Cases

### Table Rules (booktabs)

```python
from texer import Raw, cmidrule

Raw(r"\toprule")      # Top rule
Raw(r"\midrule")      # Middle rule
Raw(r"\bottomrule")   # Bottom rule

# Partial rules with cmidrule helper
Raw(cmidrule(2, 4))                    # \cmidrule{2-4}
Raw(cmidrule(2, 4, trim_left=True))    # \cmidrule(l){2-4}

# Multiple partial rules at once
Raw(cmidrule([(2, 4), (5, 7)]))                  # Two rules
Raw(cmidrule([(2, 4), (5, 7)], trim_between=True))  # With gaps between
```

### Row Colors

```python
from texer import Row, Raw

rows = [
    Row("Item 1", "Data"),
    Raw(r"\rowcolor{gray!20}"),
    Row("Item 2", "Data"),  # This row will be shaded
]
```

### Custom Spacing

```python
from texer import Raw

Raw(r"\addlinespace")      # Add vertical space (booktabs)
Raw(r"\addlinespace[5pt]") # Custom spacing
Raw(r"\\[2ex]")            # Extra vertical space after row
```

### Math and Symbols

```python
from texer import Raw

Raw(r"$\sum_{i=1}^{n} x_i$")
Raw(r"\checkmark")
Raw(r"\texttimes")
```

### TikZ/PGF in Plots

```python
from texer import Raw

# Annotations
Raw(r"\node[above] at (axis cs:1,1) {Label};")

# Custom drawings
Raw(r"\draw[blue, thick] (axis cs:0,0) circle (0.5);")

# Fill regions
Raw(r"\fill[blue, opacity=0.2] (axis cs:0,0) rectangle (axis cs:1,1);")
```

## Tips

!!! tip "Use Raw Strings"
    Always use Python raw strings (`r"..."`) with `Raw` to avoid escaping backslashes:
    ```python
    Raw(r"\textbf{bold}")   # Correct
    Raw("\\textbf{bold}")   # Also works but harder to read
    ```

!!! note "No Escaping"
    Content passed to `Raw` is inserted verbatim. Special LaTeX characters like `%`, `&`, `$` are NOT escaped.

!!! warning "Syntax Errors"
    Invalid LaTeX in `Raw` will cause compilation errors. Test your LaTeX syntax separately if needed.

## See Also

- [cmidrule](../tables/advanced.md#partial-rules-with-cmidrule) - Helper function for `\cmidrule`
- [Advanced Tables](../tables/advanced.md) - More table techniques
- [Advanced Plots](../plots/advanced.md) - Custom plot annotations
