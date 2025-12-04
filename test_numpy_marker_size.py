#!/usr/bin/env python3
"""Test NumPy array interface for marker_size and compile to PDF."""

import numpy as np
from texer import PGFPlot, Axis, AddPlot, Coordinates, scatter_plot


def test_numpy_arrays_with_marker_size():
    """Test that NumPy arrays work for x, y, and marker_size."""
    print("=" * 60)
    print("TEST: NumPy Arrays with Marker Size")
    print("=" * 60)

    # Create NumPy arrays
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 4, 3, 5, 4])
    sizes = np.array([5, 10, 15, 20, 25])

    print(f"x type: {type(x)}, shape: {x.shape}")
    print(f"y type: {type(y)}, shape: {y.shape}")
    print(f"sizes type: {type(sizes)}, shape: {sizes.shape}")

    plot = PGFPlot(
        Axis(
            xlabel="X Position",
            ylabel="Y Position",
            title="NumPy Array Bubble Chart",
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    only_marks=True,
                    scatter=True,
                    coords=Coordinates(x=x, y=y, marker_size=sizes),
                )
            ],
        )
    )

    latex_output = plot.render({})
    print("\nGenerated LaTeX:")
    print(latex_output)

    # Verify the coordinates are correct (bracket notation for meta data)
    assert "(1, 2) [5]" in latex_output
    assert "(2, 4) [10]" in latex_output
    assert "(3, 3) [15]" in latex_output
    assert "(4, 5) [20]" in latex_output
    assert "(5, 4) [25]" in latex_output
    assert "scatter" in latex_output
    assert "point meta=explicit" in latex_output

    print("\n✓ Test passed: NumPy arrays work correctly")
    return latex_output


def test_numpy_3d_with_marker_size():
    """Test NumPy arrays with 3D coordinates and marker size."""
    print("\n" + "=" * 60)
    print("TEST: NumPy 3D Arrays with Marker Size")
    print("=" * 60)

    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])
    z = np.array([1, 4, 9])
    sizes = np.array([5, 10, 15])

    plot = PGFPlot(
        Axis(
            xlabel="X",
            ylabel="Y",
            zlabel="Z",
            title="3D NumPy Bubble Chart",
            plots=[
                AddPlot(
                    color="red",
                    mark="*",
                    only_marks=True,
                    scatter=True,
                    coords=Coordinates(x=x, y=y, z=z, marker_size=sizes),
                )
            ],
        )
    )

    latex_output = plot.render({})
    print("\nGenerated LaTeX:")
    print(latex_output)

    # Verify 3D coordinates with marker size (bracket notation for meta)
    assert "(1, 1, 1) [5]" in latex_output
    assert "(2, 2, 4) [10]" in latex_output
    assert "(3, 3, 9) [15]" in latex_output

    print("\n✓ Test passed: 3D NumPy arrays work correctly")
    return latex_output


def test_scatter_plot_helper_with_numpy():
    """Test scatter_plot helper function with NumPy arrays."""
    print("\n" + "=" * 60)
    print("TEST: scatter_plot() Helper with NumPy")
    print("=" * 60)

    x = np.linspace(0, 10, 20)
    y = np.sin(x)
    sizes = np.linspace(3, 20, 20)

    plot = scatter_plot(
        x=x,
        y=y,
        marker_size=sizes,
        xlabel="X Value",
        ylabel="sin(X)",
        title="Sine Wave Bubble Chart",
        color="green",
        mark="o"
    )

    latex_output = plot.render({})
    print("\nGenerated LaTeX (first 500 chars):")
    print(latex_output[:500] + "...")

    assert "scatter" in latex_output
    assert "point meta=explicit" in latex_output

    print("\n✓ Test passed: scatter_plot() helper works with NumPy")
    return latex_output


def create_and_compile_pdf():
    """Create a complete LaTeX document and compile to PDF."""
    print("\n" + "=" * 60)
    print("COMPILE: Creating PDF from NumPy data")
    print("=" * 60)

    # Create a nice example with NumPy
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    y = np.array([2.3, 4.1, 3.5, 5.2, 4.8, 6.1, 5.5, 7.2, 6.8, 8.1])
    sizes = np.array([5, 8, 12, 10, 15, 18, 14, 20, 22, 25])

    plot = PGFPlot(
        Axis(
            xlabel="Experiment Number",
            ylabel="Measurement Value",
            title="Experimental Results (marker size = confidence)",
            grid=True,
            legend_pos="north west",
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    only_marks=True,
                    scatter=True,
                    coords=Coordinates(x=x, y=y, marker_size=sizes),
                )
            ],
        )
    )

    # Save to file
    tex_file = "/workspaces/texer/test_numpy_marker_size.tex"
    plot.save_to_file(tex_file, {}, with_preamble=True)
    print(f"\n✓ Saved LaTeX to: {tex_file}")

    # Try to compile to PDF
    import subprocess
    import shutil

    if shutil.which("pdflatex"):
        try:
            print("\nCompiling to PDF...")
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd="/workspaces/texer"
            )

            # Check if PDF was created (pdflatex sometimes returns non-zero even on success)
            import os
            pdf_file = "/workspaces/texer/test_numpy_marker_size.pdf"
            if os.path.exists(pdf_file):
                file_size = os.path.getsize(pdf_file)
                print(f"✓ PDF compilation successful!")
                print(f"  Output: test_numpy_marker_size.pdf ({file_size} bytes)")
            else:
                print("✗ PDF compilation failed")
                print("STDOUT:", result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                print("STDERR:", result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        except subprocess.TimeoutExpired:
            print("✗ PDF compilation timed out")
        except Exception as e:
            print(f"✗ PDF compilation error: {e}")
    else:
        print("⚠ pdflatex not found, skipping PDF compilation")

    return tex_file


if __name__ == "__main__":
    try:
        # Run all tests
        test_numpy_arrays_with_marker_size()
        test_numpy_3d_with_marker_size()
        test_scatter_plot_helper_with_numpy()
        create_and_compile_pdf()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
