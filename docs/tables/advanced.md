# Advanced Table Features

Learn about multi-column cells, complex layouts, and advanced table techniques.

## MultiColumn

Span multiple columns with `MultiColumn`:

```python
from texer import Tabular, Row, MultiColumn, evaluate

table = Tabular(
    columns="lccc",
    rows=[
        Row(
            "Category",
            MultiColumn(3, "c", "Measurements"),  # Spans 3 columns, centered
        ),
        Row("", "A", "B", "C"),  # Sub-headers
        Row("Test 1", "1.2", "2.3", "3.4"),
        Row("Test 2", "4.5", "5.6", "6.7"),
    ],
    toprule=True,
    bottomrule=True,
)

print(evaluate(table, {}))
```

**Output structure**:
```
Category | Measurements (spans 3 columns)
---------|--------------------------------
         | A     | B     | C
Test 1   | 1.2   | 2.3   | 3.4
Test 2   | 4.5   | 5.6   | 6.7
```

## MultiColumn Syntax

```python
MultiColumn(
    num_cols,    # Number of columns to span
    alignment,   # 'l', 'c', or 'r'
    content,     # Cell content (can be Ref, Format, etc.)
)
```

Examples:

```python
MultiColumn(2, "c", "Centered across 2 columns")
MultiColumn(3, "l", "Left-aligned across 3 columns")
MultiColumn(1, "r", "Right-aligned single column")
```

## Headers with MultiColumn

Create complex multi-level headers:

```python
from texer import Tabular, Row, MultiColumn, Cell, evaluate

table = Tabular(
    columns="lcccccc",
    rows=[
        # First level: Major groupings
        Row(
            "",
            MultiColumn(3, "c", Cell("Group A", bold=True)),
            MultiColumn(3, "c", Cell("Group B", bold=True)),
        ),
        # Second level: Sub-headers
        Row("", "X", "Y", "Z", "X", "Y", "Z"),
        # Data rows
        Row("Sample 1", "1", "2", "3", "4", "5", "6"),
        Row("Sample 2", "7", "8", "9", "10", "11", "12"),
    ],
    toprule=True,
    midrule=False,  # Manual control
    bottomrule=True,
)
```

## Partial Rules with cmidrule

The `cmidrule` helper function generates `\cmidrule` commands from the booktabs package for partial horizontal rules:

```python
from texer import Tabular, Row, MultiColumn, Raw, cmidrule, evaluate

table = Tabular(
    columns="lccc",
    rows=[
        Row("", MultiColumn(3, "c", "Metrics")),
        Raw(cmidrule(2, 4)),  # Rule under columns 2-4 only
        Row("", "A", "B", "C"),
        Row("Test 1", "1", "2", "3"),
        Row("Test 2", "4", "5", "6"),
    ],
    toprule=True,
    bottomrule=True,
)
```

### cmidrule Options

```python
from texer import cmidrule

# Basic usage
cmidrule(1, 3)                    # \cmidrule{1-3}

# With trimming (reduces rule width at edges)
cmidrule(2, 4, trim_left=True, trim_right=True)   # \cmidrule(lr){2-4}

# Custom trim widths
cmidrule(1, 2, trim_left="0.5em")                 # \cmidrule(l{0.5em}){1-2}
cmidrule(1, 2, trim_right="1em")                  # \cmidrule(r{1em}){1-2}
cmidrule(1, 2, trim_left="0.5em", trim_right="0.5em")  # \cmidrule(l{0.5em}r{0.5em}){1-2}
```

### Multiple cmidrules

Pass a list of `(start, end)` tuples to generate multiple rules at once:

```python
from texer import cmidrule

# Multiple ranges
cmidrule([(2, 4), (5, 7)])        # \cmidrule{2-4} \cmidrule{5-7}

# With automatic trimming between adjacent rules
cmidrule([(2, 4), (5, 7)], trim_between=True)
# Output: \cmidrule(r){2-4} \cmidrule(l){5-7}

# Three or more ranges - middle ones get both trims
cmidrule([(1, 2), (3, 4), (5, 6)], trim_between=True)
# Output: \cmidrule(r){1-2} \cmidrule(lr){3-4} \cmidrule(l){5-6}
```

Use in a table with grouped columns:

