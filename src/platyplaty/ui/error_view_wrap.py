"""Error view line wrapping module.

Wraps error messages to fit terminal width.
"""


def wrap_error_lines(error_log: list[str], width: int) -> list[str]:
    """Wrap error messages to fit the given width.

    Args:
        error_log: List of error messages.
        width: Maximum line width.

    Returns:
        List of wrapped lines.
    """
    if width <= 0:
        return []
    wrapped: list[str] = []
    for message in error_log:
        wrapped.extend(_wrap_single_message(message, width))
    return wrapped


def _wrap_single_message(message: str, width: int) -> list[str]:
    """Wrap a single error message to fit width.

    Args:
        message: The error message to wrap.
        width: Maximum line width.

    Returns:
        List of wrapped lines for this message.
    """
    if not message:
        return [""]
    lines: list[str] = []
    remaining = message
    while remaining:
        if len(remaining) <= width:
            lines.append(remaining)
            break
        lines.append(remaining[:width])
        remaining = remaining[width:]
    return lines
