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

    def test_coordinates_from_lists(self):
        """Test creating coordinates from separate x and y lists."""
        coords = Coordinates(x=[0, 1, 2], y=[1, 2, 4])
        result = coords.render({})
        assert result == "coordinates {(0, 1) (1, 2) (2, 4)}"

    def test_coordinates_from_lists_3d(self):
        """Test creating 3D coordinates from separate x, y, z lists."""
        coords = Coordinates(x=[0, 1], y=[0, 1], z=[1, 2])
        result = coords.render({})
        assert result == "coordinates {(0, 0, 1) (1, 1, 2)}"

    def test_coordinates_from_numpy_arrays(self):
        """Test creating coordinates from numpy arrays."""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("NumPy not installed")

        x = np.array([0, 1, 2])
        y = np.array([1, 2, 4])
        coords = Coordinates(x=x, y=y)
        result = coords.render({})
        assert result == "coordinates {(0, 1) (1, 2) (2, 4)}"

    def test_coordinates_from_numpy_arrays_3d(self):
        """Test creating 3D coordinates from numpy arrays."""
        try:
            import numpy as np
        except ImportError:
            pytest.skip("NumPy not installed")

        x = np.array([0.0, 1.0, 2.0])
        y = np.array([0.0, 1.0, 2.0])
        z = np.array([1.0, 2.0, 3.0])
        coords = Coordinates(x=x, y=y, z=z)
        result = coords.render({})
        # With default precision, trailing zeros are removed (e.g., 1.0 -> 1)
        assert result == "coordinates {(0, 0, 1) (1, 1, 2) (2, 2, 3)}"

    def test_coordinates_validation_no_args(self):
        """Test that Coordinates raises error if neither source nor x/y provided."""
        with pytest.raises(ValueError, match="Either 'source' or 'x' and 'y' must be provided"):
            Coordinates()

    def test_coordinates_validation_both_args(self):
        """Test that Coordinates raises error if both source and x/y provided."""
        with pytest.raises(ValueError, match="Cannot specify both 'source' and 'x'/'y' parameters"):
            Coordinates(source=[(0, 1)], x=[0], y=[1])

    def test_coordinates_validation_x_without_y(self):
        """Test that Coordinates raises error if x provided without y."""
        with pytest.raises(ValueError, match="If 'x' is provided, 'y' must also be provided"):
            Coordinates(x=[0, 1, 2])

    def test_coordinates_validation_mismatched_lengths(self):
        """Test that Coordinates raises error if x and y have different lengths."""
        coords = Coordinates(x=[0, 1, 2], y=[1, 2])
        with pytest.raises(ValueError, match="x and y must have the same length"):
            coords.render({})

    def test_coordinates_validation_mismatched_lengths_3d(self):
        """Test that Coordinates raises error if x, y, z have different lengths."""
        coords = Coordinates(x=[0, 1], y=[0, 1], z=[1])
        with pytest.raises(ValueError, match="x, y, and z must have the same length"):
            coords.render({})

    def test_coordinates_precision_default(self):
        """Test default precision (6 significant figures)."""
        coords = Coordinates(x=[0.123456789, 1.23456789], y=[0.987654321, 9.87654321])
        result = coords.render({})
        assert result == "coordinates {(0.123457, 0.987654) (1.23457, 9.87654)}"

    def test_coordinates_precision_custom(self):
        """Test custom precision (3 significant figures)."""
        coords = Coordinates(x=[0.123456789, 1.23456789], y=[0.987654321, 9.87654321], precision=3)
        result = coords.render({})
        assert result == "coordinates {(0.123, 0.988) (1.23, 9.88)}"

    def test_coordinates_precision_none(self):
        """Test no rounding when precision=None."""
        coords = Coordinates(x=[0.123456789, 1.23456789], y=[0.987654321, 9.87654321], precision=None)
        result = coords.render({})
        assert result == "coordinates {(0.123456789, 0.987654321) (1.23456789, 9.87654321)}"

    def test_coordinates_precision_with_tuples(self):
        """Test precision with tuple input."""
        coords = Coordinates([(0.123456789, 0.987654321), (1.23456789, 9.87654321)])
        result = coords.render({})
        assert result == "coordinates {(0.123457, 0.987654) (1.23457, 9.87654)}"

    def test_coordinates_precision_with_zeros(self):
        """Test precision with zero values."""
        coords = Coordinates(x=[0, 0.123456789, 0], y=[0, 0.987654321, 0])
        result = coords.render({})
        assert result == "coordinates {(0, 0) (0.123457, 0.987654) (0, 0)}"

    def test_coordinates_precision_scientific_notation(self):
        """Test precision with very small/large numbers."""
        coords = Coordinates(x=[1e-6, 1e6], y=[1e-7, 1e7], precision=3)
        result = coords.render({})
        assert result == "coordinates {(1e-06, 1e-07) (1e+06, 1e+07)}"


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

    def test_save_to_file(self):
        """Test saving LaTeX code to a file."""
        import tempfile
        import os

        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
            )
        )

        # Test with preamble (default)
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_plot.tex")
            plot.save_to_file(file_path)

            # Check file was created
            assert os.path.exists(file_path)

            # Check content includes preamble
            with open(file_path, "r") as f:
                content = f.read()
            assert "\\documentclass{standalone}" in content
            assert "\\begin{tikzpicture}" in content
            assert "coordinates {(0, 1) (1, 2)}" in content

        # Test without preamble
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_plot_no_preamble.tex")
            plot.save_to_file(file_path, with_preamble=False)

            with open(file_path, "r") as f:
                content = f.read()
            assert "\\documentclass{standalone}" not in content
            assert "\\begin{tikzpicture}" in content

        # Test with data and preamble
        plot_with_data = PGFPlot(
            Axis(
                xlabel=Ref("xlabel"),
                ylabel=Ref("ylabel"),
                plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
            )
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_plot_with_data.tex")
            data = {"xlabel": "Time", "ylabel": "Value"}
            plot_with_data.save_to_file(file_path, data=data, with_preamble=True)

            with open(file_path, "r") as f:
                content = f.read()
            assert "\\documentclass{standalone}" in content
            assert "xlabel=Time" in content
            assert "ylabel=Value" in content

    def test_spec_types_in_options(self):
        """Test that Ref and other Spec types work in AddPlot and Axis options."""
        plot = PGFPlot(
            Axis(
                xlabel=Ref("xlabel"),
                ylabel=Ref("ylabel"),
                xmin=Ref("xmin"),
                xmax=Ref("xmax"),
                legend_pos=Ref("legend_pos"),
                grid=Ref("grid"),
                plots=[
                    AddPlot(
                        color=Ref("color"),
                        mark=Ref("mark"),
                        style=Ref("style"),
                        coords=Coordinates([(0, 1), (1, 2)]),
                    )
                ],
            )
        )

        data = {
            "xlabel": "Time",
            "ylabel": "Value",
            "xmin": 0.0,
            "xmax": 2.0,
            "legend_pos": "north east",
            "grid": "major",
            "color": "blue",
            "mark": "*",
            "style": "dashed",
        }

        result = plot.render(data)

        # Check that values were resolved from data
        assert "xlabel=Time" in result
        assert "ylabel=Value" in result
        assert "xmin=0.0" in result
        assert "xmax=2.0" in result
        assert "legend pos={north east}" in result
        assert "grid=major" in result
        assert "color=blue" in result
        assert "mark=*" in result
        assert "dashed" in result


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

    def test_iter_for_multiple_plots(self):
        """Test using Iter to dynamically generate multiple plots from data."""
        plot = PGFPlot(
            Axis(
                xlabel=Ref("x_label"),
                ylabel=Ref("y_label"),
                legend_pos="north west",
                plots=Iter(
                    Ref("series"),
                    template=AddPlot(
                        color=Ref("color"),
                        mark=Ref("marker"),
                        coords=Coordinates(
                            Iter(Ref("data"), x=Ref("t"), y=Ref("value"))
                        ),
                    )
                ),
                legend=Iter(Ref("series"), template=Ref("name")),
            )
        )

        data = {
            "x_label": "Time (h)",
            "y_label": "Temperature (°C)",
            "series": [
                {
                    "name": "Sensor 1",
                    "color": "blue",
                    "marker": "*",
                    "data": [{"t": 0, "value": 20.5}, {"t": 1, "value": 22.3}],
                },
                {
                    "name": "Sensor 2",
                    "color": "red",
                    "marker": "square*",
                    "data": [{"t": 0, "value": 19.8}, {"t": 1, "value": 21.5}],
                },
            ],
        }

        result = plot.render(data)

        # Check that both series are present with correct colors and markers
        assert "color=blue" in result
        assert "mark=*" in result
        assert "color=red" in result
        assert "mark=square*" in result

        # Check that coordinates are correct
        assert "coordinates {(0, 20.5) (1, 22.3)}" in result
        assert "coordinates {(0, 19.8) (1, 21.5)}" in result

        # Check legend
        assert "\\legend{Sensor 1, Sensor 2}" in result

    def test_iter_with_root_level_refs(self):
        """Test that Iter can reference both local and root-level data."""
        plot = PGFPlot(
            Axis(
                xlabel=Ref("shared_xlabel"),  # From root
                ylabel=Ref("shared_ylabel"),  # From root
                title=Ref("title"),           # From root
                plots=Iter(
                    Ref("experiments"),
                    template=AddPlot(
                        color=Ref("color"),     # From current experiment
                        mark=Ref("marker"),     # From current experiment
                        coords=Coordinates(x=Ref("x"), y=Ref("y")),  # From current experiment
                    )
                ),
                legend=Iter(Ref("experiments"), template=Ref("name")),  # From each experiment
            )
        )

        data = {
            # Root-level shared configuration
            "title": "All Experiments",
            "shared_xlabel": "Time (s)",
            "shared_ylabel": "Value",

            # Per-experiment data
            "experiments": [
                {
                    "name": "Exp 1",
                    "color": "blue",
                    "marker": "*",
                    "x": [0, 1, 2],
                    "y": [1, 2, 4],
                },
                {
                    "name": "Exp 2",
                    "color": "red",
                    "marker": "square*",
                    "x": [0, 1, 2],
                    "y": [2, 3, 5],
                },
            ],
        }

        result = plot.render(data)

        # Check root-level references worked
        assert "xlabel={Time (s)}" in result
        assert "ylabel=Value" in result
        assert "title={All Experiments}" in result

        # Check local references worked
        assert "color=blue" in result
        assert "mark=*" in result
        assert "color=red" in result
        assert "mark=square*" in result

        # Check coordinates from local data
        assert "coordinates {(0, 1) (1, 2) (2, 4)}" in result
        assert "coordinates {(0, 2) (1, 3) (2, 5)}" in result

        # Check legend
        assert "\\legend{Exp 1, Exp 2}" in result


class TestCycleList:
    def test_cycle_list_name(self):
        """Test using a predefined cycle list name."""
        axis = Axis(
            cycle_list_name="color list",
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
        )
        result = axis.render({})
        assert "cycle list name={color list}" in result

    def test_cycle_list_with_dicts(self):
        """Test custom cycle list with dict entries."""
        axis = Axis(
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
                {"color": "green", "mark": "triangle*"},
            ],
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
        )
        result = axis.render({})
        assert "cycle list={" in result
        assert "color=blue" in result
        assert "mark=*" in result
        assert "color=red" in result
        assert "mark=square*" in result
        assert "color=green" in result
        assert "mark=triangle*" in result

    def test_cycle_list_with_strings(self):
        """Test custom cycle list with string entries."""
        axis = Axis(
            cycle_list=["blue", "red", "green"],
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
            ],
        )
        result = axis.render({})
        assert "cycle list={blue,red,green}" in result

    def test_cycle_list_with_ref(self):
        """Test cycle list with dynamic data from Ref."""
        axis = Axis(
            cycle_list=Ref("colors"),
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
            ],
        )
        data = {
            "colors": [
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
            ]
        }
        result = axis.render(data)
        assert "cycle list={" in result
        assert "color=blue" in result
        assert "mark=*" in result
        assert "color=red" in result
        assert "mark=square*" in result

    def test_cycle_list_name_with_ref(self):
        """Test cycle list name with dynamic data from Ref."""
        axis = Axis(
            cycle_list_name=Ref("cycle_name"),
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
            ],
        )
        data = {"cycle_name": "exotic"}
        result = axis.render(data)
        assert "cycle list name=exotic" in result

    def test_cycle_list_in_nextgroupplot(self):
        """Test cycle list in NextGroupPlot."""
        plot = NextGroupPlot(
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
            ],
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
        )
        result = plot.render({})
        assert "cycle list={" in result
        assert "color=blue" in result
        assert "mark=*" in result

    def test_cycle_list_in_groupplot(self):
        """Test cycle list applied to all subplots in GroupPlot."""
        groupplot = GroupPlot(
            group_size="1 by 2",
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
            ],
            plots=[
                NextGroupPlot(
                    plots=[
                        AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                        AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
                    ]
                ),
                NextGroupPlot(
                    plots=[
                        AddPlot(coords=Coordinates([(0, 3), (1, 4)])),
                    ]
                ),
            ],
        )
        result = groupplot.render({})
        assert "cycle list={" in result
        assert "color=blue" in result
        assert "mark=*" in result
        assert "color=red" in result
        assert "mark=square*" in result

    def test_cycle_list_name_priority(self):
        """Test that cycle_list_name takes priority over cycle_list."""
        axis = Axis(
            cycle_list_name="color list",
            cycle_list=["blue", "red"],  # Should be ignored
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
            ],
        )
        result = axis.render({})
        assert "cycle list name={color list}" in result
        assert "cycle list={blue,red}" not in result

    def test_complete_plot_with_cycle_list(self):
        """Test complete PGFPlot with cycle list."""
        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                cycle_list=[
                    {"color": "blue", "mark": "*", "line width": "2pt"},
                    {"color": "red", "mark": "square*", "line width": "2pt"},
                ],
                plots=[
                    AddPlot(coords=Coordinates([(0, 0), (1, 1)])),
                    AddPlot(coords=Coordinates([(0, 1), (1, 0)])),
                ],
            )
        )
        result = plot.render({})
        assert "\\begin{tikzpicture}" in result
        assert "\\begin{axis}" in result
        assert "cycle list={" in result
        assert "color=blue" in result
        assert "line width=2pt" in result
        assert "\\end{axis}" in result
        assert "\\end{tikzpicture}" in result

    def test_addplot_plus_with_cycle_list(self):
        """Test that AddPlot without style options generates \\addplot+ for cycle list usage."""
        axis = Axis(
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
            ],
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
        )
        result = axis.render({})
        # Should generate \addplot+ when no explicit styling is provided
        assert "\\addplot+" in result
        # Count occurrences - should have 2 \addplot+ commands
        assert result.count("\\addplot+") == 2

    def test_addplot_without_plus_when_styled(self):
        """Test that AddPlot with explicit styling generates \\addplot (not +)."""
        axis = Axis(
            cycle_list=[
                {"color": "blue", "mark": "*"},
                {"color": "red", "mark": "square*"},
            ],
            plots=[
                AddPlot(color="green", coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(mark="x", coords=Coordinates([(0, 2), (1, 3)])),
            ],
        )
        result = axis.render({})
        # Should generate \addplot when explicit styling is provided
        assert "\\addplot[" in result
        # Should NOT have \addplot+
        assert "\\addplot+" not in result


class TestLegendOptions:
    def test_legend_cell_align(self):
        """Test legend cell align option."""
        axis = Axis(
            legend_cell_align="left",
            plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
            legend=["Data"],
        )
        result = axis.render({})
        assert "legend cell align=left" in result

    def test_legend_columns(self):
        """Test legend columns option."""
        axis = Axis(
            legend_columns=3,
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
                AddPlot(coords=Coordinates([(0, 3), (1, 4)])),
            ],
            legend=["A", "B", "C"],
        )
        result = axis.render({})
        assert "legend columns=3" in result

    def test_transpose_legend(self):
        """Test transpose legend option."""
        axis = Axis(
            transpose_legend=True,
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
            legend=["Series 1", "Series 2"],
        )
        result = axis.render({})
        assert "transpose legend" in result

    def test_multiple_legend_options(self):
        """Test combining multiple legend options."""
        axis = Axis(
            legend_pos="north east",
            legend_cell_align="left",
            legend_columns=2,
            transpose_legend=True,
            plots=[
                AddPlot(coords=Coordinates([(0, 1), (1, 2)])),
                AddPlot(coords=Coordinates([(0, 2), (1, 3)])),
            ],
            legend=["Data 1", "Data 2"],
        )
        result = axis.render({})
        assert "legend pos={north east}" in result
        assert "legend cell align=left" in result
        assert "legend columns=2" in result
        assert "transpose legend" in result

    def test_legend_options_with_ref(self):
        """Test legend options with dynamic data from Ref."""
        axis = Axis(
            legend_cell_align=Ref("align"),
            legend_columns=Ref("cols"),
            plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
            legend=["Data"],
        )
        data = {"align": "center", "cols": 2}
        result = axis.render(data)
        assert "legend cell align=center" in result
        assert "legend columns=2" in result


