"""Demo of FormatNumber functionality for tables."""

from texer import evaluate, Tabular, Row, Ref, FormatNumber, Iter

# Sample data with various numbers
data = {
    "measurements": [
        {"name": "Temperature", "value": -0.001, "count": 2000},
        {"name": "Pressure", "value": 1234.567, "count": 15000},
        {"name": "Volume", "value": 0.123, "count": 1000000},
    ]
}

# Create a table using FormatNumber
table = Tabular(
    columns="lrrr",
    header=Row("Measurement", "Value (2 sig)", "Value (2 dec)", "Count (with ,)"),
    rows=Iter(
        Ref("measurements"),
        template=Row(
            Ref("name"),
            FormatNumber(Ref("value"), sig=2),
            FormatNumber(Ref("value"), decimals=2),
            FormatNumber(Ref("count"), thousands_sep=True),
        ),
    ),
    toprule=True,
    midrule=True,
    bottomrule=True,
)

# Generate LaTeX
latex = evaluate(table, data)
print(latex)
print("\n" + "="*60 + "\n")

# Demo of -0.00 handling
data2 = {
    "values": [
        {"label": "Near zero (positive)", "num": 0.001},
        {"label": "Near zero (negative)", "num": -0.001},
        {"label": "Zero", "num": 0.0},
    ]
}

table2 = Tabular(
    columns="lr",
    header=Row("Label", "Value (2 decimals)"),
    rows=Iter(
        Ref("values"),
        template=Row(
            Ref("label"),
            FormatNumber(Ref("num"), decimals=2),
        ),
    ),
    toprule=True,
    midrule=True,
    bottomrule=True,
)

print("Demo of -0.00 handling:")
latex2 = evaluate(table2, data2)
print(latex2)
print("\n" + "="*60 + "\n")

# Demo of combining decimals with thousands separator
data3 = {
    "finances": [
        {"item": "Revenue", "amount": 1234567.89},
        {"item": "Expenses", "amount": 987654.32},
        {"item": "Profit", "amount": 246913.57},
    ]
}

table3 = Tabular(
    columns="lr",
    header=Row("Item", "Amount (\\$)"),
    rows=Iter(
        Ref("finances"),
        template=Row(
            Ref("item"),
            FormatNumber(Ref("amount"), decimals=2, thousands_sep=True),
        ),
    ),
    toprule=True,
    midrule=True,
    bottomrule=True,
)

print("Demo of currency formatting:")
latex3 = evaluate(table3, data3)
print(latex3)
