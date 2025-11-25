# Cell Formatting

Format individual cells with bold, italic, colors, and other LaTeX styling.

## The Cell Class

The `Cell` class wraps content with formatting options:

```python
from texer import Table, Tabular, Row, Cell, evaluate

table = Tabular(
    columns="lcc",
    header=Row("Name", "Value", "Status"),
    rows=[
        Row(
            Cell("Important", bold=True),
            Cell("42", italic=True),
            Cell("Active", bold=True, italic=True),
        ),
    ],
    toprule=True,
    bottomrule=True,
)

print(evaluate(table, {}))
```

## Bold Text

```python
from texer import Cell

Cell("Bold Text", bold=True)
# Renders as: \textbf{Bold Text}
```

In a table:

```python
Row(
    Cell("Header 1", bold=True),
    Cell("Header 2", bold=True),
    "Regular cell",
)
```

## Italic Text

```python
Cell("Italic Text", italic=True)
# Renders as: \textit{Italic Text}
```

## Bold + Italic

```python
Cell("Bold and Italic", bold=True, italic=True)
# Renders as: \textbf{\textit{Bold and Italic}}
```

## With Dynamic Data

Use `Cell` with `Ref` and `Iter`:

```python
from texer import Tabular, Row, Cell, Ref, Iter, Format, evaluate

table = Tabular(
    columns="lcc",
    header=Row(
        Cell("Experiment", bold=True),
        Cell("Result", bold=True),
        Cell("P-value", bold=True),
    ),
    rows=Iter(
        Ref("experiments"),
        template=Row(
            Cell(Ref("name"), italic=True),
            Format(Ref("result"), ".3f"),
            Format(Ref("pvalue"), ".4f"),
        )
    ),
    toprule=True,
    bottomrule=True,
)

data = {
    "experiments": [
        {"name": "Trial A", "result": 3.142, "pvalue": 0.0234},
        {"name": "Trial B", "result": 2.718, "pvalue": 0.0012},
    ]
}

print(evaluate(table, data))
```

## Conditional Formatting

Apply formatting based on conditions:

```python
from texer import Cond, Cell, Ref, Iter

rows=Iter(
    Ref("results"),
    template=Row(
        Ref("name"),
        Ref("score"),
        # Bold if score >= 90
        Cond(
            Ref("score") >= 90,
            Cell(Ref("grade"), bold=True),
            Ref("grade"),
        ),
    )
)
```

## Text Colors

Use `Raw` with LaTeX `\textcolor`:

```python
from texer import Raw, Cell

# Basic color
Cell(Raw(r"\textcolor{red}{Error}"))

# With standard colors
Cell(Raw(r"\textcolor{blue}{Information}"))
Cell(Raw(r"\textcolor{green}{Success}"))
Cell(Raw(r"\textcolor{red}{Failed}"))
```

!!! note "Color Package"
    Requires `\usepackage{xcolor}` in your LaTeX document.

## Colored Cells with Conditions

```python
from texer import Cond, Raw, Ref, Iter, Row

rows=Iter(
    Ref("tests"),
    template=Row(
        Ref("name"),
        Ref("status"),
        Cond(
            Ref("passed"),
            Raw(r"\textcolor{green}{\checkmark}"),
            Raw(r"\textcolor{red}{\times}"),
        ),
    )
)

data = {
    "tests": [
        {"name": "Unit Tests", "status": "Complete", "passed": True},
        {"name": "Integration", "status": "Failed", "passed": False},
    ]
}
```

## Alignment within Cells

Use `\multicolumn` for cell-specific alignment:

```python
from texer import MultiColumn

Row(
    "Left aligned",
    MultiColumn(1, "r", "Right aligned"),  # Right align this cell
    "Default alignment",
)
```

## Background Colors

Use `\cellcolor` for cell backgrounds:

```python
from texer import Raw

Row(
    "Normal",
    Raw(r"\cellcolor{yellow}Highlighted"),
    "Normal",
)
```

!!! note "Colortbl Package"
    Requires `\usepackage{colortbl}` in your LaTeX document.

