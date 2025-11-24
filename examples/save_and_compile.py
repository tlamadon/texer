"""Example of saving and compiling LaTeX plots to PDF."""

import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates

# Create a simple plot
x = np.linspace(0, 2 * np.pi, 100)
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
        legend=[r"$\sin(x)$", r"$\cos(x)$"],
    )
)

# Example 1: Save to .tex file
print("Saving to trig_plot.tex...")
plot.save_to_file("trig_plot.tex")
print("✓ Saved to trig_plot.tex")

# Example 2: Save without preamble (for inclusion in larger document)
print("\nSaving to trig_plot_content.tex (without preamble)...")
plot.save_to_file("trig_plot_content.tex", with_preamble=False)
print("✓ Saved to trig_plot_content.tex")

# Example 3: Compile to PDF
print("\nCompiling to PDF...")
try:
    pdf_path = plot.compile_to_pdf("trig_plot.tex")
    print(f"✓ Compiled successfully to: {pdf_path}")
except RuntimeError as e:
    print(f"✗ Compilation failed: {e}")
    print("\nNote: pdflatex must be installed to compile PDFs.")
    print("Install with:")
    print("  - Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-pictures")
    print("  - macOS: brew install --cask mactex")
    print("  - Windows: Download MiKTeX or TeX Live")