class TestTitleStyle:
    def test_axis_title_style_static(self):
        """Test setting title style with a static string."""
        axis = Axis(
            title="My Plot",
            title_style="font=\\Large,text=blue",
            plots=[],
        )
        result = axis.render({})
        assert "title={My Plot}" in result
        assert "title style={font=\\Large,text=blue}" in result

    def test_axis_title_style_with_ref(self):
        """Test title style with dynamic data from Ref."""
        axis = Axis(
            title=Ref("plot_title"),
            title_style=Ref("title_styling"),
            plots=[],
        )
        data = {
            "plot_title": "Dynamic Title",
            "title_styling": "font=\\huge,color=red"
        }
        result = axis.render(data)
        assert "title={Dynamic Title}" in result
        assert "title style={font=\\huge,color=red}" in result

    def test_nextgroupplot_title_style(self):
        """Test title style in NextGroupPlot."""
        plot = NextGroupPlot(
            title="Subplot 1",
            title_style="font=\\small,align=center",
            plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
        )
        result = plot.render({})
        assert "title={Subplot 1}" in result
        assert "title style={font=\\small,align=center}" in result

    def test_groupplot_with_title_style(self):
        """Test GroupPlot with title style in subplots."""
        groupplot = GroupPlot(
            group_size="1 by 2",
            plots=[
                NextGroupPlot(
                    title="Left Plot",
                    title_style="font=\\Large",
                    plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2)]))],
                ),
                NextGroupPlot(
                    title="Right Plot",
                    title_style="font=\\normalsize,color=blue",
                    plots=[AddPlot(coords=Coordinates([(0, 2), (1, 3)]))],
                ),
            ],
        )
        result = groupplot.render({})
        assert "title={Left Plot}" in result
        assert "title style={font=\\Large}" in result
        assert "title={Right Plot}" in result
        assert "title style={font=\\normalsize,color=blue}" in result

    def test_complete_plot_with_title_style(self):
        """Test complete PGFPlot with title style."""
        plot = PGFPlot(
            Axis(
                title="Styled Title",
                title_style="font=\\huge,text=blue,align=center",
                xlabel="X",
                ylabel="Y",
                plots=[AddPlot(coords=Coordinates([(0, 0), (1, 1)]))],
            )
        )
        result = plot.render({})
        assert "\\begin{tikzpicture}" in result
        assert "title={Styled Title}" in result
        assert "title style={font=\\huge,text=blue,align=center}" in result
        assert "\\end{tikzpicture}" in result

    def test_title_without_style(self):
        """Test that title works without title_style (backward compatibility)."""
        axis = Axis(
            title="Simple Title",
            plots=[],
        )
        result = axis.render({})
        assert "title={Simple Title}" in result
        assert "title style" not in result


