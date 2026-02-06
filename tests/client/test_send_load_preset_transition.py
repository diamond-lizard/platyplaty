#!/usr/bin/env python3
"""Unit tests for send_load_preset transition_type parameter."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.preset_command import send_load_preset


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock application context."""
    ctx = MagicMock()
    ctx.client = AsyncMock()
    ctx.client.send_command = AsyncMock()
    return ctx


class TestSendLoadPresetTransitionType:
    """Tests for transition_type in send_load_preset."""

    @pytest.mark.asyncio
    async def test_soft_transition_type_in_payload(
        self, mock_context: MagicMock
    ) -> None:
        """Calling with transition_type='soft' passes it to send_command."""
        await send_load_preset(
            mock_context, Path("/test/a.milk"), transition_type="soft"
        )
        mock_context.client.send_command.assert_called_once_with(
            "LOAD PRESET",
            path="/test/a.milk",
            transition_type="soft",
        )

    @pytest.mark.asyncio
    async def test_hard_transition_type_in_payload(
        self, mock_context: MagicMock
    ) -> None:
        """Calling with transition_type='hard' passes it to send_command."""
        await send_load_preset(
            mock_context, Path("/test/a.milk"), transition_type="hard"
        )
        mock_context.client.send_command.assert_called_once_with(
            "LOAD PRESET",
            path="/test/a.milk",
            transition_type="hard",
        )
