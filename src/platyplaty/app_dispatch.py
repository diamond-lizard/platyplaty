"""Dispatch table building for PlatyplatyApp."""

from typing import TYPE_CHECKING

from platyplaty.dispatch_tables import (
    build_client_dispatch_table,
    build_file_browser_dispatch_table,
)

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


def build_app_dispatch_tables(app: "PlatyplatyApp") -> None:
    """Build dispatch tables for the application.

    Creates the file browser and client dispatch tables from keybindings.
    Called during __init__ to make tables available for compose().

    Args:
        app: The PlatyplatyApp instance.
    """
    # Build file browser dispatch table (available in compose)
    app.file_browser_dispatch_table = build_file_browser_dispatch_table(
        nav_up_keys=app._file_browser_keybindings.nav_up,
        nav_down_keys=app._file_browser_keybindings.nav_down,
        nav_left_keys=app._file_browser_keybindings.nav_left,
        nav_right_keys=app._file_browser_keybindings.nav_right,
    )

    # Build client dispatch table for app-level actions
    app.client_dispatch_table = build_client_dispatch_table(
        quit_key=app._client_keybindings.quit,
    )
    app.client_dispatch_table["ctrl+c"] = "quit"
