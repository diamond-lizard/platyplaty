"""Stretched layout calculation for the file browser.

This module calculates pane widths for the stretched layout state
where the right pane is collapsed. Uses fractions: left=0.125,
middle=0.775, with the right pane receiving the remainder (~10%)
via the remainder rule.
"""

from platyplaty.ui.layout import PaneWidths


def calculate_stretched_widths(terminal_width: int) -> PaneWidths:
    """Calculate pane widths for stretched layout (right pane collapsed).

    The stretched layout uses fractions: left=0.125, middle=0.775.
    The right pane receives the remainder (~10%) via the remainder rule,
    ensuring the layout always fills the terminal exactly.

    Args:
        terminal_width: Total terminal width in characters.

    Returns:
        PaneWidths with calculated widths for each pane.
    """
    if terminal_width <= 0:
        return PaneWidths(left=0, middle=0, right=0)

    # Calculate left_raw using 0.125 fraction
    left_raw = int(terminal_width * 0.125)

    # Calculate middle_raw using 0.775 fraction
    middle_raw = int(terminal_width * 0.775)

    # Subtract 1 for gap from each
    left_content = left_raw - 1
    middle_content = middle_raw - 1

    # Enforce minimum widths (1 character each)
    left_content = max(1, left_content)
    middle_content = max(1, middle_content)

    # Right pane width via remainder rule
    # This absorbs rounding to fill terminal exactly
    right_width = terminal_width - left_raw - middle_raw

    return PaneWidths(left=left_content, middle=middle_content, right=right_width)
