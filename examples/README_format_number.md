# FormatNumber Examples

This directory contains examples demonstrating the `FormatNumber` spec for advanced number formatting in tables.

## Features

The `FormatNumber` spec provides:

1. **Significant figures**: `sig=2` keeps 2 significant digits
2. **Fixed decimal places**: `decimals=2` shows exactly 2 decimal places
3. **Thousands separators**: `thousands_sep=True` adds commas (or custom separator)
4. **Negative zero handling**: Automatically converts `-0.00` to `0.00`
5. **String passthrough**: Non-numeric strings are returned unchanged

## Quick Examples

```python
from texer import FormatNumber, Ref

# Significant figures
FormatNumber(Ref("value"), sig=2)  # 1.234 -> "1.2"

# Decimal places
FormatNumber(Ref("value"), decimals=2)  # 1.234 -> "1.23"

# Thousands separator (default comma)
FormatNumber(Ref("value"), thousands_sep=True)  # 2000 -> "2,000"

# Custom separator
FormatNumber(Ref("value"), thousands_sep=" ")  # 2000 -> "2 000"

# Combined: decimals + thousands
FormatNumber(Ref("value"), decimals=2, thousands_sep=True)  # 1234.567 -> "1,234.57"

# Handles -0.00
FormatNumber(Ref("value"), decimals=2)  # -0.001 -> "0.00" (not "-0.00")
```

## Running the Demo

```bash
python examples/format_number_demo.py
```

This will generate LaTeX tables showing:
1. Different formatting options (sig vs decimals vs thousands separator)
2. Handling of -0.00 values
3. Currency formatting with thousands separators and decimal places

## Use in Tables

```python
from texer import Tabular, Row, Ref, Iter, FormatNumber

table = Tabular(
    columns="lr",
    header=Row("Item", "Amount"),
    rows=Iter(
        Ref("data"),
        template=Row(
            Ref("name"),
            FormatNumber(Ref("value"), decimals=2, thousands_sep=True),
        ),
    ),
)
```
