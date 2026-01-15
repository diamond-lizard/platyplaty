"""Layout calculation for the three-pane file browser.

This module calculates pane widths based on terminal width using
a 1:3:4 ratio (sum = 8). Each pane width is computed with integer
truncation, and 1-character gaps are subtracted from left and middle
panes. The right pane absorbs remaining space.
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class PaneWidths:
    """Container for calculated pane widths.

    All widths are in characters and represent content width
    (gaps already subtracted from left and middle panes).

    Attributes:
        left: Width of left pane (0 means pane is hidden).
        middle: Width of middle pane.
        right: Width of right pane (absorbs remaining space).
    """

    left: int
    middle: int
    right: int

def calculate_pane_widths(terminal_width: int) -> PaneWidths:
    """Calculate pane widths from terminal width using 1:3:4 ratio.

    The algorithm:
    1. If int(width * 1/8) = 0, left pane disappears entirely
    2. Otherwise, apply 1:3:4 ratio with integer truncation
    3. Subtract 1 from left and middle panes for gap
    4. Enforce minimum content width of 1 for left and middle panes
    5. Right pane receives all remaining horizontal space

    Args:
        terminal_width: Total terminal width in characters.

    Returns:
        PaneWidths with calculated widths for each pane.
    """
    if terminal_width <= 0:
        return PaneWidths(left=0, middle=0, right=0)

    # Check if left pane should disappear (TASK-0600)
    left_raw = int(terminal_width * 1 / 8)

    if left_raw == 0:
        # Left pane disappears; split remaining between middle and right
        # Use 3:4 ratio for middle and right
        middle_raw = int(terminal_width * 3 / 7)
        middle_width = max(1, middle_raw - 1)  # Subtract gap
        right_width = terminal_width - middle_width - 1  # -1 for gap
        return PaneWidths(left=0, middle=middle_width, right=right_width)

    # Normal case: all three panes visible
    # TASK-0200: Apply 1:3:4 ratio with integer truncation
    middle_raw = int(terminal_width * 3 / 8)

    # TASK-0300: Subtract 1 from left and middle for gap
    left_width = left_raw - 1
    middle_width = middle_raw - 1

    # TASK-0400: Enforce minimum content width of 1
    left_width = max(1, left_width)
    middle_width = max(1, middle_width)

    # TASK-0500: Right pane receives all remaining space
    # Account for gaps (1 char after left, 1 char after middle)
    right_width = terminal_width - left_width - middle_width - 2

    return PaneWidths(left=left_width, middle=middle_width, right=right_width)


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

    # TASK-2200: Calculate left_raw using 0.125 fraction
    left_raw = int(terminal_width * 0.125)

    # TASK-2300: Calculate middle_raw using 0.775 fraction
    middle_raw = int(terminal_width * 0.775)

    # TASK-2400 & TASK-2500: Subtract 1 for gap from each
    left_content = left_raw - 1
    middle_content = middle_raw - 1

    # TASK-2700: Enforce minimum widths (1 character each)
    left_content = max(1, left_content)
    middle_content = max(1, middle_content)

    # TASK-2600: Right pane width via remainder rule
    # This absorbs rounding to fill terminal exactly
    right_width = terminal_width - left_raw - middle_raw

    return PaneWidths(left=left_content, middle=middle_content, right=right_width)
