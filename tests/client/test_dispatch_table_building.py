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
