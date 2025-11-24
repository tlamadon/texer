"""Tests for PGFPlots generation."""

import pytest
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate, GroupPlot, NextGroupPlot


class TestCoordinates:
    def test_static_coordinates(self):
        coords = Coordinates([(0, 1), (1, 2), (2, 4)])
        result = coords.render({})
        assert result == "coordinates {(0, 1) (1, 2) (2, 4)}"

    def test_dynamic_coordinates(self):
        coords = Coordinates(
            Iter(Ref("points"), x=Ref("x"), y=Ref("y"))
        )
        data = {"points": [{"x": 0, "y": 1}, {"x": 1, "y": 4}]}
        result = coords.render(data)
        assert result == "coordinates {(0, 1) (1, 4)}"

    def test_3d_coordinates(self):
        coords = Coordinates([(0, 0, 1), (1, 1, 2)])
        result = coords.render({})
        assert result == "coordinates {(0, 0, 1) (1, 1, 2)}"


class TestAddPlot:
    def test_simple_addplot(self):
        plot = AddPlot(
            color="blue",
            mark="*",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "\\addplot" in result
        assert "color=blue" in result
        assert "mark=*" in result
        assert "coordinates" in result

    def test_expression_plot(self):
        plot = AddPlot(
            expression="x^2",
            domain="0:5",
            samples=100,
        )
        result = plot.render({})
        assert "domain=0:5" in result
        assert "samples=100" in result
        assert "{x^2}" in result

    def test_only_marks(self):
        plot = AddPlot(
            only_marks=True,
            coords=Coordinates([(0, 1)]),
        )
        result = plot.render({})
        assert "only marks" in result


class TestAxis:
    def test_basic_axis(self):
        axis = Axis(
            xlabel="Time (s)",
            ylabel="Value",
            plots=[AddPlot(coords=Coordinates([(0, 1)]))],
        )
        result = axis.render({})
        assert "\\begin{axis}" in result
        assert "xlabel={Time (s)}" in result
        assert "ylabel=Value" in result  # No braces for simple value
        assert "\\end{axis}" in result

    def test_axis_with_limits(self):
        axis = Axis(
            xmin=0,
            xmax=10,
            ymin=-5,
            ymax=5,
            plots=[],
        )
        result = axis.render({})
        assert "xmin=0" in result
        assert "xmax=10" in result
        assert "ymin=-5" in result
        assert "ymax=5" in result

    def test_axis_with_legend(self):
        axis = Axis(
            plots=[AddPlot(coords=Coordinates([(0, 1)]))],
            legend=["Series A"],
            legend_pos="north west",
        )
        result = axis.render({})
        assert "legend pos={north west}" in result
        assert "\\legend{Series A}" in result

    def test_axis_with_grid(self):
        axis = Axis(grid=True, plots=[])
        result = axis.render({})
        assert "grid=major" in result

    def test_dynamic_labels(self):
        axis = Axis(
            xlabel=Ref("x_label"),
            ylabel=Ref("y_label"),
            plots=[],
        )
        data = {"x_label": "Distance (m)", "y_label": "Speed (m/s)"}
        result = axis.render(data)
        assert "xlabel={Distance (m)}" in result
        assert "ylabel={Speed (m/s)}" in result


class TestPGFPlot:
    def test_complete_plot(self):
        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates([(0, 0), (1, 1), (2, 4)]),
                    )
                ],
            )
        )
        result = plot.render({})
        assert "\\begin{tikzpicture}" in result
        assert "\\begin{axis}" in result
        assert "\\addplot" in result
        assert "\\end{axis}" in result
        assert "\\end{tikzpicture}" in result

    def test_plot_with_scale(self):
        plot = PGFPlot(
            Axis(plots=[]),
            scale=0.8,
        )
        result = plot.render({})
        assert "scale=0.8" in result

    def test_with_preamble(self):
        plot = PGFPlot(Axis(plots=[]))
        result = plot.with_preamble()
        assert "\\documentclass{standalone}" in result
        assert "\\usepackage{pgfplots}" in result
        assert "\\pgfplotsset{compat=1.18}" in result
        assert "\\begin{document}" in result
        assert "\\end{document}" in result


class TestDynamicPlot:
    def test_plot_from_data(self):
        """Test the key use case: generating plot from data."""
        plot = PGFPlot(
            Axis(
                xlabel="Time (s)",
                ylabel="Temperature (K)",
                legend_pos="north west",
                plots=[
                    AddPlot(
                        color="blue",
                        mark="*",
                        coords=Coordinates(
                            Iter(Ref("data_points"), x=Ref("t"), y=Ref("temp"))
                        ),
                    )
                ],
                legend=[Ref("legend_label")],
            )
        )

        data = {
            "data_points": [
                {"t": 0, "temp": 300},
                {"t": 1, "temp": 310},
                {"t": 2, "temp": 315},
            ],
            "legend_label": "Experiment 1",
        }

        result = evaluate(plot, data)

        assert "xlabel={Time (s)}" in result
        assert "ylabel={Temperature (K)}" in result
        assert "coordinates {(0, 300) (1, 310) (2, 315)}" in result
        assert "\\legend{Experiment 1}" in result


