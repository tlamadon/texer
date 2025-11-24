"""Texer: Generate LaTeX tables and figures with glom-style specs."""

from texer.specs import Ref, Iter, Format, Cond, Literal, Raw, Spec
from texer.tables import Table, Tabular, Row, Cell, MultiColumn, MultiRow
from texer.pgfplots import PGFPlot, Axis, AddPlot, Coordinates, Legend
from texer.eval import evaluate

__version__ = "0.1.0"

__all__ = [
    # Specs
    "Ref",
    "Iter",
    "Format",
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
    # PGFPlots
    "PGFPlot",
    "Axis",
    "AddPlot",
    "Coordinates",
    "Legend",
    # Evaluation
    "evaluate",
]