class TestTickOptions:
    def test_axis_xtick_list(self):
        """Test setting xtick as a list of values."""
        axis = Axis(
            xtick=[0, 1, 2, 3],
            plots=[],
        )
        result = axis.render({})
        assert "xtick={0,1,2,3}" in result

    def test_axis_ytick_list(self):
        """Test setting ytick as a list of values."""
        axis = Axis(
            ytick=[0, 0.5, 1, 1.5, 2],
            plots=[],
        )
        result = axis.render({})
        assert "ytick={0,0.5,1,1.5,2}" in result

    def test_axis_ztick_list(self):
        """Test setting ztick as a list of values."""
        axis = Axis(
            ztick=[10, 20, 30],
            plots=[],
        )
        result = axis.render({})
        assert "ztick={10,20,30}" in result

    def test_axis_tick_string(self):
        """Test setting tick as a string (e.g., 'data' or special values)."""
        axis = Axis(
            xtick="data",
            plots=[],
        )
        result = axis.render({})
        assert "xtick=data" in result

    def test_axis_xticklabels_list(self):
        """Test setting xticklabels as a list of strings."""
        axis = Axis(
            xtick=[0, 1, 2],
            xticklabels=["A", "B", "C"],
            plots=[],
        )
        result = axis.render({})
        assert "xtick={0,1,2}" in result
        assert "xticklabels={A,B,C}" in result

    def test_axis_yticklabels_list(self):
        """Test setting yticklabels as a list of strings."""
        axis = Axis(
            ytick=[0, 50, 100],
            yticklabels=["Low", "Medium", "High"],
            plots=[],
        )
        result = axis.render({})
        assert "ytick={0,50,100}" in result
        assert "yticklabels={Low,Medium,High}" in result

    def test_axis_ticklabels_string(self):
        """Test setting ticklabels as a string (special value)."""
        axis = Axis(
            xticklabels="\\empty",
            plots=[],
        )
        result = axis.render({})
        assert "xticklabels=\\empty" in result

    def test_axis_tick_with_ref(self):
        """Test tick positions with dynamic data from Ref."""
        axis = Axis(
            xtick=Ref("x_ticks"),
            xticklabels=Ref("x_labels"),
            plots=[],
        )
        data = {
            "x_ticks": [0, 1, 2],
            "x_labels": ["Jan", "Feb", "Mar"],
        }
        result = axis.render(data)
        assert "xtick={0,1,2}" in result
        assert "xticklabels={Jan,Feb,Mar}" in result

    def test_nextgroupplot_xtick(self):
        """Test tick positions in NextGroupPlot."""
        plot = NextGroupPlot(
            xtick=[0, 5, 10],
            xticklabels=["Start", "Mid", "End"],
            plots=[AddPlot(coords=Coordinates([(0, 0), (5, 5), (10, 10)]))],
        )
        result = plot.render({})
        assert "xtick={0,5,10}" in result
        assert "xticklabels={Start,Mid,End}" in result

    def test_nextgroupplot_ytick(self):
        """Test y-axis tick positions in NextGroupPlot."""
        plot = NextGroupPlot(
            ytick=[0, 25, 50, 75, 100],
            yticklabels=["0%", "25%", "50%", "75%", "100%"],
            plots=[],
        )
        result = plot.render({})
        assert "ytick={0,25,50,75,100}" in result
        assert "yticklabels={0%,25%,50%,75%,100%}" in result

    def test_complete_plot_with_ticks(self):
        """Test complete PGFPlot with tick customization."""
        plot = PGFPlot(
            Axis(
                xlabel="Month",
                ylabel="Value",
                xtick=[1, 2, 3, 4],
                xticklabels=["Q1", "Q2", "Q3", "Q4"],
                ytick=[0, 50, 100],
                yticklabels=["Low", "Mid", "High"],
                plots=[AddPlot(coords=Coordinates([(1, 25), (2, 50), (3, 75), (4, 100)]))],
            )
        )
        result = plot.render({})
        assert "\\begin{tikzpicture}" in result
        assert "xtick={1,2,3,4}" in result
        assert "xticklabels={Q1,Q2,Q3,Q4}" in result
        assert "ytick={0,50,100}" in result
        assert "yticklabels={Low,Mid,High}" in result
        assert "\\end{tikzpicture}" in result

    def test_groupplot_with_ticks(self):
        """Test GroupPlot with custom ticks in subplots."""
        groupplot = GroupPlot(
            group_size="1 by 2",
            plots=[
                NextGroupPlot(
                    xtick=[0, 1, 2],
                    xticklabels=["A", "B", "C"],
                    plots=[AddPlot(coords=Coordinates([(0, 1), (1, 2), (2, 3)]))],
                ),
                NextGroupPlot(
                    xtick=[0, 1, 2],
                    xticklabels=["X", "Y", "Z"],
                    plots=[AddPlot(coords=Coordinates([(0, 3), (1, 2), (2, 1)]))],
                ),
            ],
        )
        result = groupplot.render({})
        assert "xticklabels={A,B,C}" in result
        assert "xticklabels={X,Y,Z}" in result


