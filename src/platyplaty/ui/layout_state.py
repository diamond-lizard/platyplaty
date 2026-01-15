"""Layout state determination for the file browser.

This module provides the LayoutState enum and the get_layout_state
function that determines whether the layout should be standard
(1:3:4 ratio) or stretched (right pane collapsed).
"""

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.ui.file_browser_types import RightPaneContent


class LayoutState(Enum):
    """Layout states for the file browser panes."""

    STANDARD = auto()
    STRETCHED = auto()


def get_layout_state(content: "RightPaneContent") -> LayoutState:
    """Determine layout state based on right pane content.

    Args:
        content: The right pane content, or None if collapsed.

    Returns:
        STANDARD if content should be displayed.
        STRETCHED if right pane should collapse.
    """
    if content is None:
        return LayoutState.STRETCHED
    return LayoutState.STANDARD
