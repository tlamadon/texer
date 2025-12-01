# Basic Tables

## Mental Model for Tables

Think of tables as nested structures:

```
Table (floating environment)
└── Tabular (the actual grid)
    ├── Header (Row)
    └── Body (list of Rows or Iter)
        └── Cells (values, Refs, or Cell objects)
```

- **Table**: The floating environment with caption and label
- **Tabular**: The actual tabular grid with rows and columns
- **Row**: A single row of cells
- **Cell**: Individual cell with optional formatting

## Your First Table

Let's create a simple static table:

```python
from texer import Table, Tabular, Row, evaluate

table = Table(
    Tabular(
        columns="lcc",  # left, center, center alignment
        header=Row("Name", "Value", "Unit"),
        rows=[
            Row("Length", "42", "m"),
            Row("Mass", "100", "kg"),
            Row("Time", "5", "s"),
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

<details>
<summary>LaTeX code</summary>

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
    Time & 5 & s \\
    \bottomrule
  \end{tabular}
\end{table}
```
</details>

## Understanding the Parts

### Column Specification

The `columns` parameter defines alignment for each column:

| Code | Alignment |
|------|-----------|
| `l` | Left |
| `c` | Center |
| `r` | Right |
| `p{width}` | Paragraph (top-aligned) |

Examples:

```python
columns="lll"      # Three left-aligned columns
columns="lcr"      # Left, center, right
columns="p{3cm}cc" # Paragraph column + two centered
```

### Rules and Lines

Use booktabs-style rules for professional tables:

```python
Tabular(
    columns="lcc",
    toprule=True,      # Top rule
    midrule=True,      # Rule after header (automatic if header provided)
    bottomrule=True,   # Bottom rule
    header=Row(...),
    rows=[...],
)
```

For custom lines within the table, use `Raw`:

```python
from texer import Raw

rows=[
    Row("Section 1", "data", "data"),
    Raw(r"\midrule"),  # Custom horizontal line
    Row("Section 2", "data", "data"),
]
```

### Table vs Tabular

**Table** is optional - use it for floating tables with captions:

```python
# With Table (floating environment)
Table(
    Tabular(...),
    caption="My Table",
    label="tab:mytable",
    position="htbp",  # optional: h=here, t=top, b=bottom, p=page
)

# Just Tabular (inline, no caption)
Tabular(...)
```

## Simple Examples

### Two-Column Table

```python
from texer import Tabular, Row, evaluate

table = Tabular(
    columns="lr",
    header=Row("Item", "Price"),
    rows=[
        Row("Apple", "$1.00"),
        Row("Orange", "$1.50"),
        Row("Banana", "$0.75"),
    ],
    toprule=True,
    bottomrule=True,
)

print(evaluate(table, {}))
```

### Table Without Header

```python
table = Tabular(
    columns="ll",
    rows=[
        Row("Name:", "Alice"),
        Row("Age:", "30"),
        Row("City:", "Boston"),
    ],
    toprule=True,
    bottomrule=True,
    midrule=False,  # No midrule since no header
)
```

### Table with Paragraph Column

```python
table = Tabular(
    columns="lp{5cm}",
    header=Row("ID", "Description"),
    rows=[
        Row("A1", "This is a longer description that will wrap within the paragraph column"),
        Row("A2", "Another long description with automatic line wrapping"),
    ],
    toprule=True,
    bottomrule=True,
)
```

## Automatic LaTeX Escaping

texer automatically escapes special LaTeX characters:

```python
table = Tabular(
    columns="ll",
    rows=[
        Row("Price", "$100 & up"),       # & is escaped
        Row("Discount", "50%"),          # % is escaped
        Row("Reference", "Smith_2024"),  # _ is escaped
    ],
)

# Generated LaTeX:
# Price & \$100 \& up \\
# Discount & 50\% \\
# Reference & Smith\_2024 \\
```

If you need unescaped LaTeX, use `Raw`:

```python
from texer import Raw

Row("Math", Raw(r"$\alpha + \beta$"))
```

## Next Steps

- [Data-Driven Tables](data-driven.md) - Use `Ref` and `Iter` for dynamic tables
- [Cell Formatting](formatting.md) - Bold, italic, colors, and more
- [Advanced Features](advanced.md) - Multi-column, multi-row, and complex layouts
