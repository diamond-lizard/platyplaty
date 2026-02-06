#!/usr/bin/env python3
"""Unit tests for render-time errors during manual playback."""

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
        ctx.config.transition_type = "hard"

        app = MagicMock()
        app.query_one = MagicMock(return_value=MagicMock())
        get_preset = MagicMock(return_value=Path("/test/preset.milk"))

        with patch(
            "platyplaty.autoplay_helpers.is_preset_playable",
            return_value=True,
        ):
            await load_preset_by_direction(ctx, app, get_preset, "next")

        assert len(ctx.error_log) == 1
        assert "Failed to load preset" in ctx.error_log[0]
