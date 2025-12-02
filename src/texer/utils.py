"""Utility functions for LaTeX generation."""

from __future__ import annotations

import re
from typing import Any

# Characters that need escaping in LaTeX
LATEX_SPECIAL_CHARS = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}

# Regex pattern for special characters
LATEX_ESCAPE_PATTERN = re.compile(
    "|".join(re.escape(char) for char in LATEX_SPECIAL_CHARS.keys())
)


def escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text.

    Args:
        text: The text to escape.

    Returns:
        The escaped text safe for LaTeX.

    Examples:
        >>> escape_latex("10% off")
        '10\\% off'
        >>> escape_latex("$100")
        '\\$100'
    """
    return LATEX_ESCAPE_PATTERN.sub(
        lambda m: LATEX_SPECIAL_CHARS[m.group()], text
    )


def format_option_value(value: Any) -> str:
    """Format a Python value for use in LaTeX options.

    Args:
        value: The value to format.

    Returns:
        LaTeX-formatted string.

    Examples:
        >>> format_option_value("north west")
        '{north west}'
        >>> format_option_value(True)
        'true'
        >>> format_option_value(3.14)
        '3.14'
    """
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    # Strings get wrapped in braces if they contain spaces or special chars
    s = str(value)
    # Don't double-wrap if already wrapped in braces
    if s.startswith("{") and s.endswith("}"):
        return s
    if " " in s or any(c in s for c in ",=[]"):
        return f"{{{s}}}"
    return s


def format_options(options: dict[str, Any], raw_options: str | None = None) -> str:
    """Format a dictionary of options for LaTeX.

    Args:
        options: Dictionary of option key-value pairs.
        raw_options: Raw LaTeX options string to append.

    Returns:
        Formatted options string (without surrounding brackets).

    Examples:
        >>> format_options({"xlabel": "Time", "ylabel": "Value"})
        'xlabel={Time}, ylabel={Value}'
    """
    parts = []
    for key, value in options.items():
        if value is None:
            continue
        if value is True:
            # Boolean true options are just the key
            parts.append(key)
        elif value is False:
            continue  # Skip false options
        else:
            formatted = format_option_value(value)
            # Convert Python-style names to LaTeX style (legend_pos -> legend pos)
            latex_key = key.replace("_", " ")
            parts.append(f"{latex_key}={formatted}")

    if raw_options:
        parts.append(raw_options)

    return ", ".join(parts)


def indent(text: str, spaces: int = 2) -> str:
    """Indent each line of text.

    Args:
        text: The text to indent.
        spaces: Number of spaces to indent.

    Returns:
        Indented text.
    """
    prefix = " " * spaces
    return "\n".join(prefix + line if line else line for line in text.split("\n"))


def wrap_environment(name: str, content: str, options: str = "") -> str:
    """Wrap content in a LaTeX environment.

    Args:
        name: Environment name.
        content: Content to wrap.
        options: Optional options string.

    Returns:
        Complete environment string.
    """
    if options:
        begin = f"\\begin{{{name}}}[{options}]"
    else:
        begin = f"\\begin{{{name}}}"
    end = f"\\end{{{name}}}"
    return f"{begin}\n{indent(content)}\n{end}"
