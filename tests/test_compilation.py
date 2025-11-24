"""Integration tests that compile LaTeX to PDF."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest
from texer import (
    AddPlot,
    Axis,
    Cell,
    Cond,
    Coordinates,
    Format,
    GroupPlot,
    Iter,
    NextGroupPlot,
    PGFPlot,
    Ref,
    Row,
    Table,
    Tabular,
    evaluate,
)


def compile_latex(latex_code: str, filename: str = "test") -> Path:
    """
    Compile LaTeX code to PDF and return the path to the PDF.

    Args:
        latex_code: Complete LaTeX document with preamble
        filename: Base name for the output file

    Returns:
        Path to the generated PDF file

    Raises:
        AssertionError: If compilation fails
    """
    # Create a temporary directory for compilation
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        tex_file = tmppath / f"{filename}.tex"
        pdf_file = tmppath / f"{filename}.pdf"

        # Write LaTeX file
        tex_file.write_text(latex_code)

        # Compile with pdflatex
        # -interaction=nonstopmode: Don't stop on errors
        # -halt-on-error: Exit immediately on error
        # -output-directory: Specify output directory
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={tmppath}",
                str(tex_file),
            ],
            capture_output=True,
            text=True,
            cwd=tmppath,
        )

        # Check if compilation succeeded
        if result.returncode != 0 or not pdf_file.exists():
            # Print the log for debugging
            log_file = tmppath / f"{filename}.log"
            log_content = ""
            if log_file.exists():
                log_content = log_file.read_text()

            error_msg = f"LaTeX compilation failed!\n"
            error_msg += f"Return code: {result.returncode}\n"
            error_msg += f"STDOUT:\n{result.stdout}\n"
            error_msg += f"STDERR:\n{result.stderr}\n"
            if log_content:
                error_msg += f"LOG FILE:\n{log_content}\n"

            pytest.fail(error_msg)

        # Copy PDF to a persistent location for inspection if needed
        # For now, just verify it exists and has content
        assert pdf_file.exists(), "PDF file was not created"
        assert pdf_file.stat().st_size > 0, "PDF file is empty"

        return pdf_file


class TestTableCompilation:
    """Test that table LaTeX code compiles successfully."""

    def test_simple_table_compiles(self):
        """Test that a simple table compiles to PDF."""
        table = Table(
            Tabular(
                columns="lcc",
                header=Row("Name", "Value 1", "Value 2"),
                rows=[
                    Row("Item A", "10", "20"),
                    Row("Item B", "30", "40"),
                ],
            ),
            caption="Test Table",
            label="tab:test",
        )

        latex_code = table.render({})

        # Wrap in a complete document
        document = r"""\documentclass{article}
\usepackage{booktabs}
\begin{document}
""" + latex_code + r"""
\end{document}
"""

        # Should compile without errors
        compile_latex(document, "simple_table")

    def test_table_with_dynamic_data_compiles(self):
        """Test that a table with dynamic data compiles to PDF."""
        table = Table(
            Tabular(
                columns="lcc",
                header=Row("Name", "Value 1", "Value 2"),
                rows=Iter(
                    Ref("data"),
                    template=Row(
                        Cell(Ref("name"), bold=Ref("important")),
                        Format(Ref("value1"), ".2f"),
                        Format(Ref("value2"), ".1%"),
                    )
                ),
                toprule=True,
                bottomrule=True,
            ),
            caption=Ref("caption"),
            label="tab:dynamic",
        )

        data = {
            "caption": "Dynamic Test Table",
            "data": [
                {"name": "Sample A", "value1": 3.14159, "value2": 0.123, "important": True},
                {"name": "Sample B", "value1": 2.71828, "value2": 0.456, "important": False},
                {"name": "Sample C", "value1": 1.41421, "value2": 0.789, "important": True},
            ],
        }

        latex_code = evaluate(table, data)

        # Wrap in a complete document
        document = r"""\documentclass{article}
\usepackage{booktabs}
\begin{document}
""" + latex_code + r"""
\end{document}
"""

        # Should compile without errors
        compile_latex(document, "dynamic_table")

    def test_tabular_without_table_environment_compiles(self):
        """Test that a standalone Tabular compiles to PDF."""
        tabular = Tabular(
            columns="lcc",
            header=Row("A", "B", "C"),
            rows=[
                Row("1", "2", "3"),
                Row("4", "5", "6"),
            ],
            toprule=True,
            bottomrule=True,
        )

        latex_code = tabular.render({})

        # Wrap in a complete document
        document = r"""\documentclass{article}
