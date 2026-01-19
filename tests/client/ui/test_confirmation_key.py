#!/usr/bin/env python3
"""Unit tests for confirmation prompt key handling.

Tests the handle_confirmation_key() function which processes y/n
key presses in confirmation prompts.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.confirmation_key import handle_confirmation_key


class TestConfirmationKeyHandling:
    """Tests for confirmation key handling."""

    @pytest.mark.asyncio
    async def test_y_key_calls_callback_with_true(self) -> None:
        """Pressing 'y' calls callback with True."""
        callback = AsyncMock()
        hide_func = MagicMock()
        await handle_confirmation_key("y", callback, hide_func)
        callback.assert_awaited_once_with(True)

    @pytest.mark.asyncio
    async def test_n_key_calls_callback_with_false(self) -> None:
        """Pressing 'n' calls callback with False."""
        callback = AsyncMock()
        hide_func = MagicMock()
        await handle_confirmation_key("n", callback, hide_func)
        callback.assert_awaited_once_with(False)

    @pytest.mark.asyncio
    async def test_y_key_hides_prompt(self) -> None:
        """Pressing 'y' calls hide function."""
        callback = AsyncMock()
        hide_func = MagicMock()
        await handle_confirmation_key("y", callback, hide_func)
        hide_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_n_key_hides_prompt(self) -> None:
        """Pressing 'n' calls hide function."""
        callback = AsyncMock()
        hide_func = MagicMock()
        await handle_confirmation_key("n", callback, hide_func)
        hide_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_y_returns_true(self) -> None:
        """Pressing 'y' returns True (handled)."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("y", callback, hide_func)
        assert result is True

    @pytest.mark.asyncio
    async def test_n_returns_true(self) -> None:
        """Pressing 'n' returns True (handled)."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("n", callback, hide_func)
        assert result is True
