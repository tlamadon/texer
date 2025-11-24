"""Tests for PGFPlots generation."""

import pytest
from texer import PGFPlot, Axis, AddPlot, Coordinates, Ref, Iter, evaluate


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
