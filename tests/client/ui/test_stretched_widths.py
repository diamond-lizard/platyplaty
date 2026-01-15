"""Tests for calculate_stretched_widths function.

Tests that pane widths are correctly calculated for the stretched
layout state where the right pane is collapsed.
"""

import pytest

from platyplaty.ui.layout import PaneWidths
from platyplaty.ui.layout_stretched import calculate_stretched_widths


def test_stretched_widths_80_chars() -> None:
    """Test stretched width calculation at 80 character width."""
    result = calculate_stretched_widths(80)
    # left_raw = int(80 * 0.125) = 10
    # middle_raw = int(80 * 0.775) = 62
    # left_content = 10 - 1 = 9
    # middle_content = 62 - 1 = 61
    # right = 80 - 10 - 62 = 8 (remainder rule)
    assert result.left == 9
    assert result.middle == 61
    assert result.right == 8


def test_stretched_widths_100_chars() -> None:
    """Test stretched width calculation at 100 character width."""
    result = calculate_stretched_widths(100)
    # left_raw = int(100 * 0.125) = 12
    # middle_raw = int(100 * 0.775) = 77
    # left_content = 12 - 1 = 11
    # middle_content = 77 - 1 = 76
    # right = 100 - 12 - 77 = 11 (remainder rule)
    assert result.left == 11
    assert result.middle == 76
    assert result.right == 11


def test_stretched_widths_fills_terminal() -> None:
    """Verify that stretched layout fills terminal width exactly."""
    for width in [40, 60, 80, 100, 120, 160, 200]:
        result = calculate_stretched_widths(width)
        # left_content + gap + middle_content + gap + right = terminal
        total = result.left + 1 + result.middle + 1 + result.right
        assert total == width, f"Width {width}: {total} != {width}"


def test_stretched_widths_zero() -> None:
    """Test that zero terminal width returns all zeros."""
    result = calculate_stretched_widths(0)
    assert result == PaneWidths(left=0, middle=0, right=0)


def test_stretched_widths_negative() -> None:
    """Test that negative terminal width returns all zeros."""
    result = calculate_stretched_widths(-10)
    assert result == PaneWidths(left=0, middle=0, right=0)


def test_stretched_widths_minimum_enforcement() -> None:
    """Test minimum width enforcement for very narrow terminal."""
    # At width 8: left_raw = 1, middle_raw = 6
    # left_content = 0 -> enforced to 1
    # middle_content = 5
    # right = 8 - 1 - 6 = 1
    result = calculate_stretched_widths(8)
    assert result.left >= 1
    assert result.middle >= 1


def test_stretched_middle_larger_than_standard() -> None:
    """Verify stretched middle pane is larger than standard layout."""
    from platyplaty.ui.layout import calculate_pane_widths
    for width in [80, 100, 120]:
        standard = calculate_pane_widths(width)
        stretched = calculate_stretched_widths(width)
        assert stretched.middle > standard.middle
