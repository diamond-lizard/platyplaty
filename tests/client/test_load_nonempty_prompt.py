#!/usr/bin/env python3
"""Unit tests for :load command with non-empty playlist prompt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def mock_ctx():
    """Create a mock AppContext with non-empty playlist, no unsaved changes."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    ctx.playlist.presets = [Path("/existing.milk")]
    return ctx


@pytest.fixture
def mock_app():
    """Create a mock PlatyplatyApp."""
    return MagicMock()


class TestLoadWithNonEmptyPlaylist:
    """Tests for :load when playlist is non-empty but not dirty."""

    @pytest.mark.asyncio
    async def test_load_shows_nonempty_prompt(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Load shows non-empty prompt when playlist has items."""
        from platyplaty.commands.load_confirm import check_and_load
        from platyplaty.ui.prompt_messages import PROMPT_LOAD_CLEAR_NONEMPTY

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt

        await check_and_load(playlist_file, mock_ctx, mock_app)

        mock_prompt.show_prompt.assert_called_once()
        call_args = mock_prompt.show_prompt.call_args
        assert call_args[0][0] == PROMPT_LOAD_CLEAR_NONEMPTY

    @pytest.mark.asyncio
    async def test_nonempty_prompt_not_shown_when_dirty(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Dirty flag prompt supersedes non-empty prompt."""
        from platyplaty.commands.load_confirm import check_and_load
        from platyplaty.ui.prompt_messages import PROMPT_LOAD_REPLACE_UNSAVED

        mock_ctx.playlist.dirty_flag = True
        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt

        await check_and_load(playlist_file, mock_ctx, mock_app)

        call_args = mock_prompt.show_prompt.call_args
        assert call_args[0][0] == PROMPT_LOAD_REPLACE_UNSAVED


class TestLoadNonEmptyConfirmation:
    """Tests for non-empty playlist confirmation callbacks."""

    @pytest.mark.asyncio
    async def test_nonempty_confirmed_performs_load(
        self, mock_ctx, mock_app, tmp_path
    ):
        """User pressing 'y' on non-empty prompt triggers load."""
        from platyplaty.commands.load_confirm import check_and_load

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_prompt.show_prompt.side_effect = capture_callback

        await check_and_load(playlist_file, mock_ctx, mock_app)

        with patch("platyplaty.playlist_snapshot.push_undo_snapshot"):
            with patch(
                "platyplaty.commands.load_helpers.perform_load",
                new_callable=AsyncMock,
                return_value=(True, None),
            ) as mock_load:
                await captured_callback(True)

        mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_nonempty_cancelled_does_not_load(
        self, mock_ctx, mock_app, tmp_path
    ):
        """User pressing 'n' on non-empty prompt cancels load."""
        from platyplaty.commands.load_confirm import check_and_load

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_prompt.show_prompt.side_effect = capture_callback

        await check_and_load(playlist_file, mock_ctx, mock_app)

        with patch(
            "platyplaty.commands.load_helpers.perform_load",
            new_callable=AsyncMock,
        ) as mock_load:
            await captured_callback(False)

        mock_load.assert_not_called()
