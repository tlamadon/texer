"""Core spec system for texer - glom-style specs with type checking."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, Union

import glom  # type: ignore[import-untyped]

T = TypeVar("T")
U = TypeVar("U")


class Spec(ABC):
    """Base class for all specs. Specs are lazy evaluation descriptors."""

    @abstractmethod
    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        """Resolve this spec against the given data."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(...)"


@dataclass(frozen=True)
class Ref(Spec):
    """Reference to a data path using glom-style dot notation.

    Examples:
        `Ref("name")` -> `data["name"]`
        `Ref("user.email")` -> `data["user"]["email"]`
        `Ref("items.0.value")` -> `data["items"][0]["value"]`
    """

    path: str
    default: Any = field(default=None)

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        """Resolve the reference path against data."""
        # Check scope first for locally bound variables
        if scope and self.path in scope:
            return scope[self.path]

        # Use glom for path resolution
        try:
            return glom.glom(data, self.path)
        except glom.PathAccessError:
            if self.default is not None:
                return self.default
            raise

    def __repr__(self) -> str:
        if self.default is not None:
            return f'Ref("{self.path}", default={self.default!r})'
        return f'Ref("{self.path}")'

    # Comparison operators for Cond
    def __gt__(self, other: Any) -> Comparison:
        return Comparison(self, ">", other)

    def __lt__(self, other: Any) -> Comparison:
        return Comparison(self, "<", other)

    def __ge__(self, other: Any) -> Comparison:
        return Comparison(self, ">=", other)

    def __le__(self, other: Any) -> Comparison:
        return Comparison(self, "<=", other)

    def __eq__(self, other: Any) -> Comparison:  # type: ignore[override]
        return Comparison(self, "==", other)

    def __ne__(self, other: Any) -> Comparison:  # type: ignore[override]
        return Comparison(self, "!=", other)


@dataclass(frozen=True)
class Comparison(Spec):
    """A comparison expression for use in Cond."""

    left: Spec
    op: str
    right: Any

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> bool:
        """Evaluate the comparison."""
        left_val = resolve_value(self.left, data, scope)
        right_val = resolve_value(self.right, data, scope)

        ops: dict[str, Any] = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        return bool(ops[self.op](left_val, right_val))

    def __repr__(self) -> str:
        return f"({self.left!r} {self.op} {self.right!r})"

    def __and__(self, other: Comparison) -> And:
        return And(self, other)

    def __or__(self, other: Comparison) -> Or:
        return Or(self, other)


@dataclass(frozen=True)
class And(Spec):
    """Logical AND of two conditions."""

    left: Spec
    right: Spec

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> bool:
        return bool(resolve_value(self.left, data, scope)) and bool(
            resolve_value(self.right, data, scope)
        )


@dataclass(frozen=True)
class Or(Spec):
    """Logical OR of two conditions."""

    left: Spec
    right: Spec

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> bool:
        return bool(resolve_value(self.left, data, scope)) or bool(
            resolve_value(self.right, data, scope)
        )


@dataclass(frozen=True)
class Iter(Spec):
    """Iterate over a collection, applying a template to each item.

    Examples:
        Iter(Ref("items"), template=Row(Ref("name"), Ref("value")))
        Iter(Ref("points"), x=Ref("x"), y=Ref("y"))  # For coordinates
    """

    source: Spec | str
    template: Any = None
    separator: str = "\n"
    # For coordinate-style iteration
    x: Spec | None = None
    y: Spec | None = None
    z: Spec | None = None

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        """Resolve by iterating over source and applying template."""
        # Resolve the source collection
        if isinstance(self.source, str):
            items = glom.glom(data, self.source)
        else:
            items = self.source.resolve(data, scope)

        if not hasattr(items, "__iter__"):
            raise TypeError(f"Iter source must be iterable, got {type(items)}")

        results = []
        for item in items:
            # Create a new scope with the current item as the data context
            item_scope = dict(scope) if scope else {}
            # If item is a dict, add its keys to the scope for nested access
            if isinstance(item, dict):
                item_scope.update(item)

            if self.template is not None:
                # Template mode: resolve template against each item
                result = resolve_value(self.template, item, item_scope)
                results.append(result)
            elif self.x is not None:
                # Coordinate mode: extract x, y, z from each item
                x_val = resolve_value(self.x, item, item_scope)
                y_val = resolve_value(self.y, item, item_scope) if self.y else None
                z_val = resolve_value(self.z, item, item_scope) if self.z else None

                if z_val is not None:
                    results.append((x_val, y_val, z_val))
                elif y_val is not None:
                    results.append((x_val, y_val))
                else:
                    results.append(x_val)

        return results

    def __repr__(self) -> str:
        parts = [f"source={self.source!r}"]
        if self.template is not None:
            parts.append(f"template={self.template!r}")
        if self.x is not None:
            parts.append(f"x={self.x!r}")
        if self.y is not None:
            parts.append(f"y={self.y!r}")
        if self.z is not None:
            parts.append(f"z={self.z!r}")
        return f"Iter({', '.join(parts)})"