class TestHexColors:
    """Tests for hex color conversion in PGFPlots."""

    def test_hex_color_with_hash(self):
        """Test hex color code with # prefix is converted to PGF RGB format."""
        plot = AddPlot(
            color="#5D8AA8",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color={rgb,255:red,93; green,138; blue,168}" in result

    def test_hex_color_without_hash(self):
        """Test hex color code without # prefix is also converted."""
        plot = AddPlot(
            color="FF0000",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color={rgb,255:red,255; green,0; blue,0}" in result

    def test_hex_color_green(self):
        """Test pure green hex color."""
        plot = AddPlot(
            color="#00FF00",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color={rgb,255:red,0; green,255; blue,0}" in result

    def test_hex_color_blue(self):
        """Test pure blue hex color."""
        plot = AddPlot(
            color="#0000FF",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color={rgb,255:red,0; green,0; blue,255}" in result

    def test_named_color_unchanged(self):
        """Test that named colors are not affected."""
        plot = AddPlot(
            color="blue",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color=blue" in result
        assert "rgb,255" not in result

    def test_hex_color_with_ref(self):
        """Test hex color with dynamic Ref."""
        plot = AddPlot(
            color=Ref("my_color"),
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        data = {"my_color": "#1E90FF"}  # DodgerBlue
        result = plot.render(data)
        assert "color={rgb,255:red,30; green,144; blue,255}" in result

    def test_hex_color_lowercase(self):
        """Test hex color with lowercase letters."""
        plot = AddPlot(
            color="#ff5733",
            coords=Coordinates([(0, 1), (1, 2)]),
        )
        result = plot.render({})
        assert "color={rgb,255:red,255; green,87; blue,51}" in result

    def test_hex_color_in_complete_plot(self):
        """Test hex color in a complete PGFPlot."""
        plot = PGFPlot(
            Axis(
                xlabel="X",
                ylabel="Y",
                plots=[
                    AddPlot(color="#5D8AA8", coords=Coordinates([(0, 1), (1, 2)])),
                ],
            )
        )
        result = plot.render({})
        assert "color={rgb,255:red,93; green,138; blue,168}" in result
