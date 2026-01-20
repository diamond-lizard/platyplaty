#!/usr/bin/env python3
"""
Unit tests for dispatch table building.

Tests construction of key-to-action dispatch tables for renderer and client.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.dispatch_tables import (
    build_client_dispatch_table,
    build_renderer_dispatch_table,
)
from platyplaty.dispatch_tables_ui import (
    build_error_view_dispatch_table,
    build_file_browser_dispatch_table,
    build_global_dispatch_table,
    build_playlist_dispatch_table,
)


class TestDispatchTableBuilding:
    """Tests for dispatch table construction."""

    def test_build_renderer_dispatch_table_maps_all_keys(self) -> None:
        """Renderer dispatch table maps all three action keys to action names."""
        table = build_renderer_dispatch_table("right", "left", "q")
        assert table["right"] == "next_preset"
        assert table["left"] == "previous_preset"
        assert table["q"] == "quit"

    def test_build_renderer_dispatch_table_with_custom_keys(self) -> None:
        """Renderer dispatch table works with custom key assignments."""
        table = build_renderer_dispatch_table("n", "p", "escape")
        assert table["n"] == "next_preset"
        assert table["p"] == "previous_preset"
        assert table["escape"] == "quit"

    def test_build_client_dispatch_table_with_quit(self) -> None:
        """Client dispatch table includes quit when specified."""
        table = build_client_dispatch_table("ctrl+q")
        assert table["ctrl+q"] == "quit"

    def test_build_client_dispatch_table_without_quit(self) -> None:
        """Client dispatch table is empty when quit is None."""
        table = build_client_dispatch_table(None)
        assert len(table) == 0

    def test_build_global_dispatch_table_maps_all_keys(self) -> None:
        """Global dispatch table maps all action keys."""
        table = build_global_dispatch_table(
            switch_focus_keys=["tab"],
            quit_keys=["q"],
            navigate_up_keys=["k", "up"],
            navigate_down_keys=["j", "down"],
            open_selected_keys=["l", "right"],
            view_errors_keys=["e"],
            play_selection_keys=["enter"],
        )
        assert table["tab"] == "switch_focus"
        assert table["q"] == "quit"
        assert table["k"] == "navigate_up"
        assert table["up"] == "navigate_up"
        assert table["j"] == "navigate_down"
        assert table["down"] == "navigate_down"
        assert table["l"] == "open_selected"
        assert table["e"] == "view_errors"
        assert table["enter"] == "play_selection"

    def test_build_playlist_dispatch_table_maps_all_keys(self) -> None:
        """Playlist dispatch table maps all action keys."""
        table = build_playlist_dispatch_table(
            play_previous_keys=["K"],
            play_next_keys=["J"],
            reorder_up_keys=["ctrl+k"],
            reorder_down_keys=["ctrl+j"],
            delete_keys=["D", "delete"],
            undo_keys=["u"],
            redo_keys=["ctrl+r"],
            save_keys=["ctrl+s"],
            shuffle_keys=["s"],
            toggle_autoplay_keys=["space"],
            page_up_keys=["pageup"],
            page_down_keys=["pagedown"],
            navigate_to_first_keys=["home"],
            navigate_to_last_keys=["end"],
        )
        assert table["K"] == "play_previous"
        assert table["J"] == "play_next"
        assert table["ctrl+k"] == "reorder_up"
        assert table["ctrl+j"] == "reorder_down"
        assert table["D"] == "delete_from_playlist"
        assert table["delete"] == "delete_from_playlist"
        assert table["u"] == "undo"
        assert table["ctrl+r"] == "redo"
        assert table["ctrl+s"] == "save_playlist"
        assert table["s"] == "shuffle_playlist"
        assert table["space"] == "toggle_autoplay"
        assert table["pageup"] == "page_up"
        assert table["pagedown"] == "page_down"
        assert table["home"] == "navigate_to_first_preset"
        assert table["end"] == "navigate_to_last_preset"

    def test_build_error_view_dispatch_table_maps_keys(self) -> None:
        """Error view dispatch table maps clear_errors key."""
        table = build_error_view_dispatch_table(clear_errors_keys=["c"])
        assert table["c"] == "clear_errors"

    def test_build_file_browser_dispatch_table_extended_keys(self) -> None:
        """File browser dispatch table includes extended keys."""
        table = build_file_browser_dispatch_table(
            nav_up_keys=["k"],
            nav_down_keys=["j"],
            nav_left_keys=["h"],
            nav_right_keys=["l"],
            add_preset_or_load_playlist_keys=["a"],
            play_previous_preset_keys=["K"],
            play_next_preset_keys=["J"],
        )
        assert table["a"] == "add_preset_or_load_playlist"
        assert table["K"] == "play_previous_preset"
        assert table["J"] == "play_next_preset"
