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

    # Handle left pane disappearance (same rule as standard layout)
    if left_raw == 0:
        # Left pane disappears; use stretched ratio for middle only
        # Middle gets 0.775 fraction, right gets remainder
        middle_raw = int(terminal_width * 0.775)
        middle_content = max(1, middle_raw - 1)
        right_width = terminal_width - middle_content - 1  # -1 for gap
        return PaneWidths(left=0, middle=middle_content, right=right_width)

    # Normal case: all three panes visible
    middle_raw = int(terminal_width * 0.775)

    # Subtract 1 for gap from each
    left_content = left_raw - 1
    middle_content = middle_raw - 1

    # Enforce minimum widths (1 character each)
    left_content = max(1, left_content)
    middle_content = max(1, middle_content)

    # Right pane width via remainder rule (after minimum enforcement)
    # Account for gaps (1 char after left, 1 char after middle)
    right_width = terminal_width - left_content - middle_content - 2

    return PaneWidths(left=left_content, middle=middle_content, right=right_width)
