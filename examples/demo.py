#!/usr/bin/env python3
"""Demo of texer package capabilities."""

from texer import (
    # Specs
    Ref, Iter, Format, Cond, Raw,
    # Tables
    Table, Tabular, Row, Cell,
    # PGFPlots
    PGFPlot, Axis, AddPlot, Coordinates, GroupPlot, NextGroupPlot,
    # Evaluation
    evaluate,
)


def table_example():
    """Generate a LaTeX table from data."""
    print("=" * 60)
    print("TABLE EXAMPLE")
    print("=" * 60)

    # Define the table structure with specs
    table = Table(
        Tabular(
            columns="lcc",
            header=Row("Name", "Value 1", "Value 2"),
            rows=Iter(
                Ref("data"),
                template=Row(
                    Cell(Ref("name"), bold=Cond(Ref("important"), True, False)),
                    Format(Ref("value1"), ".2f"),
                    Format(Ref("value2"), ".1%"),
                )
            ),
            toprule=True,
            bottomrule=True,
        ),
        caption=Ref("table_caption"),
        label="tab:results",
    )

    # Sample data
    data = {
        "table_caption": "Experimental Results",
        "data": [
            {"name": "Sample A", "value1": 3.14159, "value2": 0.123, "important": True},
            {"name": "Sample B", "value1": 2.71828, "value2": 0.456, "important": False},
            {"name": "Sample C", "value1": 1.41421, "value2": 0.789, "important": True},
        ],
    }

    # Generate LaTeX
    result = evaluate(table, data)
    print(result)
    print()


def pgfplot_example():
    """Generate a PGFPlot from data."""
    print("=" * 60)
    print("PGFPLOT EXAMPLE")
    print("=" * 60)

    # Define the plot structure
    plot = PGFPlot(
        Axis(
            xlabel="Time (s)",
            ylabel="Temperature (K)",
            title=Ref("plot_title"),
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

    # Sample data
    data = {
        "plot_title": "Temperature vs Time",
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

    # Generate LaTeX
    result = evaluate(plot, data)
    print(result)
    print()


def conditional_formatting_example():
    """Show conditional formatting in tables."""
    print("=" * 60)
    print("CONDITIONAL FORMATTING EXAMPLE")
    print("=" * 60)

    table = Tabular(
        columns="lcc",
        header=Row("Metric", "Value", "Status"),
        rows=Iter(
            Ref("metrics"),
            template=Row(
                Ref("name"),
                Format(Ref("value"), ".1f"),
                Cond(
                    Ref("value") > Ref("threshold"),
                    Raw(r"\textcolor{green}{PASS}"),
                    Raw(r"\textcolor{red}{FAIL}"),
                ),
            )
        ),
        toprule=True,
        bottomrule=True,
    )

    data = {
        "metrics": [
            {"name": "Accuracy", "value": 95.5, "threshold": 90},
            {"name": "Precision", "value": 88.2, "threshold": 90},
            {"name": "Recall", "value": 92.1, "threshold": 90},
        ]
    }

    result = evaluate(table, data)
    print(result)
    print()


def expression_plot_example():
    """Show a mathematical function plot."""
    print("=" * 60)
    print("EXPRESSION PLOT EXAMPLE")
    print("=" * 60)

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

    result = evaluate(plot, {})
    print(result)
    print()


def groupplot_example():
    """Generate a GroupPlot with multiple subplots in a grid."""
    print("=" * 60)
    print("GROUPPLOT EXAMPLE")
    print("=" * 60)

    # Define a 2x2 grid of plots
    plot = PGFPlot(
        GroupPlot(
            group_size="2 by 2",
            width="5cm",
            height="4cm",
            horizontal_sep="1.5cm",
            vertical_sep="1.5cm",
            xlabels_at="edge bottom",
            ylabels_at="edge left",
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
                    legend=[Ref("label1")],
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
                    legend=[Ref("label2")],
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
                    legend=[Ref("label3")],
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
                    legend=[Ref("label4")],
                ),
            ],
        )
    )

    # Sample data for all four subplots
    data = {
        "title1": "Temperature",
        "title2": "Pressure",
        "title3": "Volume",
        "title4": "Density",
        "label1": "Sensor A",
        "label2": "Sensor B",
        "label3": "Sensor C",
        "label4": "Sensor D",
        "dataset1": [
            {"t": 0, "temp": 300},
            {"t": 1, "temp": 320},
            {"t": 2, "temp": 335},
            {"t": 3, "temp": 345},
        ],
        "dataset2": [
            {"t": 0, "pressure": 101325},
            {"t": 1, "pressure": 102000},
            {"t": 2, "pressure": 103500},
            {"t": 3, "pressure": 105000},
        ],
        "dataset3": [
            {"t": 0, "volume": 1.0},
            {"t": 1, "volume": 1.1},
            {"t": 2, "volume": 1.15},
            {"t": 3, "volume": 1.2},
        ],
        "dataset4": [
            {"t": 0, "density": 1.2},
            {"t": 1, "density": 1.15},
            {"t": 2, "density": 1.12},
            {"t": 3, "density": 1.1},
        ],
    }

    # Generate LaTeX
    result = evaluate(plot, data)
    print(result)
    print()


def simple_groupplot_example():
    """Generate a simple 1x2 groupplot with expression-based plots."""
    print("=" * 60)
    print("SIMPLE GROUPPLOT EXAMPLE (1x2)")
    print("=" * 60)

    plot = PGFPlot(
        GroupPlot(
            group_size="1 by 2",
            width="6cm",
            height="5cm",
            plots=[
                NextGroupPlot(
                    title="Sine Function",
                    xlabel="$x$",
                    ylabel="$\\sin(x)$",
                    xmin=-3.14,
                    xmax=3.14,
                    grid=True,
                    plots=[
                        AddPlot(
                            expression="sin(deg(x))",
                            domain="-3.14:3.14",
                            samples=50,
                            color="blue",
                            thick=True,
                            no_marks=True,
                        )
                    ],
                ),
                NextGroupPlot(
                    title="Cosine Function",
                    xlabel="$x$",
                    ylabel="$\\cos(x)$",
                    xmin=-3.14,
                    xmax=3.14,
                    grid=True,
                    plots=[
                        AddPlot(
                            expression="cos(deg(x))",
                            domain="-3.14:3.14",
                            samples=50,
                            color="red",
                            thick=True,
                            no_marks=True,
                        )
                    ],
                ),
            ],
        )
    )

    result = evaluate(plot, {})
    print(result)
    print()


if __name__ == "__main__":
    table_example()
    pgfplot_example()
    conditional_formatting_example()
    expression_plot_example()
    groupplot_example()
    simple_groupplot_example()
