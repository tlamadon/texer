#!/usr/bin/env python3
"""Generate images for documentation examples.

This script compiles LaTeX examples to PDF and converts them to PNG images
for inclusion in the documentation.
"""

import subprocess
import sys
from pathlib import Path
import shutil

# Import texer
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from texer import (
    PGFPlot, Axis, AddPlot, Coordinates, GroupPlot, NextGroupPlot,
    Table, Tabular, Row, Cell, MultiColumn,
    Ref, Iter, Format, evaluate
)


def check_dependencies():
    """Check if required tools are available."""
    required = ["pdflatex", "convert"]
    missing = []

    for tool in required:
        if shutil.which(tool) is None:
            missing.append(tool)

    if missing:
        print(f"Error: Missing required tools: {', '.join(missing)}")
        print("\nInstall instructions:")
        print("  - pdflatex: Install texlive-latex-base texlive-pictures")
        print("  - convert: Install imagemagick")
        return False

    return True


def compile_latex_to_png(latex_content: str, output_path: Path, crop: bool = True):
    """Compile LaTeX to PNG image.

    Args:
        latex_content: Complete LaTeX document content
        output_path: Path for output PNG file
        crop: Whether to crop whitespace
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary directory
    temp_dir = output_path.parent / ".temp"
    temp_dir.mkdir(exist_ok=True)

    tex_file = temp_dir / f"{output_path.stem}.tex"
    pdf_file = temp_dir / f"{output_path.stem}.pdf"

    # Write LaTeX file
    tex_file.write_text(latex_content)

    # Compile to PDF
    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={temp_dir}",
                str(tex_file),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"Error compiling {tex_file.name}:")
            print(result.stdout[-1000:])  # Last 1000 chars
            return False

    except subprocess.TimeoutExpired:
        print(f"Timeout compiling {tex_file.name}")
        return False
    except Exception as e:
        print(f"Error compiling {tex_file.name}: {e}")
        return False

    if not pdf_file.exists():
        print(f"PDF not generated for {tex_file.name}")
        return False

    # Convert PDF to PNG
    try:
        convert_args = [
            "convert",
            "-density", "300",  # High DPI
            "-quality", "100",
            str(pdf_file),
        ]

        if crop:
            convert_args.extend(["-trim", "+repage"])

        convert_args.extend([
            "-background", "white",
            "-alpha", "remove",
            str(output_path),
        ])

        result = subprocess.run(
            convert_args,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"Error converting {pdf_file.name} to PNG:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"Error converting {pdf_file.name}: {e}")
        return False

    print(f"✓ Generated {output_path}")
    return True


def generate_plot_examples(output_dir: Path):
    """Generate example plot images."""
    print("\n=== Generating Plot Examples ===")

    # Example 1: Basic plot
    plot1 = PGFPlot(
        Axis(
            xlabel="Time (s)",
            ylabel="Distance (m)",
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    coords=Coordinates([(0, 0), (1, 2), (2, 8), (3, 18)]),
                )
            ],
        )
    )

    latex1 = r"""\documentclass[border=2mm]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
""" + evaluate(plot1, {}) + "\n\\end{document}"

    compile_latex_to_png(latex1, output_dir / "plots" / "basic_plot.png")

    # Example 2: Multiple series
    plot2 = PGFPlot(
        Axis(
            xlabel="Time (h)",
            ylabel="Temperature (°C)",
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    coords=Coordinates([(0, 20), (1, 22), (2, 25)]),
                ),
                AddPlot(
                    color="red",
                    mark="square*",
                    coords=Coordinates([(0, 19), (1, 21), (2, 24)]),
                ),
                AddPlot(
                    color="green",
                    mark="triangle*",
                    coords=Coordinates([(0, 21), (1, 23), (2, 26)]),
                ),
            ],
            legend=["Sensor 1", "Sensor 2", "Sensor 3"],
            legend_pos="north west",
        )
    )

    latex2 = r"""\documentclass[border=2mm]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
