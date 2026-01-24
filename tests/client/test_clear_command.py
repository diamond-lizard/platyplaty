#!/usr/bin/env python3
"""Unit tests for :clear command with unsaved changes prompt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def mock_ctx():
    """Create a mock AppContext."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    ctx.playlist.presets = [Path("/test.milk")]
    ctx.autoplay_manager = MagicMock()
    return ctx


@pytest.fixture
def mock_app():
    """Create a mock PlatyplatyApp."""
    return MagicMock()


class TestClearWithoutUnsavedChanges:
    """Tests for clear when no unsaved changes."""

    @pytest.mark.asyncio
    async def test_clear_without_dirty_flag(self, mock_ctx, mock_app):
        """Clear executes immediately when dirty_flag is False."""
        from platyplaty.commands.clear_playlist import execute

        with patch("platyplaty.commands.clear_playlist.push_undo_snapshot"):
            result = await execute(mock_ctx, mock_app)

        assert result == (True, None)
        mock_ctx.playlist.clear.assert_called_once()


class TestClearWithUnsavedChanges:
    """Tests for clear when unsaved changes exist."""

    @pytest.mark.asyncio
    async def test_clear_with_dirty_flag_shows_prompt(self, mock_ctx, mock_app):
        """Clear shows confirmation prompt when dirty_flag is True."""
        from platyplaty.commands.clear_playlist import execute

        mock_ctx.playlist.dirty_flag = True
        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line

        with patch("platyplaty.commands.clear_playlist.push_undo_snapshot"):
            result = await execute(mock_ctx, mock_app)

        assert result == (True, None)
        mock_command_line.show_confirmation_prompt.assert_called_once()
        mock_ctx.playlist.clear.assert_not_called()

    @pytest.mark.asyncio
    async def test_clear_cancelled_when_prompt_declined(
        self, mock_ctx, mock_app
    ):
        """Clear is cancelled when user declines prompt."""
        from platyplaty.commands.clear_playlist import execute

        mock_ctx.playlist.dirty_flag = True
        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_command_line.show_confirmation_prompt.side_effect = capture_callback

        with patch("platyplaty.commands.clear_playlist.push_undo_snapshot"):
            await execute(mock_ctx, mock_app)

        # Simulate user pressing 'n'
        await captured_callback(False)
        mock_ctx.playlist.clear.assert_not_called()


class TestClearStopsAutoplay:
    """Tests for clear stopping autoplay."""

    @pytest.fixture
    def mock_ctx(self):
        """Create a mock AppContext."""
        ctx = MagicMock()
        ctx.playlist = MagicMock()
        ctx.autoplay_manager = MagicMock()
        return ctx

    @pytest.mark.asyncio
    async def test_clear_stops_autoplay(self, mock_ctx):
        """Clear stops autoplay when executed."""
        from platyplaty.commands.clear_playlist import perform_clear

        with patch("platyplaty.commands.clear_playlist.push_undo_snapshot"):
            await perform_clear(mock_ctx)

        mock_ctx.autoplay_manager.stop_autoplay.assert_called_once()