```python
from texer import Tabular, Row, MultiColumn, Raw, cmidrule

table = Tabular(
    columns="lcccccc",
    rows=[
        Row(
            "",
            MultiColumn(3, "c", "Group A"),
            MultiColumn(3, "c", "Group B"),
        ),
        Raw(cmidrule([(2, 4), (5, 7)], trim_between=True)),
        Row("", "X", "Y", "Z", "X", "Y", "Z"),
        Row("Sample", "1", "2", "3", "4", "5", "6"),
    ],
    toprule=True,
    bottomrule=True,
)
```

!!! tip "trim_between"
    The `trim_between=True` option automatically adds `trim_right` to all but the last rule and `trim_left` to all but the first rule, creating visual gaps between adjacent rules.

## Custom Rules with MultiColumn

Insert rules between sections:

```python
from texer import Tabular, Row, MultiColumn, Raw, evaluate

table = Tabular(
    columns="lccc",
    rows=[
        Row("", MultiColumn(3, "c", Cell("Header", bold=True))),
        Raw(r"\midrule"),
        Row("", "A", "B", "C"),
        Raw(r"\midrule"),
        Row("Data 1", "1", "2", "3"),
        Row("Data 2", "4", "5", "6"),
        Raw(r"\midrule"),
        Row("Total", "5", "7", "9"),
    ],
    toprule=True,
    midrule=False,  # We're adding rules manually
    bottomrule=True,
)
```

## Dynamic MultiColumn

Use with `Ref` and `Iter`:

```python
from texer import Tabular, Row, MultiColumn, Ref, Iter, evaluate

table = Tabular(
    columns="lcccc",
    rows=[
        Row(
            "Category",
            MultiColumn(Ref("num_metrics"), "c", Ref("group_title")),
        ),
        # ... more rows
    ],
)

data = {
    "num_metrics": 4,
    "group_title": "Performance Metrics",
}
```

## Alignment Override

Use `MultiColumn` to override column alignment for a single cell:

```python
# Default columns="lcc" (left, center, center)
Row(
    "Item",
    MultiColumn(1, "r", "999.99"),  # Right-align this number
    "Normal",
)
```

This is useful when you want a specific cell to have different alignment than its column.

## Complex Example: Grouped Data

```python
from texer import Table, Tabular, Row, MultiColumn, Cell, Ref, Iter, Format, Raw, evaluate

table = Table(
    Tabular(
        columns="lcccccc",
        rows=[
            # Main header
            Row(
                Cell("Experiment", bold=True),
                MultiColumn(3, "c", Cell("Trial 1", bold=True)),
                MultiColumn(3, "c", Cell("Trial 2", bold=True)),
            ),
            # Sub-headers
            Row("", "Mean", "Std", "N", "Mean", "Std", "N"),
            Raw(r"\midrule"),
            # Data rows with Iter
            *Iter(
                Ref("experiments"),
                template=Row(
                    Cell(Ref("name"), italic=True),
                    Format(Ref("trial1.mean"), ".2f"),
                    Format(Ref("trial1.std"), ".2f"),
                    Ref("trial1.n"),
                    Format(Ref("trial2.mean"), ".2f"),
                    Format(Ref("trial2.std"), ".2f"),
                    Ref("trial2.n"),
                )
            ),
        ],
        toprule=True,
        midrule=False,
        bottomrule=True,
    ),
    caption="Experimental Results Summary",
    label="tab:results",
)

data = {
    "experiments": [
        {
            "name": "Exp A",
            "trial1": {"mean": 10.5, "std": 1.2, "n": 30},
            "trial2": {"mean": 11.2, "std": 1.5, "n": 30},
        },
        {
            "name": "Exp B",
            "trial1": {"mean": 8.3, "std": 0.9, "n": 25},
            "trial2": {"mean": 9.1, "std": 1.1, "n": 25},
        },
    ]
}

print(evaluate(table, data))
```

## Nested Tabular Environments

For complex layouts, you can nest tabular environments:

```python
from texer import Raw

# Outer table
outer_table = Tabular(
    columns="lc",
    rows=[
        Row("Name", "Data"),
        Row(
            "Nested",
            Raw(r"\begin{tabular}{cc} A & B \\ C & D \end{tabular}"),
        ),
    ],
)
```

!!! warning "Use Sparingly"
    Nested tables can be hard to maintain. Consider if a simpler design works.

## Paragraph Columns

Use `p{width}` for paragraph-style columns with wrapping:

```python
Tabular(
    columns="lp{5cm}c",
    rows=[
        Row(
            "ID",
            "This is a long description that will automatically wrap within the 5cm column width",
            "Status",
        ),
    ],
    toprule=True,
    bottomrule=True,
)
```

