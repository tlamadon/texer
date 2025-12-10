"""Texer: Generate LaTeX tables and figures with glom-style specs."""

from texer.specs import Ref, Iter, Format, FormatNumber, Cond, Literal, Raw, Spec
from texer.tables import Table, Tabular, Row, Cell, MultiColumn, MultiRow
from texer.pgfplots import PGFPlot, Axis, AddPlot, Coordinates, Legend, GroupPlot, NextGroupPlot, scatter_plot
from texer.eval import evaluate
from texer.utils import cmidrule

__version__ = "0.2.0"

__all__ = [
    # Specs
    "Ref",
    "Iter",
    "Format",
    "FormatNumber",
    "Cond",
    "Literal",
    "Raw",
    "Spec",
    # Tables
    "Table",
    "Tabular",
    "Row",
    "Cell",
    "MultiColumn",
    "MultiRow",
    "cmidrule",
    # PGFPlots
    "PGFPlot",
    "Axis",
    "AddPlot",
    "Coordinates",
    "Legend",
    "GroupPlot",
    "NextGroupPlot",
    "scatter_plot",
    # Evaluation
    "evaluate",
]