@dataclass(frozen=True)
class Format(Spec):
    """Format a value using Python format specification.

    Examples:
        Format(Ref("value"), ".2f")     -> f"{value:.2f}"
        Format(Ref("pct"), ".1%")       -> f"{pct:.1%}"
        Format(Ref("num"), "04d")       -> f"{num:04d}"
    """

    value: Spec | Any
    fmt: str

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        """Resolve and format the value."""
        val = resolve_value(self.value, data, scope)
        return format(val, self.fmt)

    def __repr__(self) -> str:
        return f'Format({self.value!r}, "{self.fmt}")'


@dataclass(frozen=True)
class Cond(Spec):
    """Conditional logic - returns one value or another based on condition.

    Examples:
        Cond(Ref("x") > 5, "red", "blue")
        Cond(Ref("active"), "\\checkmark", "")
    """

    condition: Spec | bool
    if_true: Any
    if_false: Any = ""

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        """Evaluate condition and return the selected branch (not resolved).

        Note: This returns the branch itself, not its resolved value.
        This allows Raw and other special specs to be handled properly
        by the evaluation layer.
        """
        cond_result = resolve_value(self.condition, data, scope)
        if cond_result:
            return self.if_true
        return self.if_false

    def __repr__(self) -> str:
        return f"Cond({self.condition!r}, {self.if_true!r}, {self.if_false!r})"


@dataclass(frozen=True)
class Literal(Spec):
    """A literal value that doesn't need resolution.

    Examples:
        Literal("some text")
        Literal(42)
    """

    value: Any

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        return self.value

    def __repr__(self) -> str:
        return f"Literal({self.value!r})"


@dataclass(frozen=True)
class Raw(Spec):
    r"""Raw LaTeX code that should not be escaped.

    Examples:
        Raw(r"\textbf{bold}")
        Raw(r"\hline")
    """

    latex: str

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        return self.latex

    def __repr__(self) -> str:
        return f"Raw({self.latex!r})"

    @property
    def is_raw(self) -> bool:
        return True


@dataclass(frozen=True)
class Call(Spec):
    """Call a function with resolved arguments.

    Examples:
        Call(len, Ref("items"))
        Call(max, Ref("values"))
    """

    func: Callable[..., Any]
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> Any:
        resolved_args = [resolve_value(arg, data, scope) for arg in self.args]
        resolved_kwargs = {
            k: resolve_value(v, data, scope) for k, v in self.kwargs.items()
        }
        return self.func(*resolved_args, **resolved_kwargs)

    def __repr__(self) -> str:
        return f"Call({self.func.__name__}, {self.args!r}, {self.kwargs!r})"


@dataclass(frozen=True)
class Join(Spec):
    """Join multiple specs with a separator.

    Examples:
        Join([Ref("first"), Ref("last")], " ")
    """

    parts: list[Any]
    separator: str = ""

    def resolve(self, data: Any, scope: dict[str, Any] | None = None) -> str:
        resolved = [str(resolve_value(p, data, scope)) for p in self.parts]
        return self.separator.join(resolved)


def resolve_value(value: Any, data: Any, scope: dict[str, Any] | None = None) -> Any:
    """Resolve a value which may be a Spec or a plain value."""
    if isinstance(value, Spec):
        return value.resolve(data, scope)
    return value
