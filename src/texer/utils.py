"""Utility functions for LaTeX generation."""

from __future__ import annotations

import re
from typing import Any


# Regex pattern for hex color codes (with or without #)
HEX_COLOR_PATTERN = re.compile(r"^#?([0-9A-Fa-f]{6})$")


def hex_to_pgf_rgb(color: str) -> str:
    """Convert a hex color code to PGF/TikZ RGB format.

    Args:
        color: A hex color code like "#5D8AA8" or "5D8AA8".

    Returns:
        The color in PGF format: "{rgb,255:red,93; green,138; blue,168}"

    Raises:
        ValueError: If the color is not a valid 6-character hex code.

    Examples:
        >>> hex_to_pgf_rgb("#5D8AA8")
        '{rgb,255:red,93; green,138; blue,168}'
        >>> hex_to_pgf_rgb("#FF0000")
        '{rgb,255:red,255; green,0; blue,0}'
        >>> hex_to_pgf_rgb("00FF00")
        '{rgb,255:red,0; green,255; blue,0}'
    """
    match = HEX_COLOR_PATTERN.match(color)
    if not match:
        raise ValueError(
            f"Invalid hex color code: {color!r}. "
            "Expected format: '#RRGGBB' or 'RRGGBB'"
        )

    hex_str = match.group(1)
    red = int(hex_str[0:2], 16)
    green = int(hex_str[2:4], 16)
    blue = int(hex_str[4:6], 16)

    return f"{{rgb,255:red,{red}; green,{green}; blue,{blue}}}"


def is_hex_color(color: str) -> bool:
    """Check if a string is a valid hex color code.

    Args:
        color: A string to check.

    Returns:
        True if the string is a valid hex color code (with or without #).

    Examples:
        >>> is_hex_color("#5D8AA8")
        True
        >>> is_hex_color("FF0000")
        True
        >>> is_hex_color("blue")
        False
        >>> is_hex_color("#GGG")
        False
    """
    return HEX_COLOR_PATTERN.match(color) is not None

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


def _single_cmidrule(
    start: int,
    end: int,
    trim_left: str | bool = False,
    trim_right: str | bool = False,
) -> str:
    """Generate a single \\cmidrule command."""
    trim = ""
    if trim_left or trim_right:
        left_part = ""
        right_part = ""
        if trim_left is True:
            left_part = "l"
        elif trim_left:
            left_part = f"l{{{trim_left}}}"
        if trim_right is True:
            right_part = "r"
        elif trim_right:
            right_part = f"r{{{trim_right}}}"
        trim = f"({left_part}{right_part})"

    return f"\\cmidrule{trim}{{{start}-{end}}}"


def cmidrule(
    start: int | list[tuple[int, int]],
    end: int | None = None,
    trim_left: str | bool = False,
    trim_right: str | bool = False,
    trim_between: bool = False,
) -> str:
    """Generate \\cmidrule command(s) from the booktabs package.

    Can generate a single cmidrule or multiple cmidrules from a list of ranges.

    Args:
        start: Either:
            - Starting column number (1-indexed) for a single rule, OR
            - List of (start, end) tuples for multiple rules
        end: Ending column number (1-indexed). Required if start is an int.
        trim_left: Left trim specification. Can be:
            - False: no left trim
            - True: default left trim ("l")
            - str: custom trim width (e.g., "0.5em")
        trim_right: Right trim specification. Can be:
            - False: no right trim
            - True: default right trim ("r")
            - str: custom trim width (e.g., "0.5em")
        trim_between: If True and multiple ranges given, automatically add
            trim_right to all but the last rule and trim_left to all but
            the first rule, creating gaps between adjacent rules.

    Returns:
        The \\cmidrule command string(s), space-separated if multiple.

    Examples:
        >>> cmidrule(1, 3)
        '\\\\cmidrule{1-3}'
        >>> cmidrule(2, 4, trim_left=True, trim_right=True)
        '\\\\cmidrule(lr){2-4}'
        >>> cmidrule([(2, 4), (5, 7)])
        '\\\\cmidrule{2-4} \\\\cmidrule{5-7}'
        >>> cmidrule([(2, 4), (5, 7)], trim_between=True)
        '\\\\cmidrule(r){2-4} \\\\cmidrule(l){5-7}'
        >>> cmidrule([(1, 2), (3, 4), (5, 6)], trim_between=True)
        '\\\\cmidrule(r){1-2} \\\\cmidrule(lr){3-4} \\\\cmidrule(l){5-6}'
    """
    # Handle list of ranges
    if isinstance(start, list):
        ranges = start
        if not ranges:
            return ""

        results = []
        for i, (s, e) in enumerate(ranges):
            # Determine trim for this rule
            left = trim_left
            right = trim_right

            if trim_between and len(ranges) > 1:
                # First rule: no left trim (unless specified), add right trim
                # Middle rules: add both trims
                # Last rule: add left trim, no right trim (unless specified)
                if i == 0:
                    right = right or True
                elif i == len(ranges) - 1:
                    left = left or True
                else:
                    left = left or True
                    right = right or True

            results.append(_single_cmidrule(s, e, left, right))

        return " ".join(results)

    # Single range (original API)
    if end is None:
        raise ValueError("end is required when start is an integer")

    return _single_cmidrule(start, end, trim_left, trim_right)
