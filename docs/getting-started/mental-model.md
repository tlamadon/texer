# Mental Model

## The Core Principle

texer follows a simple principle: **describe your LaTeX structure once, then fill it with any data**.

Instead of writing string templates or manually building LaTeX, you define:

1. The **structure** of your table or plot using Python classes
2. **Specs** that describe where data comes from
3. Your **data** as plain Python dicts/lists

texer then evaluates the specs against your data to produce valid LaTeX.

```
Structure + Specs + Data → LaTeX
```

## How It Works

### 1. Define Structure

Use Python classes to define the structure of your output:

```python
from texer import Table, Tabular, Row

table = Table(
    Tabular(
        columns="lcc",
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
```

This is a **static** table - all values are hardcoded.

### 2. Add Specs for Dynamic Data

Replace static values with specs that describe how to extract data:

```python
from texer import Table, Tabular, Row, Ref, Iter, Format

table = Table(
    Tabular(
        columns="lcc",
        header=Row("Name", "Value", "Unit"),
        rows=Iter(
            Ref("measurements"),  # Where to get the list
            template=Row(
                Ref("name"),              # Extract "name" from each item
                Format(Ref("value"), ".2f"),  # Extract and format "value"
                Ref("unit"),              # Extract "unit"
            )
        ),
        toprule=True,
        bottomrule=True,
    ),
    caption=Ref("title"),  # Dynamic caption
    label="tab:properties",
)
```

Now the table is **dynamic** - it adapts to whatever data you provide.

### 3. Provide Data

Provide data as plain Python data structures:

```python
data = {
    "title": "Physical Properties",
    "measurements": [
        {"name": "Length", "value": 42.5, "unit": "m"},
        {"name": "Mass", "value": 100.3, "unit": "kg"},
        {"name": "Time", "value": 5.7, "unit": "s"},
    ]
}
```

### 4. Evaluate

Combine structure and data to generate LaTeX:

```python
from texer import evaluate

latex = evaluate(table, data)
print(latex)
```

## The Evaluation Flow

```
1. You call evaluate(structure, data)
2. texer walks through the structure
3. When it encounters a Spec (Ref, Iter, Format, etc.):
   - It evaluates the spec against the current data context
   - It produces a concrete value
4. All values are properly escaped for LaTeX
5. Valid LaTeX code is generated
```

## Why This Approach?

### Separation of Concerns

- **Structure** defines what your output looks like
- **Specs** define how to extract and transform data
- **Data** is just plain Python data structures

This separation means you can:

- Reuse the same structure with different data
- Change data sources without touching structure
- Test structure and data independently

### Type Safety

Because you're using Python classes, you get:

- IDE autocomplete
- Type checking with mypy
- Compile-time error catching

### Flexibility

Specs are composable and reusable:

```python
# Define a spec once
measurement_row = Row(
    Ref("name"),
    Format(Ref("value"), ".2f"),
    Ref("unit"),
)

# Use it in multiple places
table1 = Tabular(rows=Iter(Ref("set1"), template=measurement_row))
table2 = Tabular(rows=Iter(Ref("set2"), template=measurement_row))
```

## Next Steps

Now that you understand the mental model, learn about:

- [Core Concepts](core-concepts.md) - Deep dive into specs and evaluation
- [Basic Tables](../tables/basic.md) - Apply this to tables
- [Basic Plots](../plots/basic.md) - Apply this to plots
