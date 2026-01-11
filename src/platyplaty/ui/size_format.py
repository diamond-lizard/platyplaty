"""File size formatting functions.

This module provides functions to format file sizes for display
using base-2 units (B, K, M, G, T).
"""


def format_file_size(size_bytes: int) -> str:
    """Format file size for display.

    Uses base-2 units (1 K = 1024 bytes).

    Args:
        size_bytes: File size in bytes.

    Returns:
        Formatted size string (e.g., "512 B", "1.5 K", "2 M").
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    return _format_with_unit(size_bytes)


def _format_with_unit(size_bytes: int) -> str:
    """Format size >= 1024 bytes with appropriate unit."""
    units = [("K", 1024), ("M", 1024**2), ("G", 1024**3), ("T", 1024**4)]
    for unit, threshold in reversed(units):
        if size_bytes >= threshold:
            value = size_bytes / threshold
            return _format_value_with_unit(value, unit)
    return f"{size_bytes} B"


def _format_value_with_unit(value: float, unit: str) -> str:
    """Format a value with its unit, removing trailing zeros."""
    formatted = f"{value:.2f}"
    # Remove trailing zeros and decimal point if not needed
    formatted = formatted.rstrip("0").rstrip(".")
    return f"{formatted} {unit}"
