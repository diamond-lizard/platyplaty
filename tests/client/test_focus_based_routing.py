#!/usr/bin/env python3
"""
Unit tests for focus-based key routing.

Tests dispatch_focused_key_event routes keys based on current focus.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.keybinding_dispatch import dispatch_focused_key_event


@pytest.fixture
def mock_app() -> MagicMock:
    """Create a mock PlatyplatyApp for testing dispatch."""
    app = MagicMock()
    app.run_action = AsyncMock()
    # Mock query_one to return a mock CommandLine with clear_persistent_message
    mock_cmd_line = MagicMock()
    mock_cmd_line.clear_persistent_message = MagicMock()
    app.query_one = MagicMock(return_value=mock_cmd_line)
    return app


@pytest.fixture
def mock_ctx() -> MagicMock:
    """Create a mock AppContext with dispatch tables and focus."""
    ctx = MagicMock()
    ctx.exiting = False
    ctx.current_focus = "file_browser"
    ctx.global_dispatch_table = {"q": "quit", "tab": "switch_focus"}
    ctx.file_browser_dispatch_table = {"a": "add_preset_or_load_playlist"}
    ctx.playlist_dispatch_table = {"u": "undo", "s": "shuffle_playlist"}
    ctx.error_view_dispatch_table = {"c": "clear_errors"}
    return ctx


class TestFocusBasedRouting:
    """Tests for focus-based key routing."""

    @pytest.mark.asyncio
    async def test_global_key_works_regardless_of_focus(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Global keys work when file browser has focus."""
        result = await dispatch_focused_key_event("q", mock_ctx, mock_app)
        assert result is True
        mock_app.run_action.assert_awaited_once_with("quit")

    @pytest.mark.asyncio
    async def test_global_key_works_with_playlist_focus(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Global keys work when playlist has focus."""
        mock_ctx.current_focus = "playlist"
        result = await dispatch_focused_key_event("tab", mock_ctx, mock_app)
        assert result is True
        mock_app.run_action.assert_awaited_once_with("switch_focus")

    @pytest.mark.asyncio
    async def test_file_browser_key_works_when_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """File browser keys work when file browser has focus."""
        mock_ctx.current_focus = "file_browser"
        result = await dispatch_focused_key_event("a", mock_ctx, mock_app)
        assert result is True
        mock_app.run_action.assert_awaited_once_with("add_preset_or_load_playlist")

    @pytest.mark.asyncio
    async def test_file_browser_key_ignored_when_playlist_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """File browser keys silently ignored when playlist has focus."""
        mock_ctx.current_focus = "playlist"
        result = await dispatch_focused_key_event("a", mock_ctx, mock_app)
        assert result is False
        mock_app.run_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_playlist_key_works_when_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Playlist keys work when playlist has focus."""
        mock_ctx.current_focus = "playlist"
        result = await dispatch_focused_key_event("u", mock_ctx, mock_app)
        assert result is True
        mock_app.run_action.assert_awaited_once_with("undo")

    @pytest.mark.asyncio
    async def test_playlist_key_ignored_when_file_browser_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Playlist keys silently ignored when file browser has focus."""
        mock_ctx.current_focus = "file_browser"
        result = await dispatch_focused_key_event("u", mock_ctx, mock_app)
        assert result is False
        mock_app.run_action.assert_not_called()

    @pytest.mark.asyncio
    async def test_error_view_key_works_when_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Error view keys work when error view has focus."""
        mock_ctx.current_focus = "error_view"
        result = await dispatch_focused_key_event("c", mock_ctx, mock_app)
        assert result is True
        mock_app.run_action.assert_awaited_once_with("clear_errors")

    @pytest.mark.asyncio
    async def test_error_view_key_ignored_when_playlist_focused(
        self, mock_ctx: MagicMock, mock_app: MagicMock
    ) -> None:
        """Error view keys silently ignored when playlist has focus."""
        mock_ctx.current_focus = "playlist"
        result = await dispatch_focused_key_event("c", mock_ctx, mock_app)
        assert result is False
        mock_app.run_action.assert_not_called()