## Font Sizes

```python
from texer import Raw

Cell(Raw(r"\small Small text"))
Cell(Raw(r"\large Large text"))
Cell(Raw(r"\Large Even larger"))
Cell(Raw(r"\tiny Tiny text"))
```

## Mathematical Content

```python
from texer import Raw

Row(
    "Formula",
    Raw(r"$\alpha + \beta = \gamma$"),
    Raw(r"$x^2 + y^2 = r^2$"),
)
```

## Combining Formats

Stack multiple formatting options:

```python
from texer import Cell, Raw

# Bold italic colored text
Cell(
    Raw(r"\textcolor{blue}{\textbf{\textit{Important Note}}}"),
)

# Or with Cell attributes
Cell(
    Raw(r"\textcolor{blue}{Important}"),
    bold=True,
    italic=True,
)
```

## Number Formatting

Use `Format` with `Cell`:

```python
from texer import Cell, Format, Ref

Row(
    Ref("name"),
    Cell(Format(Ref("value"), ".2f"), bold=True),  # Bold formatted number
    Format(Ref("percent"), ".1%"),                 # Percentage
)
```

## Complete Example

```python
from texer import Table, Tabular, Row, Cell, Ref, Iter, Format, Cond, Raw, evaluate

table = Table(
    Tabular(
        columns="llccc",
        header=Row(
            Cell("Student", bold=True),
            Cell("Assignment", bold=True),
            Cell("Score", bold=True),
            Cell("Grade", bold=True),
            Cell("Status", bold=True),
        ),
        rows=Iter(
            Ref("submissions"),
            template=Row(
                Cell(Ref("student"), italic=True),
                Ref("assignment"),
                Format(Ref("score"), ".1f"),
                # Conditional bold for high grades
                Cond(
                    Ref("score") >= 90,
                    Cell(Ref("letter_grade"), bold=True),
                    Ref("letter_grade"),
                ),
                # Colored status
                Cond(
                    Ref("passed"),
                    Raw(r"\textcolor{green}{PASS}"),
                    Raw(r"\textcolor{red}{FAIL}"),
                ),
            )
        ),
        toprule=True,
        bottomrule=True,
    ),
    caption="Student Grades",
    label="tab:grades",
)

data = {
    "submissions": [
        {
            "student": "Alice Johnson",
            "assignment": "HW1",
            "score": 95.5,
            "letter_grade": "A",
            "passed": True,
        },
        {
            "student": "Bob Smith",
            "assignment": "HW1",
            "score": 67.3,
            "letter_grade": "D",
            "passed": False,
        },
        {
            "student": "Charlie Brown",
            "assignment": "HW1",
            "score": 88.9,
            "letter_grade": "B",
            "passed": True,
        },
    ]
}

print(evaluate(table, data))
```

## LaTeX Special Characters

texer automatically escapes special LaTeX characters (`&`, `%`, `$`, `_`, etc.), but you can use `Raw` for unescaped content:

```python
# Automatic escaping
Row("Price", "$100")  # Renders as: Price & \$100 \\

# Unescaped with Raw
Row("Formula", Raw(r"$x^2$"))  # Renders as: Formula & $x^2$ \\
```

## Custom LaTeX Commands

Use `Raw` for custom LaTeX commands:

```python
from texer import Raw, Cell

# Custom command
Cell(Raw(r"\mycustomcommand{value}"))

# With conditionals
Cond(
    Ref("is_important"),
    Raw(r"\important{" + Ref("text") + r"}"),
    Ref("text"),
)
```

## Tips

1. **Keep it simple**: Use `Cell(text, bold=True)` for common cases
2. **Use Raw sparingly**: Only when you need LaTeX-specific features
3. **Escape or Raw**: Either let texer escape or use `Raw`, not both
4. **Test colors**: Different LaTeX distributions may support different colors

## Next Steps

- [Advanced Features](advanced.md) - Multi-column and multi-row cells
- [Data-Driven Tables](data-driven.md) - Combine formatting with dynamic data
- [Raw Spec](../specs/raw.md) - Complete Raw specification
