# Core Concepts

## Specs: Lazy Data Descriptors

Specs are lazy descriptors that tell texer how to extract and transform data. They don't evaluate immediately - they describe what *should* happen when evaluated.

### Available Specs

| Spec | Purpose | Example |
|------|---------|---------|
| `Ref` | Access data by path | `Ref("user.name")` |
| `Iter` | Loop over collections | `Iter(Ref("items"), template=...)` |
| `Format` | Format values | `Format(Ref("x"), ".2f")` |
| `Cond` | Conditional logic | `Cond(Ref("x") > 5, "high", "low")` |
| `Raw` | Raw LaTeX (tables, plots, anywhere) | `Raw(r"\cmidrule{2-4}")` |

## Ref: Accessing Data

`Ref` uses glom-style dot notation to access nested data:

```python
from texer import Ref

# Simple access
Ref("name")              # data["name"]

# Nested access
Ref("user.email")        # data["user"]["email"]

# Array indexing
Ref("items.0.value")     # data["items"][0]["value"]

# With default value
Ref("x", default=0)      # returns 0 if "x" doesn't exist
```

### Example

```python
data = {
    "user": {
        "name": "Alice",
        "email": "alice@example.com"
    },
    "items": [
        {"value": 42},
        {"value": 23}
    ]
}

# Ref("user.name") evaluates to "Alice"
# Ref("items.0.value") evaluates to 42
```

## Iter: Looping Over Collections

`Iter` iterates over a collection and applies a template to each item:

```python
from texer import Iter, Ref, Row

# Iterate over a list
Iter(
    Ref("experiments"),  # The collection to iterate over
    template=Row(        # Applied to each item
        Ref("name"),
        Ref("result"),
    )
)
```

### For Coordinates

`Iter` has a special mode for extracting x/y coordinates:

```python
# Extract x and y from each point
Iter(
    Ref("points"),
    x=Ref("x"),
    y=Ref("y")
)

# With data:
data = {
    "points": [
        {"x": 0, "y": 1},
        {"x": 1, "y": 4},
        {"x": 2, "y": 9},
    ]
}
# Produces: [(0, 1), (1, 4), (2, 9)]
```

### Example

```python
from texer import Tabular, Row, Ref, Iter, evaluate

table = Tabular(
    columns="lc",
    header=Row("Name", "Score"),
    rows=Iter(
        Ref("students"),
        template=Row(Ref("name"), Ref("score"))
    ),
    toprule=True,
    bottomrule=True,
)

data = {
    "students": [
        {"name": "Alice", "score": 95},
        {"name": "Bob", "score": 87},
        {"name": "Charlie", "score": 92},
    ]
}

print(evaluate(table, data))
```

## Format: Formatting Values

`Format` applies Python format specifications to values:

```python
from texer import Format, Ref

# Floating point
Format(Ref("price"), ".2f")   # "3.14"

# Percentage
Format(Ref("ratio"), ".1%")   # "25.0%"

# Scientific notation
Format(Ref("value"), ".2e")   # "1.23e+05"

# Integer with thousand separators
Format(Ref("count"), ",d")    # "1,234,567"
```

### Format Spec Reference

| Spec | Description | Example Input | Example Output |
|------|-------------|---------------|----------------|
| `.2f` | 2 decimal places | 3.14159 | 3.14 |
| `.0f` | No decimal places | 3.14159 | 3 |
| `.1%` | Percentage, 1 decimal | 0.251 | 25.1% |
| `.2e` | Scientific, 2 decimals | 123.45 | 1.23e+02 |
| `,d` | Thousands separator | 1234567 | 1,234,567 |