\usepackage{booktabs}
\begin{document}
""" + latex_code + r"""
\end{document}
"""

        # Should compile without errors
        compile_latex(document, "standalone_tabular")


class TestPlotCompilation:
    """Test that PGFPlot LaTeX code compiles successfully."""

    def test_simple_plot_compiles(self):
        """Test that a simple plot compiles to PDF."""
        plot = PGFPlot(
            Axis(
                xlabel="X axis",
                ylabel="Y axis",
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates([(0, 0), (1, 1), (2, 4), (3, 9)]),
                    )
                ],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "simple_plot")

    def test_plot_with_dynamic_data_compiles(self):
        """Test that a plot with dynamic data compiles to PDF."""
        plot = PGFPlot(
            Axis(
                xlabel="Time (s)",
                ylabel="Temperature (K)",
                title=Ref("title"),
                legend_pos="north west",
                grid=True,
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates(
                            Iter(Ref("series1"), x=Ref("t"), y=Ref("temp"))
                        ),
                    ),
                    AddPlot(
                        color="red",
                        mark="square*",
                        style="dashed",
                        coords=Coordinates(
                            Iter(Ref("series2"), x=Ref("t"), y=Ref("temp"))
                        ),
                    ),
                ],
                legend=[Ref("legend1"), Ref("legend2")],
            )
        )

        data = {
            "title": "Temperature vs Time",
            "series1": [
                {"t": 0, "temp": 300},
                {"t": 1, "temp": 320},
                {"t": 2, "temp": 335},
                {"t": 3, "temp": 345},
            ],
            "series2": [
                {"t": 0, "temp": 290},
                {"t": 1, "temp": 310},
                {"t": 2, "temp": 325},
                {"t": 3, "temp": 340},
            ],
            "legend1": "Experiment 1",
            "legend2": "Experiment 2",
        }

        latex_code = evaluate(plot, data)

        # Wrap with preamble
        document = r"""\documentclass{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
""" + latex_code + r"""
\end{document}
"""

        # Should compile without errors
        compile_latex(document, "dynamic_plot")

    def test_expression_plot_compiles(self):
        """Test that a plot with mathematical expressions compiles to PDF."""
        plot = PGFPlot(
            Axis(
                xlabel="$x$",
                ylabel="$f(x)$",
                xmin=-5,
                xmax=5,
                ymin=-1.5,
                ymax=1.5,
                grid=True,
                plots=[
                    AddPlot(
                        expression="sin(deg(x))",
                        domain="-5:5",
                        samples=100,
                        color="blue",
                        thick=True,
                        no_marks=True,
                    ),
                    AddPlot(
                        expression="cos(deg(x))",
                        domain="-5:5",
                        samples=100,
                        color="red",
                        style="dashed",
                        thick=True,
                        no_marks=True,
                    ),
                ],
                legend=["$\\sin(x)$", "$\\cos(x)$"],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "expression_plot")

    def test_plot_with_multiple_series_compiles(self):
        """Test that a plot with multiple series compiles to PDF."""
        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                grid=True,
                legend_pos="south east",
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates([(0, 0), (1, 1), (2, 4), (3, 9)]),
                    ),
                    AddPlot(
                        color="red",
                        mark="square*",
                        style="dashed",
                        coords=Coordinates([(0, 1), (1, 2), (2, 3), (3, 4)]),
                    ),
                    AddPlot(
                        color="green",
                        mark="triangle*",
                        coords=Coordinates([(0, 2), (1, 1.5), (2, 2.5), (3, 2)]),
                    ),
                ],
                legend=["Quadratic", "Linear", "Wavy"],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "multi_series_plot")

    def test_plot_with_numpy_arrays_compiles(self):
        """Test that a plot with numpy arrays compiles to PDF."""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("NumPy not installed")

        # Generate some data with numpy
        x = np.linspace(0, 2 * np.pi, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)

        plot = PGFPlot(
            Axis(
                xlabel="$x$",
                ylabel="$f(x)$",
                title="Trigonometric Functions",
                grid=True,
                legend_pos="south east",
                plots=[
                    AddPlot(
                        color="blue",
                        no_marks=True,
                        thick=True,
                        coords=Coordinates(x=x, y=y1),
                    ),
                    AddPlot(
                        color="red",
                        no_marks=True,
                        thick=True,
                        style="dashed",
                        coords=Coordinates(x=x, y=y2),
                    ),
                ],
                legend=["$\\sin(x)$", "$\\cos(x)$"],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "numpy_plot")

    def test_plot_with_list_arrays_compiles(self):
        """Test that a plot with separate x, y lists compiles to PDF."""
        # Generate data with plain Python lists
        x = [i * 0.5 for i in range(20)]
        y = [xi ** 2 for xi in x]

        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                title="Parabola",
                grid=True,
                plots=[
                    AddPlot(
                        color="purple",
                        mark="*",
                        coords=Coordinates(x=x, y=y),
                    )
                ],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "list_arrays_plot")


class TestGroupPlotCompilation:
    """Test that GroupPlot LaTeX code compiles successfully."""

    def test_simple_groupplot_compiles(self):
        """Test that a simple groupplot compiles to PDF."""
        plot = PGFPlot(
            GroupPlot(
                group_size="1 by 2",
                plots=[
                    NextGroupPlot(
                        title="Left Plot",
                        xlabel="X",
                        ylabel="Y",
                        plots=[
                            AddPlot(coords=Coordinates([(0, 0), (1, 1), (2, 4)]))
                        ],
                    ),
                    NextGroupPlot(
                        title="Right Plot",
                        xlabel="X",
                        ylabel="Y",
                        plots=[
                            AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 5)]))
                        ],
                    ),
                ],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "simple_groupplot")

    def test_2x2_groupplot_compiles(self):
        """Test that a 2x2 groupplot compiles to PDF."""
        plot = PGFPlot(
            GroupPlot(
                group_size="2 by 2",
                width="5cm",
                height="4cm",
                horizontal_sep="1.5cm",
                vertical_sep="1.5cm",
                plots=[
                    NextGroupPlot(
                        title="Plot 1",
                        plots=[AddPlot(coords=Coordinates([(0, 0), (1, 1)]))],
                    ),
                    NextGroupPlot(
                        title="Plot 2",
                        plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
                    ),
                    NextGroupPlot(
                        title="Plot 3",
                        plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3)]))],
                    ),
                    NextGroupPlot(
                        title="Plot 4",
                        plots=[AddPlot(coords=Coordinates([(0, 3), (1, 4)]))],
                    ),
                ],
            )
        )

        latex_code = plot.with_preamble()

        # Should compile without errors
        compile_latex(latex_code, "2x2_groupplot")

    def test_groupplot_with_dynamic_data_compiles(self):
        """Test that a groupplot with dynamic data compiles to PDF."""
        plot = PGFPlot(
            GroupPlot(
                group_size="2 by 2",
                width="5cm",
                height="4cm",
                plots=[
                    NextGroupPlot(
                        title=Ref("title1"),
                        xlabel="Time (s)",
                        ylabel="Temperature (K)",
                        grid=True,
                        plots=[
                            AddPlot(
                                color="blue",
                                mark="*",
                                coords=Coordinates(
                                    Iter(Ref("dataset1"), x=Ref("t"), y=Ref("temp"))
                                ),
                            )
                        ],
                    ),
                    NextGroupPlot(
                        title=Ref("title2"),
                        xlabel="Time (s)",
                        ylabel="Pressure (Pa)",
                        grid=True,
                        plots=[
                            AddPlot(
                                color="red",
                                mark="square*",
                                coords=Coordinates(
                                    Iter(Ref("dataset2"), x=Ref("t"), y=Ref("pressure"))
                                ),
                            )
                        ],
                    ),
                    NextGroupPlot(
                        title=Ref("title3"),
                        xlabel="Time (s)",
                        ylabel="Volume (L)",
                        grid=True,
                        plots=[
                            AddPlot(
                                color="green",
                                mark="triangle*",
                                coords=Coordinates(
                                    Iter(Ref("dataset3"), x=Ref("t"), y=Ref("volume"))
                                ),
                            )
                        ],
                    ),
                    NextGroupPlot(
                        title=Ref("title4"),
                        xlabel="Time (s)",
                        ylabel="Density (kg/m³)",
                        grid=True,
                        plots=[
                            AddPlot(
                                color="purple",
                                mark="diamond*",
                                coords=Coordinates(
                                    Iter(Ref("dataset4"), x=Ref("t"), y=Ref("density"))
                                ),
                            )
                        ],
                    ),
                ],
            )
        )

        data = {
            "title1": "Temperature",
            "title2": "Pressure",
            "title3": "Volume",
            "title4": "Density",
            "dataset1": [
                {"t": 0, "temp": 300},
                {"t": 1, "temp": 320},
                {"t": 2, "temp": 335},
            ],
            "dataset2": [
                {"t": 0, "pressure": 101325},
                {"t": 1, "pressure": 102000},
                {"t": 2, "pressure": 103500},
            ],
            "dataset3": [
                {"t": 0, "volume": 1.0},
                {"t": 1, "volume": 1.1},
                {"t": 2, "volume": 1.15},
            ],
            "dataset4": [
                {"t": 0, "density": 1.2},
                {"t": 1, "density": 1.15},
                {"t": 2, "density": 1.12},
            ],
        }

        latex_code = evaluate(plot, data)

        # Wrap with preamble
        document = r"""\documentclass{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{groupplots}
\begin{document}
""" + latex_code + r"""
\end{document}
"""

        # Should compile without errors
        compile_latex(document, "dynamic_groupplot")


class TestMixedContentCompilation:
    """Test that mixed content (tables and plots) compile successfully."""

    def test_table_and_plot_in_same_document(self):
        """Test that a document with both table and plot compiles."""
        table = Table(
            Tabular(
                columns="lcc",
                header=Row("Name", "Value 1", "Value 2"),
                rows=[
                    Row("Item A", "10", "20"),
                    Row("Item B", "30", "40"),
                ],
                toprule=True,
                bottomrule=True,
            ),
            caption="Results Table",
            label="tab:results",
        )

        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates([(0, 10), (1, 30)]),
                    )
                ],
            )
        )

        table_latex = table.render({})
        plot_latex = plot.render({})

        # Combine in a document
        document = r"""\documentclass{article}
\usepackage{booktabs}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}

\section{Results}

""" + table_latex + r"""

\section{Visualization}

\begin{figure}[htbp]
\centering
""" + plot_latex + r"""
\caption{Results Plot}
\label{fig:results}
\end{figure}

\end{document}
"""

        # Should compile without errors
        compile_latex(document, "mixed_content")