class TestGroupPlot:
    def test_basic_groupplot(self):
        """Test basic groupplot creation with 2x2 layout."""
        groupplot = GroupPlot(
            group_size="2 by 2",
            plots=[
                NextGroupPlot(
                    title="Plot 1",
                    plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
                ),
                NextGroupPlot(
                    title="Plot 2",
                    plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3)]))],
                ),
                NextGroupPlot(
                    title="Plot 3",
                    plots=[AddPlot(coords=Coordinates([(0, 3), (1, 4)]))],
                ),
                NextGroupPlot(
                    title="Plot 4",
                    plots=[AddPlot(coords=Coordinates([(0, 4), (1, 5)]))],
                ),
            ],
        )
        result = groupplot.render({})
        assert "\\begin{groupplot}" in result
        assert "group size={2 by 2}" in result
        assert "\\nextgroupplot" in result
        assert result.count("\\nextgroupplot") == 4
        assert "\\end{groupplot}" in result

    def test_groupplot_with_common_options(self):
        """Test groupplot with common options applied to all subplots."""
        groupplot = GroupPlot(
            group_size="1 by 2",
            width="6cm",
            height="4cm",
            xmin=0,
            xmax=10,
            plots=[
                NextGroupPlot(plots=[]),
                NextGroupPlot(plots=[]),
            ],
        )
        result = groupplot.render({})
        assert "width=6cm" in result
        assert "height=4cm" in result
        assert "xmin=0" in result
        assert "xmax=10" in result

    def test_groupplot_with_separations(self):
        """Test groupplot with custom spacing."""
        groupplot = GroupPlot(
            group_size="2 by 1",
            horizontal_sep="2cm",
            vertical_sep="1.5cm",
            plots=[
                NextGroupPlot(plots=[]),
                NextGroupPlot(plots=[]),
            ],
        )
        result = groupplot.render({})
        assert "horizontal sep=2cm" in result
        assert "vertical sep=1.5cm" in result

    def test_groupplot_with_label_positions(self):
        """Test groupplot with custom label positions."""
        groupplot = GroupPlot(
            group_size="2 by 2",
            xlabels_at="edge bottom",
            ylabels_at="edge left",
            plots=[
                NextGroupPlot(xlabel="X", ylabel="Y", plots=[]),
                NextGroupPlot(plots=[]),
                NextGroupPlot(plots=[]),
                NextGroupPlot(plots=[]),
            ],
        )
        result = groupplot.render({})
        assert "xlabels at={edge bottom}" in result
        assert "ylabels at={edge left}" in result

    def test_nextgroupplot_with_options(self):
        """Test nextgroupplot with various options."""
        plot = NextGroupPlot(
            title="Test Plot",
            xlabel="X axis",
            ylabel="Y axis",
            xmin=0,
            xmax=10,
            ymin=0,
            ymax=5,
            grid=True,
            legend=["Series A"],
            plots=[AddPlot(coords=Coordinates([(0, 1), (5, 3), (10, 5)]))],
        )
        result = plot.render({})
        assert "\\nextgroupplot" in result
        assert "title={Test Plot}" in result
        assert "xlabel={X axis}" in result
        assert "ylabel={Y axis}" in result
        assert "xmin=0" in result
        assert "xmax=10" in result
        assert "ymin=0" in result
        assert "ymax=5" in result
        assert "grid=major" in result
        assert "\\legend{Series A}" in result

    def test_pgfplot_with_groupplot(self):
        """Test complete PGFPlot with groupplot."""
        plot = PGFPlot(
            GroupPlot(
                group_size="1 by 2",
                plots=[
                    NextGroupPlot(
                        title="Left",
                        plots=[AddPlot(coords=Coordinates([(0, 0), (1, 1)]))],
                    ),
                    NextGroupPlot(
                        title="Right",
                        plots=[AddPlot(coords=Coordinates([(0, 1), (1, 0)]))],
                    ),
                ],
            )
        )
        result = plot.render({})
        assert "\\begin{tikzpicture}" in result
        assert "\\begin{groupplot}" in result
        assert "\\nextgroupplot" in result
        assert "\\end{groupplot}" in result
        assert "\\end{tikzpicture}" in result

    def test_groupplot_dynamic_data(self):
        """Test groupplot with dynamic data from Ref and Iter."""
        groupplot = GroupPlot(
            group_size="1 by 2",
            plots=[
                NextGroupPlot(
                    title=Ref("title1"),
                    plots=[
                        AddPlot(
                            coords=Coordinates(
                                Iter(Ref("data1"), x=Ref("x"), y=Ref("y"))
                            )
                        )
                    ],
                ),
                NextGroupPlot(
                    title=Ref("title2"),
                    plots=[
                        AddPlot(
                            coords=Coordinates(
                                Iter(Ref("data2"), x=Ref("x"), y=Ref("y"))
                            )
                        )
                    ],
                ),
            ],
        )

        data = {
            "title1": "First Plot",
            "title2": "Second Plot",
            "data1": [{"x": 0, "y": 0}, {"x": 1, "y": 1}],
            "data2": [{"x": 0, "y": 1}, {"x": 1, "y": 0}],
        }

        result = groupplot.render(data)
        assert "title={First Plot}" in result
        assert "title={Second Plot}" in result
        assert "coordinates {(0, 0) (1, 1)}" in result
        assert "coordinates {(0, 1) (1, 0)}" in result

    def test_groupplot_with_preamble(self):
        """Test that groupplot includes the groupplots library in preamble."""
        plot = PGFPlot(
            GroupPlot(
                group_size="1 by 1",
                plots=[NextGroupPlot(plots=[])],
            )
        )
        result = plot.with_preamble()
        assert "\\usepgfplotslibrary{groupplots}" in result
        assert "\\documentclass{standalone}" in result
        assert "\\usepackage{pgfplots}" in result
