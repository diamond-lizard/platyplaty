#!/usr/bin/env python3
"""Shared utilities for focus management."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


def return_focus_to_widget(app: "App[object]", widget_id: str | None) -> None:
    """Return focus to a widget by ID.

    Args:
        app: The Textual app instance.
        widget_id: The ID of the widget to focus, or None.
    """
    if not widget_id:
        return
    try:
        widget = app.query_one(f"#{widget_id}")
        widget.focus()
    except Exception:
        pass
