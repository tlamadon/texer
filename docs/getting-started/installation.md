# Installation

## From PyPI (recommended)

Install texer using pip:

```bash
pip install texer
```

## From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/yourusername/texer.git
cd texer
pip install -e .
```

## Optional Dependencies

### For Development

To install development dependencies (testing, type checking):

```bash
pip install -e ".[dev]"
```

### For Documentation

To build the documentation locally:

```bash
pip install -e ".[docs]"
```

Then serve the docs:

```bash
mkdocs serve
```

## LaTeX Requirements

### For PDF Compilation

If you want to compile LaTeX to PDF using `compile_to_pdf()`, you need a LaTeX distribution installed:

=== "Ubuntu/Debian"

    ```bash
    sudo apt-get install texlive-latex-base texlive-pictures
    ```

=== "macOS"

    ```bash
    brew install --cask mactex
    ```

=== "Windows"

    Download and install either:

    - [MiKTeX](https://miktex.org/)
    - [TeX Live](https://www.tug.org/texlive/)

### Required LaTeX Packages

texer generates LaTeX that requires these packages. They're typically included in standard LaTeX distributions:

- **For tables with rules**: `booktabs`
- **For colored text**: `xcolor`
- **For plots**: `pgfplots` (with `compat=1.18`)
- **For multiple subplots**: `pgfplots` with `groupplots` library
- **For multirow cells**: `multirow`

## Verify Installation

Check that texer is installed correctly:

```python
import texer
print(texer.__version__)
```

You should see the version number printed without errors.

## Next Steps

Now that you have texer installed, learn about:

- [Mental Model](mental-model.md) - How texer works
- [Core Concepts](core-concepts.md) - Understanding specs and evaluation