Other paragraph column types:

- `p{width}`: Top-aligned paragraph
- `m{width}`: Middle-aligned paragraph (requires `array` package)
- `b{width}`: Bottom-aligned paragraph (requires `array` package)

## Vertical Rules

Add vertical lines in the column specification:

```python
Tabular(
    columns="l|cc|c",  # Vertical lines after 1st and 3rd columns
    rows=[...],
)
```

!!! note "Booktabs Style"
    The `booktabs` package (which provides `\toprule`, `\midrule`, etc.) recommends against vertical rules for professional tables.

## Custom Column Types

Define custom column types with LaTeX:

```python
from texer import Raw

# In your LaTeX preamble:
# \newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}

table = Tabular(
    columns="lRc",  # Using custom 'R' column type
    rows=[...],
)
```

## Wide Tables

For tables wider than the text width:

```python
# Option 1: Adjust column widths
Tabular(
    columns="p{2cm}p{3cm}p{2cm}",
    rows=[...],
)

# Option 2: Use landscape (in LaTeX preamble)
from texer import Raw

# Wrap in landscape environment
Raw(r"\begin{landscape}")
# ... table here ...
Raw(r"\end{landscape}")
```

## Long Tables (Multi-page)

For tables spanning multiple pages, use the `longtable` package:

```python
from texer import Raw

# Note: This is a raw LaTeX example
# texer doesn't have built-in longtable support yet

latex = r"""
\begin{longtable}{lcc}
\toprule
Header 1 & Header 2 & Header 3 \\
\midrule
\endfirsthead

\multicolumn{3}{c}{\textit{(continued)}} \\
\toprule
Header 1 & Header 2 & Header 3 \\
\midrule
\endhead

\bottomrule
\endfoot

% Data rows
Row 1 & Data & Data \\
Row 2 & Data & Data \\
% ... many more rows ...
\end{longtable}
"""
```

## Conditional Rows

Add rows conditionally:

```python
from texer import Cond, Raw

rows = [
    Row("Always shown", "value1", "value2"),
    # Conditional row
    *([Row("Optional", "val3", "val4")] if condition else []),
    Row("Also always shown", "value5", "value6"),
]
```

Or with specs:

```python
rows=Iter(
    Ref("items"),
    template=Cond(
        Ref("include"),
        Row(Ref("name"), Ref("value")),
        Raw(""),  # Empty for excluded items
    )
)
```

## Summary Rows

Add summary/total rows:

```python
from texer import Tabular, Row, Cell, Ref, Iter, Format, Raw, Call

table = Tabular(
    columns="lcc",
    header=Row("Item", "Quantity", "Price"),
    rows=[
        *Iter(
            Ref("items"),
            template=Row(
                Ref("name"),
                Ref("qty"),
                Format(Ref("price"), ".2f"),
            )
        ),
        Raw(r"\midrule"),
        Row(
            Cell("Total", bold=True),
            Call("sum", Iter(Ref("items"), template=Ref("qty"))),
            Cell(Format(Call("sum", Iter(Ref("items"), template=Ref("price"))), ".2f"), bold=True),
        ),
    ],
    toprule=True,
    bottomrule=True,
)
```

## Tips for Complex Tables

1. **Start simple**: Build incrementally
2. **Test frequently**: Verify LaTeX compilation at each step
3. **Use comments**: Document complex structures
4. **Modularize**: Break large tables into reusable parts
5. **Consider alternatives**: Sometimes multiple simple tables are better than one complex table

## Common Patterns

### Grouped Rows

```python
rows=[
    Cell("Group A", bold=True),
    Row("  Item 1", "data", "data"),
    Row("  Item 2", "data", "data"),
    Raw(r"\midrule"),
    Cell("Group B", bold=True),
    Row("  Item 3", "data", "data"),
    Row("  Item 4", "data", "data"),
]
```

### Alternating Row Colors

```python
# Requires \usepackage{xcolor,colortbl}
rows=[
    Row("Item 1", "data"),
    Raw(r"\rowcolor{gray!20}"),
    Row("Item 2", "data"),
    Row("Item 3", "data"),
    Raw(r"\rowcolor{gray!20}"),
    Row("Item 4", "data"),
]
```

## Next Steps

- [Basic Tables](basic.md) - Table fundamentals
- [Data-Driven Tables](data-driven.md) - Dynamic table generation
- [Cell Formatting](formatting.md) - Bold, italic, colors
