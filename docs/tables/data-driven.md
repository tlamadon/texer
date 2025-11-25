# Data-Driven Tables

The power of texer comes from using specs to create tables that adapt to your data.

## Basic Data-Driven Table

Replace static values with `Ref` specs:

```python
from texer import Table, Tabular, Row, Ref, Iter, evaluate

table = Table(
    Tabular(
        columns="lcc",
        header=Row("Name", "Value", "Unit"),
        rows=Iter(
            Ref("measurements"),  # Extract list from data
            template=Row(
                Ref("name"),      # Extract fields from each item
                Ref("value"),
                Ref("unit"),
            )
        ),
        toprule=True,
        bottomrule=True,
    ),
    caption=Ref("table_title"),  # Dynamic caption
    label="tab:measurements",
)

data = {
    "table_title": "Physical Measurements",
    "measurements": [
        {"name": "Length", "value": "42", "unit": "m"},
        {"name": "Mass", "value": "100", "unit": "kg"},
        {"name": "Time", "value": "5", "unit": "s"},
    ]
}

print(evaluate(table, data))
```

The number of rows automatically matches your data - add more items to the list, get more rows!

## Formatted Values

Use `Format` to format numbers:

```python
from texer import Format

table = Tabular(
    columns="lcc",
    header=Row("Experiment", "Result", "Error"),
    rows=Iter(
        Ref("experiments"),
        template=Row(
            Ref("name"),
            Format(Ref("result"), ".3f"),   # 3 decimal places
            Format(Ref("error"), ".1%"),    # As percentage
        )
    ),
    toprule=True,
    bottomrule=True,
)

data = {
    "experiments": [
        {"name": "Trial A", "result": 3.14159, "error": 0.023},
        {"name": "Trial B", "result": 2.71828, "error": 0.015},
        {"name": "Trial C", "result": 1.41421, "error": 0.042},
    ]
}

# Output:
# Trial A & 3.142 & 2.3\% \\
# Trial B & 2.718 & 1.5\% \\
# Trial C & 1.414 & 4.2\% \\
```

## Conditional Content

Use `Cond` for conditional values:

```python
from texer import Cond, Raw

table = Tabular(
    columns="lcc",
    header=Row("Test", "Score", "Status"),
    rows=Iter(
        Ref("tests"),
        template=Row(
            Ref("name"),
            Format(Ref("score"), ".1f"),
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
```

## Nested Data

Access nested data with dot notation:

```python
table = Tabular(
    columns="lll",
    header=Row("Name", "Email", "City"),
    rows=Iter(
        Ref("users"),
        template=Row(
            Ref("name"),
            Ref("contact.email"),      # Nested field
            Ref("contact.address.city"), # Deeply nested
        )
    ),
    toprule=True,
    bottomrule=True,
)

data = {
    "users": [
        {
            "name": "Alice",
            "contact": {
                "email": "alice@example.com",
                "address": {"city": "Boston"}
            }
        },
        {
            "name": "Bob",
            "contact": {
                "email": "bob@example.com",
                "address": {"city": "Seattle"}
            }
        },
    ]
}
```

## Complex Example

Combining multiple techniques:

```python
from texer import Table, Tabular, Row, Cell, Ref, Iter, Format, Cond, Raw

table = Table(
    Tabular(
        columns="llccc",
        header=Row(
            "Student",
            "Assignment",
            "Score",
            "Grade",
            "Status"
        ),
        rows=Iter(
            Ref("submissions"),
            template=Row(
                Cell(Ref("student.name"), bold=True),
                Ref("assignment"),
                Format(Ref("score"), ".1f"),
                # Letter grade based on score
                Cond(
                    Ref("score") >= 90, "A",
                    Cond(
                        Ref("score") >= 80, "B",
                        Cond(
                            Ref("score") >= 70, "C",
                            "F"
                        )
                    )
                ),
                # Pass/fail with color
                Cond(
                    Ref("score") >= 70,
                    Raw(r"\textcolor{green}{\checkmark}"),
                    Raw(r"\textcolor{red}{\times}"),
                ),
            )
        ),
        toprule=True,
        bottomrule=True,
    ),
    caption="Assignment Submissions",
    label="tab:submissions",
)

data = {
    "submissions": [
        {
            "student": {"name": "Alice Johnson"},
            "assignment": "HW1",
            "score": 95.5
        },
        {
            "student": {"name": "Bob Smith"},
            "assignment": "HW1",
            "score": 67.3
        },
        {
            "student": {"name": "Charlie Brown"},
            "assignment": "HW1",
            "score": 88.9
        },
    ]
}

print(evaluate(table, data))
```

## Reusable Templates

Define row templates once and reuse them:

```python
# Define a reusable row template
student_row = Row(
    Ref("name"),
    Format(Ref("score"), ".1f"),
    Cond(Ref("score") >= 70, "PASS", "FAIL"),
)

# Use it in multiple tables
table1 = Tabular(
    header=Row("Name", "Score", "Status"),
    rows=Iter(Ref("class_a"), template=student_row),
    toprule=True,
    bottomrule=True,
)

table2 = Tabular(
    header=Row("Name", "Score", "Status"),
    rows=Iter(Ref("class_b"), template=student_row),
    toprule=True,
    bottomrule=True,
)

data = {
    "class_a": [{"name": "Alice", "score": 95}, ...],
    "class_b": [{"name": "Bob", "score": 87}, ...],
}
```

## Next Steps

- [Cell Formatting](formatting.md) - Bold, italic, colors, and alignment
- [Advanced Features](advanced.md) - Multi-column and multi-row cells
- [Format Spec](../specs/format.md) - Complete formatting reference
- [Cond Spec](../specs/cond.md) - Conditional logic patterns
