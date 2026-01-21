#!/usr/bin/env python3
"""Unit tests for :load command with empty playlist (no prompt)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def mock_ctx():
    """Create a mock AppContext with empty playlist."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    ctx.playlist.presets = []
    return ctx


@pytest.fixture
def mock_app():
    """Create a mock PlatyplatyApp."""
    return MagicMock()


class TestLoadWithEmptyPlaylist:
    """Tests for :load when playlist is empty (no prompts needed)."""

    @pytest.mark.asyncio
    async def test_load_no_prompt_when_empty(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Load proceeds without prompt when playlist is empty."""
        from platyplaty.commands.load_confirm import check_and_load

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt

        with patch("platyplaty.commands.load_confirm.push_undo_snapshot"):
            with patch(
                "platyplaty.commands.load_confirm.perform_load",
                new_callable=AsyncMock,
                return_value=(True, None),
            ) as mock_load:
                await check_and_load(playlist_file, mock_ctx, mock_app)

        mock_prompt.show_prompt.assert_not_called()
        mock_load.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_pushes_undo_snapshot(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Load pushes undo snapshot before loading."""
        from platyplaty.commands.load_confirm import check_and_load

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")

        with patch(
            "platyplaty.commands.load_confirm.push_undo_snapshot"
        ) as mock_push:
            with patch(
                "platyplaty.commands.load_confirm.perform_load",
                new_callable=AsyncMock,
                return_value=(True, None),
            ):
                await check_and_load(playlist_file, mock_ctx, mock_app)

        mock_push.assert_called_once_with(mock_ctx)

    @pytest.mark.asyncio
    async def test_load_returns_success_on_empty(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Load returns success tuple when playlist is empty."""
        from platyplaty.commands.load_confirm import check_and_load

        playlist_file = tmp_path / "test.platy"
        playlist_file.write_text("/preset.milk\n")

        with patch("platyplaty.commands.load_confirm.push_undo_snapshot"):
            with patch(
                "platyplaty.commands.load_confirm.perform_load",
                new_callable=AsyncMock,
                return_value=(True, None),
            ):
                result = await check_and_load(playlist_file, mock_ctx, mock_app)

        assert result == (True, None)
