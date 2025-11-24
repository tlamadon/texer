"""Evaluation engine for texer specs and LaTeX elements."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from texer.specs import Spec, resolve_value, Raw
from texer.utils import escape_latex


@runtime_checkable
class Renderable(Protocol):
    """Protocol for objects that can render to LaTeX."""

    def render(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Render this object to LaTeX string."""
        ...


def evaluate(
    element: Any,
    data: Any | None = None,
    scope: dict[str, Any] | None = None,
    escape: bool = True,
) -> str:
    """Evaluate an element and return LaTeX string.

    This is the main entry point for converting texer elements to LaTeX.

    Args:
        element: The element to evaluate (Spec, Renderable, or plain value).
        data: The data context for resolving specs.
        scope: Additional scope variables.
        escape: Whether to escape LaTeX special characters in strings.

    Returns:
        LaTeX string representation.

    Examples:
        >>> from texer import Ref, Table, Tabular, Row
        >>> data = {"name": "Alice", "value": 42}
        >>> evaluate(Ref("name"), data)
        'Alice'
    """
    if data is None:
        data = {}

    if scope is None:
        scope = {}

    return _evaluate_impl(element, data, scope, escape)


def _evaluate_impl(
    element: Any,
    data: Any,
    scope: dict[str, Any],
    escape: bool,
) -> str:
    """Internal implementation of evaluate."""
    # Handle None
    if element is None:
        return ""

    # Handle Raw specs (don't escape)
    if isinstance(element, Raw):
        return element.resolve(data, scope)

    # Handle Specs
    if isinstance(element, Spec):
        resolved = element.resolve(data, scope)
        return _evaluate_impl(resolved, data, scope, escape)

    # Handle Renderables (Table, Tabular, Row, etc.)
    if isinstance(element, Renderable):
        return element.render(data, scope)

    # Handle lists/tuples
    if isinstance(element, (list, tuple)):
        return "".join(_evaluate_impl(item, data, scope, escape) for item in element)

    # Handle plain values
    result = str(element)
    if escape:
        return escape_latex(result)
    return result


def evaluate_value(
    value: Any,
    data: Any,
    scope: dict[str, Any] | None = None,
) -> Any:
    """Evaluate a value without converting to string.

    This resolves Specs but doesn't convert to LaTeX string.
    Useful for getting raw values (lists, numbers, etc.)

    Args:
        value: The value to evaluate.
        data: The data context.
        scope: Additional scope variables.

    Returns:
        The resolved value (may be any type).
    """
    if scope is None:
        scope = {}

    return resolve_value(value, data, scope)
