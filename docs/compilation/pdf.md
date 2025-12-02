# Compiling to PDF

The `evaluate()` function can compile your LaTeX directly to PDF using the `compile=True` parameter.

## Prerequisites

You need a LaTeX distribution installed:

- **Ubuntu/Debian**: `sudo apt-get install texlive-latex-base texlive-pictures`
- **macOS**: `brew install --cask mactex`
- **Windows**: [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

## Basic Usage

```python
from texer import Table, Tabular, Row, evaluate

table = Table(
    Tabular(
        columns="lcc",
        header=Row("Name", "Value", "Unit"),
        rows=[Row("Speed", "100", "km/h")],
    ),
    caption="Results",
)

# Compile to PDF
pdf_path = evaluate(table, output_file="my_table.tex", compile=True)
print(f"PDF created at: {pdf_path}")
```

When `compile=True`:

1. The `with_preamble` option is automatically enabled (required for compilation)
2. The `.tex` file is saved
3. `pdflatex` is run to compile the document
4. The path to the generated PDF is returned

## Output Directory

By default, the PDF is created in the same directory as the `.tex` file. Use `output_dir` to specify a different location:

```python
# Create PDF in a different directory
pdf_path = evaluate(
    table,
    output_file="src/my_table.tex",
    compile=True,
    output_dir="output/pdfs"
)
```

## Compiling Plots

The same approach works for plots:

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, evaluate

plot = PGFPlot(
    Axis(
        xlabel="X",
        ylabel="Y",
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates([(0, 0), (1, 1), (2, 4), (3, 9)]),
            )
        ],
    )
)

# Compile to PDF
pdf_path = evaluate(plot, output_file="my_plot.tex", compile=True)
```

## Complete Example

```python
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate

# Define plot with data references
plot = PGFPlot(
    Axis(
        xlabel=Ref("x_label"),
        ylabel=Ref("y_label"),
        title=Ref("title"),
        grid=True,
        plots=[
            AddPlot(
                color="blue",
                mark="*",
                coords=Coordinates(
                    Iter(Ref("data"), x=Ref("x"), y=Ref("y"))
                ),
            )
        ],
    )
)

# Data
data = {
    "title": "Quadratic Function",
    "x_label": "$x$",
    "y_label": "$y = x^2$",
    "data": [{"x": i, "y": i**2} for i in range(10)]
}

# Compile to PDF
pdf_path = evaluate(
    plot,
    data,
    output_file="quadratic.tex",
    compile=True,
    header=False  # No header comment in the .tex file
)

print(f"PDF created: {pdf_path}")
```

## Error Handling

If compilation fails, a `RuntimeError` is raised with the pdflatex output:

```python
try:
    evaluate(table, output_file="table.tex", compile=True)
except RuntimeError as e:
    print(f"Compilation failed: {e}")
```

If `pdflatex` is not installed, you'll get a helpful error message:

```
RuntimeError: pdflatex not found. Please install a LaTeX distribution (e.g., TeX Live, MiKTeX).
```

## Parameters Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_file` | str | None | Path to save the .tex file (required for compile) |
| `compile` | bool | False | Whether to compile to PDF |
| `with_preamble` | bool | False | Include document preamble (auto-enabled when compile=True) |
| `output_dir` | str | None | Directory for PDF output (default: same as .tex file) |
| `header` | bool | True | Include version/timestamp comment |

## Tips

1. **Disable header for cleaner .tex files**: Use `header=False` if you don't want the version/timestamp comment in your .tex file.

2. **Keep .tex files for debugging**: When compilation fails, the .tex file is still saved, making it easier to debug LaTeX issues.

3. **Use output_dir for organization**: Keep source .tex files separate from compiled PDFs using the `output_dir` parameter.