""" + evaluate(plot2, {}) + "\n\\end{document}"

    compile_latex_to_png(latex2, output_dir / "plots" / "multiple_series.png")

    # Example 3: GroupPlot
    plot3 = PGFPlot(
        GroupPlot(
            group_size="2 by 2",
            width="5cm",
            height="4cm",
            plots=[
                NextGroupPlot(
                    title="Plot 1",
                    plots=[AddPlot(coords=Coordinates([(0, 0), (1, 1), (2, 4)]))],
                ),
                NextGroupPlot(
                    title="Plot 2",
                    plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 3)]))],
                ),
                NextGroupPlot(
                    title="Plot 3",
                    plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3), (2, 5)]))],
                ),
                NextGroupPlot(
                    title="Plot 4",
                    plots=[AddPlot(coords=Coordinates([(0, 3), (1, 4), (2, 6)]))],
                ),
            ],
        )
    )

    latex3 = r"""\documentclass[border=2mm]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{groupplots}
\begin{document}
""" + evaluate(plot3, {}) + "\n\\end{document}"

    compile_latex_to_png(latex3, output_dir / "plots" / "groupplot.png")

    # Example 4: Cycle list
    plot4 = PGFPlot(
        Axis(
            xlabel="X",
            ylabel="Y",
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
                {"color": "green", "mark": "triangle*"},
            ],
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 4)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3), (2, 5)])),
                AddPlot(coords=Coordinates([(0, 0.5), (1, 1.5), (2, 3)])),
            ],
            legend=["Series A", "Series B", "Series C"],
            legend_pos="north west",
        )
    )

    latex4 = r"""\documentclass[border=2mm]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
""" + evaluate(plot4, {}) + "\n\\end{document}"

    compile_latex_to_png(latex4, output_dir / "plots" / "cycle_list.png")


def generate_table_examples(output_dir: Path):
    """Generate example table images."""
    print("\n=== Generating Table Examples ===")

    # Example 1: Basic table
    table1 = Tabular(
        columns="lcc",
        header=Row("Name", "Value", "Unit"),
        rows=[
            Row("Length", "42", "m"),
            Row("Mass", "100", "kg"),
            Row("Time", "5", "s"),
        ],
        toprule=True,
        bottomrule=True,
    )

    latex1 = r"""\documentclass[border=2mm]{standalone}
\usepackage{booktabs}
\begin{document}
""" + evaluate(table1, {}) + "\n\\end{document}"

    compile_latex_to_png(latex1, output_dir / "tables" / "basic_table.png")

    # Example 2: Formatted cells
    table2 = Tabular(
        columns="lcc",
        header=Row(
            Cell("Experiment", bold=True),
            Cell("Result", bold=True),
            Cell("Error", bold=True),
        ),
        rows=[
            Row(Cell("Trial A", italic=True), "3.142", "2.3%"),
            Row(Cell("Trial B", italic=True), "2.718", "1.5%"),
            Row(Cell("Trial C", italic=True), "1.414", "4.2%"),
        ],
        toprule=True,
        bottomrule=True,
    )

    latex2 = r"""\documentclass[border=2mm]{standalone}
\usepackage{booktabs}
\begin{document}
""" + evaluate(table2, {}) + "\n\\end{document}"

    compile_latex_to_png(latex2, output_dir / "tables" / "formatted_table.png")

    # Example 3: MultiColumn
    table3 = Tabular(
        columns="lccc",
        rows=[
            Row(
                "Category",
                MultiColumn(3, "c", Cell("Measurements", bold=True)),
            ),
            Row("", "A", "B", "C"),
            Row("Test 1", "1.2", "2.3", "3.4"),
            Row("Test 2", "4.5", "5.6", "6.7"),
        ],
        toprule=True,
        bottomrule=True,
    )

    latex3 = r"""\documentclass[border=2mm]{standalone}
\usepackage{booktabs}
\begin{document}
""" + evaluate(table3, {}) + "\n\\end{document}"

    compile_latex_to_png(latex3, output_dir / "tables" / "multicolumn_table.png")


def main():
    """Main entry point."""
    if not check_dependencies():
        return 1

    # Output directory
    output_dir = Path(__file__).parent.parent / "docs" / "assets" / "images"

    # Generate examples
    try:
        generate_plot_examples(output_dir)
        generate_table_examples(output_dir)

        print("\n✓ All images generated successfully!")
        print(f"  Output directory: {output_dir}")

        # Clean up temp directories
        for temp_dir in output_dir.glob("*/.temp"):
            shutil.rmtree(temp_dir)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
