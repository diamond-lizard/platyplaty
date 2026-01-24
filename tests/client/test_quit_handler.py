#!/usr/bin/env python3
"""Unit tests for quit handler with confirmation prompts."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def mock_ctx():
    """Create a mock AppContext."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    return ctx


@pytest.fixture
def mock_app():
    """Create a mock PlatyplatyApp."""
    app = MagicMock()
    app.graceful_shutdown = AsyncMock()
    return app


class TestQuitWithoutUnsavedChanges:
    """Tests for quit when no unsaved changes."""

    @pytest.mark.asyncio
    async def test_quit_shows_normal_prompt(self, mock_ctx, mock_app):
        """Quit shows 'Quit? (y/n)' when no unsaved changes."""
        from platyplaty.quit_handler import handle_quit
        from platyplaty.ui.prompt_messages import PROMPT_QUIT

        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line

        await handle_quit(mock_ctx, mock_app)

        mock_command_line.show_confirmation_prompt.assert_called_once()
        call_args = mock_command_line.show_confirmation_prompt.call_args
        assert call_args[0][0] == PROMPT_QUIT


class TestQuitWithUnsavedChanges:
    """Tests for quit when unsaved changes exist."""

    @pytest.mark.asyncio
    async def test_quit_shows_unsaved_changes_prompt(self, mock_ctx, mock_app):
        """Quit shows unsaved changes prompt when dirty_flag is True."""
        from platyplaty.quit_handler import handle_quit
        from platyplaty.ui.prompt_messages import PROMPT_QUIT_UNSAVED

        mock_ctx.playlist.dirty_flag = True
        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line

        await handle_quit(mock_ctx, mock_app)

        mock_command_line.show_confirmation_prompt.assert_called_once()
        call_args = mock_command_line.show_confirmation_prompt.call_args
        assert call_args[0][0] == PROMPT_QUIT_UNSAVED


class TestQuitConfirmation:
    """Tests for quit confirmation callbacks."""

    @pytest.mark.asyncio
    async def test_quit_confirmed_calls_graceful_shutdown(
        self, mock_ctx, mock_app
    ):
        """User pressing 'y' triggers graceful shutdown."""
        from platyplaty.quit_handler import handle_quit

        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_command_line.show_confirmation_prompt.side_effect = capture_callback

        await handle_quit(mock_ctx, mock_app)
        await captured_callback(True)

        mock_app.graceful_shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_quit_cancelled_does_not_shutdown(self, mock_ctx, mock_app):
        """User pressing 'n' does not trigger shutdown."""
        from platyplaty.quit_handler import handle_quit

        mock_command_line = MagicMock()
        mock_app.query_one.return_value = mock_command_line
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_command_line.show_confirmation_prompt.side_effect = capture_callback

        await handle_quit(mock_ctx, mock_app)
        await captured_callback(False)

        mock_app.graceful_shutdown.assert_not_called()
