"""Error view keyboard handling module.

Handles keyboard input for the error view.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app_context import AppContext
    from platyplaty.ui.error_view import ErrorView

# Hard-coded navigation and exit keys (not configurable per spec)
_NAV_UP_KEYS = {"k", "up"}
_NAV_DOWN_KEYS = {"j", "down"}
_EXIT_KEY = "escape"


def handle_error_view_key(
    key: str,
    view: ErrorView,
    context: AppContext,
) -> bool:
    """Handle a key press in the error view.

    Args:
        key: The key that was pressed.
        view: The ErrorView widget.
        context: The application context.

    Returns:
        True if the key was handled, False otherwise.
    """
    if key == _EXIT_KEY:
        return _handle_exit(context)
    if key in _NAV_UP_KEYS:
        view.navigate_up()
        return True
    if key in _NAV_DOWN_KEYS:
        view.navigate_down()
        return True
    action = context.error_view_dispatch_table.get(key)
    if action == "clear_errors":
        return _handle_clear_errors(view, context)
    return False


def _handle_exit(context: AppContext) -> bool:
    """Handle exit from error view."""
    context.current_focus = "file_browser"
    return True


def _handle_clear_errors(view: ErrorView, context: AppContext) -> bool:
    """Handle clearing all errors."""
    context.error_log.clear()
    view.notify_errors_changed()
    return True
