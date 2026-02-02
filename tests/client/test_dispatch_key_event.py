#!/usr/bin/env python3
"""
Unit tests for dispatch_key_event function.

Tests async key dispatch via Textual's run_action mechanism.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.keybinding_dispatch import dispatch_key_event

@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing dispatch."""
    app = MagicMock()
    app.run_action = AsyncMock()
    return app

@pytest.fixture
def mock_ctx() -> MagicMock:
    """Create a mock AppContext for testing dispatch."""
    ctx = MagicMock()
    ctx.exiting = False
    return ctx

class TestDispatchKeyEvent:
    """Tests for dispatch_key_event function."""
    @pytest.mark.asyncio
    async def test_dispatch_bound_key_returns_true(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch returns True for bound keys."""
        table = {"n": "next_preset", "p": "previous_preset", "q": "quit"}
        result = await dispatch_key_event("n", table, mock_ctx, mock_app)
        assert result is True

    @pytest.mark.asyncio
    async def test_dispatch_unbound_key_returns_false(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch returns False for unbound keys."""
        table = {"n": "next_preset", "p": "previous_preset", "q": "quit"}
        result = await dispatch_key_event("x", table, mock_ctx, mock_app)
        assert result is False

    @pytest.mark.asyncio
    async def test_dispatch_calls_run_action_with_action_name(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch calls app.run_action with the action name from table."""
        table = {"n": "next_preset", "q": "quit"}
        await dispatch_key_event("n", table, mock_ctx, mock_app)
        mock_app.run_action.assert_awaited_once_with("next_preset")

    @pytest.mark.asyncio
    async def test_dispatch_quit_calls_run_action_quit(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch quit key calls app.run_action with 'quit'."""
        table = {"q": "quit"}
        await dispatch_key_event("q", table, mock_ctx, mock_app)
        mock_app.run_action.assert_awaited_once_with("quit")

    @pytest.mark.asyncio
    async def test_dispatch_unbound_key_does_not_call_run_action(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch does not call run_action for unbound keys."""
        table = {"n": "next_preset"}
        await dispatch_key_event("x", table, mock_ctx, mock_app)
        mock_app.run_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_suppresses_connection_error(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Dispatch suppresses ConnectionError without exiting.

        The crash handler (stderr_monitor_task) is responsible for
        handling renderer crashes, not the dispatch function.
        """
        mock_app.run_action = AsyncMock(side_effect=ConnectionError("disconnected"))
        table = {"n": "next_preset"}
        result = await dispatch_key_event("n", table, mock_ctx, mock_app)
        assert result is True  # Key was handled
        mock_app.exit.assert_not_called()  # No exit on ConnectionError
