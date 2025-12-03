#!/usr/bin/env python3
"""Demo of marker size control features in texer."""

from texer import (
    PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter,
    scatter_plot, evaluate
)


def static_marker_size_example():
    """Example 1: Static marker size for all points."""
    print("=" * 60)
    print("STATIC MARKER SIZE EXAMPLE")
    print("=" * 60)

    plot = PGFPlot(
        Axis(
            xlabel="X",
            ylabel="Y",
            title="Static Marker Size",
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    mark_size=5,  # All markers will be 5pt
                    only_marks=True,
                    coords=Coordinates(x=[1, 2, 3, 4, 5], y=[2, 4, 3, 5, 4]),
                )
            ],
        )
    )

    result = evaluate(plot, {})
    print(result)
    print()


def data_driven_marker_size_example():
    """Example 2: Data-driven marker sizes (bubble chart)."""
    print("=" * 60)
    print("DATA-DRIVEN MARKER SIZE EXAMPLE (Bubble Chart)")
    print("=" * 60)

    plot = PGFPlot(
        Axis(
            xlabel="X Position",
            ylabel="Y Position",
            title="Bubble Chart - Marker Size by Data",
            grid=True,
            plots=[
                AddPlot(
                    color="red",
                    mark="*",
                    only_marks=True,
                    scatter=True,  # Enable scatter mode
                    coords=Coordinates(
                        x=[1, 2, 3, 4, 5],
                        y=[2, 4, 3, 5, 4],
                        marker_size=[5, 10, 15, 20, 25]  # Different size for each point
                    ),
                )
            ],
        )
    )

    result = evaluate(plot, {})
    print(result)
    print()


def scatter_plot_helper_example():
    """Example 3: Using the scatter_plot helper function."""
    print("=" * 60)
    print("SCATTER_PLOT HELPER FUNCTION EXAMPLE")
    print("=" * 60)

    plot = scatter_plot(
        x=[1, 2, 3, 4, 5],
        y=[2, 4, 3, 5, 4],
        marker_size=[5, 10, 15, 20, 25],
        xlabel="X Value",
        ylabel="Y Value",
        title="Easy Bubble Chart",
        color="green",
        mark="o"
    )

    result = evaluate(plot, {})
    print(result)
    print()


def dynamic_marker_size_example():
    """Example 4: Dynamic marker sizes from data using Ref/Iter."""
    print("=" * 60)
    print("DYNAMIC MARKER SIZE FROM DATA")
    print("=" * 60)

    plot = PGFPlot(
        Axis(
            xlabel="Time (s)",
            ylabel="Performance",
            title=Ref("plot_title"),
            grid=True,
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    only_marks=True,
                    scatter=True,
                    coords=Coordinates(
                        Iter(Ref("measurements"), x=Ref("time"), y=Ref("perf"), marker_size=Ref("importance"))
                    ),
                )
            ],
        )
    )

    # Data with importance values that control marker size
    data = {
        "plot_title": "Performance Over Time (size = importance)",
        "measurements": [
            {"time": 0, "perf": 50, "importance": 5},
            {"time": 1, "perf": 60, "importance": 8},
            {"time": 2, "perf": 55, "importance": 12},
            {"time": 3, "perf": 70, "importance": 15},
            {"time": 4, "perf": 65, "importance": 20},
        ],
    }

    result = evaluate(plot, data)
    print(result)
    print()


def multiple_series_different_sizes_example():
    """Example 5: Multiple series with different marker sizes."""
    print("=" * 60)
    print("MULTIPLE SERIES WITH DIFFERENT STATIC SIZES")
    print("=" * 60)

    plot = PGFPlot(
        Axis(
            xlabel="X",
            ylabel="Y",
            title="Multiple Series",
            grid=True,
            legend_pos="north west",
            plots=[
                AddPlot(
                    color="blue",
                    mark="*",
                    mark_size=3,
                    only_marks=True,
                    coords=Coordinates(x=[1, 2, 3, 4, 5], y=[2, 4, 3, 5, 4]),
                ),
                AddPlot(
                    color="red",
                    mark="square*",
                    mark_size=6,
                    only_marks=True,
                    coords=Coordinates(x=[1, 2, 3, 4, 5], y=[3, 2, 4, 3, 5]),
                ),
                AddPlot(
                    color="green",
                    mark="triangle*",
                    mark_size=9,
                    only_marks=True,
                    coords=Coordinates(x=[1, 2, 3, 4, 5], y=[4, 5, 2, 4, 3]),
                ),
            ],
            legend=["Small (3pt)", "Medium (6pt)", "Large (9pt)"],
        )
    )

    result = evaluate(plot, {})
    print(result)
    print()


if __name__ == "__main__":
    static_marker_size_example()
    data_driven_marker_size_example()
    scatter_plot_helper_example()
    dynamic_marker_size_example()
    multiple_series_different_sizes_example()
