#!/usr/bin/env python3
"""Unit tests for render-time error handling.

Tests that render-time errors are properly handled for both
manual playback and autoplay scenarios.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.socket_exceptions import RendererError


class TestManualPlaybackErrors:
    """Tests for render-time errors during manual playback."""

    @pytest.mark.asyncio
    async def test_error_appended_to_error_log(self) -> None:
        """Renderer error message is appended to ctx.error_log."""
        from platyplaty.app_actions import load_preset_by_direction

        ctx = MagicMock()
        ctx.renderer_ready = True
        ctx.exiting = False
        ctx.error_log = []
        ctx.client = AsyncMock()
        ctx.client.send_command = AsyncMock(
            side_effect=RendererError("Failed to load preset")
        )
        ctx.renderer_process = MagicMock()
        ctx.renderer_process.returncode = None

        app = MagicMock()
        app.query_one = MagicMock(return_value=MagicMock())
        get_preset = MagicMock(return_value=Path("/test/preset.milk"))

        with patch("platyplaty.autoplay_helpers.is_preset_playable", return_value=True):
            await load_preset_by_direction(ctx, app, get_preset, "next")

        assert len(ctx.error_log) == 1
        assert "Failed to load preset" in ctx.error_log[0]


class TestAutoplayErrors:
    """Tests for render-time errors during autoplay."""

    @pytest.mark.asyncio
    async def test_error_appended_to_error_log_during_autoplay(self) -> None:
        """Renderer error during autoplay is appended to ctx.error_log."""
        from platyplaty.preset_command import load_preset
        from platyplaty.preset_validator import is_valid_preset

        ctx = MagicMock()
        ctx.error_log = []
        ctx.client = AsyncMock()
        ctx.client.send_command = AsyncMock(
            side_effect=RendererError("Renderer error")
        )
        ctx.renderer_process = MagicMock()
        ctx.renderer_process.returncode = None

        with patch("platyplaty.autoplay_helpers.is_preset_playable", return_value=True):
            success, error = await load_preset(ctx, MagicMock(), Path("/test/preset.milk"))

        assert success is False
        assert error == "Renderer error"

    @pytest.mark.asyncio
    async def test_autoplay_marks_broken_and_skips(self) -> None:
        """Autoplay marks preset as broken and skips to next."""
        from platyplaty.autoplay_advance import advance_playlist_to_next
        from platyplaty.playlist import Playlist

        ctx = MagicMock()
        ctx.error_log = []
        ctx.client = AsyncMock()
        call_count = [0]

        async def mock_send_command(cmd, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise RendererError("First preset error")
            return None

        ctx.client.send_command = mock_send_command
        ctx.renderer_process = MagicMock()
        ctx.renderer_process.returncode = None

        playlist = Playlist([
            Path("/test/preset1.milk"),
            Path("/test/preset2.milk"),
        ])
        playlist.set_playing(0)

        with patch("platyplaty.autoplay_helpers.is_preset_playable", return_value=True):
            result = await advance_playlist_to_next(ctx, MagicMock(), playlist)

        assert result is True
        assert 1 in playlist.broken_indices
        assert playlist.get_playing() == 0
        assert "First preset error" in ctx.error_log
