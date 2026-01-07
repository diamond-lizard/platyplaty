#!/usr/bin/env python3
"""
Unit tests for Textual-based key event handling.

Tests KEY_PRESSED event parsing, dispatch table building, and action dispatch
via Textual's run_action mechanism.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.dispatch_tables import (
    build_client_dispatch_table,
    build_renderer_dispatch_table,
)
from platyplaty.keybinding_dispatch import dispatch_key_event
from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.types import KeyPressedEvent


# ==============================================================================
# Tests for KEY_PRESSED event parsing with Textual key format
# ==============================================================================


class TestKeyPressedParsing:
    """Tests for KEY_PRESSED event parsing."""

    def test_parse_key_pressed_simple_key(self) -> None:
        """Parse a simple KEY_PRESSED event with a letter key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.event == "KEY_PRESSED"
        assert event.key == "n"

    def test_parse_key_pressed_with_ctrl_modifier(self) -> None:
        """Parse a KEY_PRESSED event with ctrl modifier (Textual format)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "ctrl+n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "ctrl+n"

    def test_parse_key_pressed_with_multiple_modifiers(self) -> None:
        """Parse a KEY_PRESSED event with multiple modifiers (Textual format)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "ctrl+shift+alt+n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "ctrl+shift+alt+n"

    def test_parse_key_pressed_function_key(self) -> None:
        """Parse a KEY_PRESSED event with a function key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "f12"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "f12"

    def test_parse_key_pressed_navigation_key(self) -> None:
        """Parse a KEY_PRESSED event with a navigation key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "pagedown"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "pagedown"

    def test_parse_key_pressed_missing_key_field_returns_none(self) -> None:
        """KEY_PRESSED without key field returns None (invalid event)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED"}'
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_non_platyplaty_source_returns_none(self) -> None:
        """Events with non-PLATYPLATY source return None."""
        line = '{"source": "OTHER", "event": "KEY_PRESSED", "key": "n"}'
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_regular_output_returns_none(self) -> None:
        """Regular stderr output returns None."""
        event = parse_stderr_event("Some debug output from renderer")
        assert event is None

    def test_parse_disconnect_event_still_works(self) -> None:
        """DISCONNECT events still parse correctly."""
        line = '{"source": "PLATYPLATY", "event": "DISCONNECT", "reason": "client closed"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "DISCONNECT"

    def test_parse_quit_event_still_works(self) -> None:
        """QUIT events still parse correctly."""
        line = '{"source": "PLATYPLATY", "event": "QUIT", "reason": "user quit"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "QUIT"


# ==============================================================================
# Tests for dispatch table building (maps keys to action name strings)
# ==============================================================================


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


# ==============================================================================
# Tests for dispatch_key_event (async dispatch via run_action)
# ==============================================================================


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing dispatch."""
    app = MagicMock()
    app.run_action = AsyncMock()
    app._exiting = False
    return app


class TestDispatchKeyEvent:
    """Tests for dispatch_key_event function."""

    @pytest.mark.asyncio
    async def test_dispatch_bound_key_returns_true(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch returns True for bound keys."""
        table = {"n": "next_preset", "p": "previous_preset", "q": "quit"}
        result = await dispatch_key_event("n", table, mock_app)
        assert result is True

    @pytest.mark.asyncio
    async def test_dispatch_unbound_key_returns_false(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch returns False for unbound keys."""
        table = {"n": "next_preset", "p": "previous_preset", "q": "quit"}
        result = await dispatch_key_event("x", table, mock_app)
        assert result is False

    @pytest.mark.asyncio
    async def test_dispatch_calls_run_action_with_action_name(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch calls app.run_action with the action name from table."""
        table = {"n": "next_preset", "q": "quit"}
        await dispatch_key_event("n", table, mock_app)
        mock_app.run_action.assert_awaited_once_with("next_preset")

    @pytest.mark.asyncio
    async def test_dispatch_quit_calls_run_action_quit(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch quit key calls app.run_action with 'quit'."""
        table = {"q": "quit"}
        await dispatch_key_event("q", table, mock_app)
        mock_app.run_action.assert_awaited_once_with("quit")

    @pytest.mark.asyncio
    async def test_dispatch_unbound_key_does_not_call_run_action(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch does not call run_action for unbound keys."""
        table = {"n": "next_preset"}
        await dispatch_key_event("x", table, mock_app)
        mock_app.run_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_handles_connection_error_sets_exiting(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch sets _exiting and calls exit() on ConnectionError."""
        mock_app.run_action = AsyncMock(side_effect=ConnectionError("disconnected"))
        table = {"n": "next_preset"}
        await dispatch_key_event("n", table, mock_app)
        assert mock_app._exiting is True
        mock_app.exit.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_connection_error_skips_if_already_exiting(
        self, mock_app: MagicMock
    ) -> None:
        """Dispatch does not double-exit if already exiting."""
        mock_app._exiting = True
        mock_app.run_action = AsyncMock(side_effect=ConnectionError("disconnected"))
        table = {"n": "next_preset"}
        await dispatch_key_event("n", table, mock_app)
        # exit() should not be called again since already exiting
        mock_app.exit.assert_not_called()