See [Python format specification](https://docs.python.org/3/library/string.html#format-specification-mini-language) for complete reference.

## Cond: Conditional Logic

`Cond` implements if-then-else logic:

```python
from texer import Cond, Ref

# Simple conditional
Cond(Ref("x") > 5, "high", "low")

# With specs as results
Cond(
    Ref("active"),
    r"\checkmark",  # if true
    ""              # if false
)

# Nested conditions
Cond(
    Ref("score") >= 90,
    "A",
    Cond(
        Ref("score") >= 80,
        "B",
        "C"
    )
)
```

### Comparison Operators

You can build complex conditions using comparison operators:

```python
from texer import Ref

# Basic comparisons
Ref("x") > 5      # greater than
Ref("x") < 5      # less than
Ref("x") >= 5     # greater or equal
Ref("x") <= 5     # less or equal
Ref("x") == 5     # equal
Ref("x") != 5     # not equal

# Combine with & (and) and | (or)
(Ref("x") > 0) & (Ref("x") < 10)    # between 0 and 10
(Ref("x") < 0) | (Ref("x") > 10)    # outside 0 to 10
```

### Example: Status Colors

```python
from texer import Row, Cell, Ref, Iter, Cond, Format

Row(
    Ref("test_name"),
    Format(Ref("score"), ".1f"),
    Cond(
        Ref("score") >= 70,
        r"\textcolor{green}{PASS}",
        r"\textcolor{red}{FAIL}",
    ),
)
```

## Writing LaTeX in Tables

Tables do **not** auto-escape LaTeX special characters. You're expected to write valid LaTeX directly using raw strings:

```python
from texer import Row

# Use raw strings (r"...") for LaTeX
Row(r"\textbf{bold}", r"$\alpha + \beta$")

# Math mode
Row("Formula", r"$x^2 + y^2 = r^2$")

# Colors (requires xcolor package)
Row("Status", r"\textcolor{red}{FAIL}")
```

!!! tip "Raw Strings"
    Use Python raw strings (`r"..."`) to avoid escaping backslashes. For example, `r"\textbf{bold}"` instead of `"\\textbf{bold}"`.

## The Evaluation Process

When you call `evaluate(structure, data)`:

1. **Walk the structure**: texer traverses your structure tree
2. **Evaluate specs**: When it encounters a spec:
   - The spec is evaluated against the current data context
   - For `Iter`, the context changes for each iteration
3. **Generate LaTeX**: The final LaTeX string is assembled

!!! note "No Auto-Escaping in Tables"
    Tables do not auto-escape LaTeX special characters. Use raw strings (`r"..."`) and write valid LaTeX directly.

### Example Flow

```python
from texer import Tabular, Row, Ref, Iter, evaluate

table = Tabular(
    columns="lc",
    rows=Iter(
        Ref("items"),
        template=Row(Ref("name"), Ref("count"))
    ),
)

data = {
    "items": [
        {"name": "Apples", "count": 5},
        {"name": "Oranges", "count": 3},
    ]
}

# Evaluation:
# 1. Start with full data context
# 2. Encounter Iter(Ref("items"), ...)
# 3. Evaluate Ref("items") → [{"name": "Apples", ...}, {...}]
# 4. For each item:
#    a. Context becomes {"name": "Apples", "count": 5}
#    b. Evaluate Row(Ref("name"), Ref("count"))
#    c. Ref("name") → "Apples", Ref("count") → 5
# 5. Generate LaTeX rows
```

## Composability

Specs are composable - you can nest them freely:

```python
from texer import Ref, Format, Cond

# Format a conditional value
Format(
    Cond(Ref("use_celsius"), Ref("temp_c"), Ref("temp_f")),
    ".1f"
)

# Conditional formatting
Cond(
    Ref("large"),
    Format(Ref("value"), ".2e"),  # Scientific for large numbers
    Format(Ref("value"), ".2f"),  # Regular for small numbers
)
```

## Next Steps

Now that you understand specs and evaluation:

- [Basic Tables](../tables/basic.md) - Apply specs to tables
- [Data-Driven Tables](../tables/data-driven.md) - Advanced table patterns
- [Basic Plots](../plots/basic.md) - Apply specs to plots
- [Specs Reference](../specs/overview.md) - Complete spec documentation
