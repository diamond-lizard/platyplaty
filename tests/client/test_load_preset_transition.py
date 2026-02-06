#!/usr/bin/env python3
"""Unit tests for load_preset transition_type config threading."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.preset_command import load_preset


def _make_context(transition_type: str) -> MagicMock:
    """Create a mock context with the given transition type.

    Args:
        transition_type: Value for config.transition_type ("soft" or "hard").

    Returns:
        MagicMock configured as an AppContext with async client.
    """
    ctx = MagicMock()
    ctx.client = AsyncMock()
    ctx.client.send_command = AsyncMock()
    ctx.renderer_process = MagicMock()
    ctx.renderer_process.returncode = None
    ctx.config.transition_type = transition_type
    ctx.config.fullscreen = False
    return ctx


class TestLoadPresetTransitionConfig:
    """Tests that load_preset threads config transition_type to IPC."""

    @pytest.mark.asyncio
    async def test_soft_config_passed_to_ipc(self) -> None:
        """Config transition_type='soft' is passed to send_command."""
        ctx = _make_context("soft")
        with patch(
            "platyplaty.autoplay_helpers.is_preset_playable",
            return_value=True,
        ):
            await load_preset(ctx, MagicMock(), Path("/test/a.milk"))
        ctx.client.send_command.assert_any_call(
            "LOAD PRESET",
            path="/test/a.milk",
            transition_type="soft",
        )

    @pytest.mark.asyncio
    async def test_hard_config_passed_to_ipc(self) -> None:
        """Config transition_type='hard' is passed to send_command."""
        ctx = _make_context("hard")
        with patch(
            "platyplaty.autoplay_helpers.is_preset_playable",
            return_value=True,
        ):
            await load_preset(ctx, MagicMock(), Path("/test/a.milk"))
        ctx.client.send_command.assert_any_call(
            "LOAD PRESET",
            path="/test/a.milk",
            transition_type="hard",
        )
