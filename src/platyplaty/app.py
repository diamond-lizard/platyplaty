#!/usr/bin/env python3
"""Textual application for Platyplaty visualizer control."""

from textual.app import App


class PlatyplatyApp(App):
    """Textual application for controlling the Platyplaty visualizer.

    This app manages the renderer process, handles keyboard input from both
    the terminal and the renderer window, and coordinates auto-advance and
    other background tasks.

    Attributes:
        renderer_dispatch_table: Maps renderer window keys to action names.
        client_dispatch_table: Maps terminal keys to action names.
        _renderer_ready: True after INIT command succeeds.
    """

    renderer_dispatch_table: dict[str, str]
    client_dispatch_table: dict[str, str]
    _renderer_ready: bool
