#!/usr/bin/env python3
"""Unit tests for confirmation prompt ignoring non-y/n keys.

Tests that handle_confirmation_key() correctly ignores all keys
except 'y' and 'n'.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.confirmation_key import handle_confirmation_key


class TestIgnoreOtherKeys:
    """Tests that non-y/n keys are ignored."""

    @pytest.mark.asyncio
    async def test_ignore_letter_a(self) -> None:
        """Pressing 'a' is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("a", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()
        hide_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_ignore_letter_q(self) -> None:
        """Pressing 'q' is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("q", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ignore_escape(self) -> None:
        """Pressing Escape is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("escape", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ignore_enter(self) -> None:
        """Pressing Enter is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("enter", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ignore_space(self) -> None:
        """Pressing Space is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("space", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_ignore_number(self) -> None:
        """Pressing a number key is ignored."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("1", callback, hide_func)
        assert result is False
        callback.assert_not_awaited()


class TestUppercaseHandling:
    """Tests for uppercase Y and N keys."""

    @pytest.mark.asyncio
    async def test_uppercase_y_accepted(self) -> None:
        """Uppercase 'Y' is accepted."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("Y", callback, hide_func)
        assert result is True
        callback.assert_awaited_once_with(True)

    @pytest.mark.asyncio
    async def test_uppercase_n_accepted(self) -> None:
        """Uppercase 'N' is accepted."""
        callback = AsyncMock()
        hide_func = MagicMock()
        result = await handle_confirmation_key("N", callback, hide_func)
        assert result is True
        callback.assert_awaited_once_with(False)


class TestNoneCallback:
    """Tests for handling None callback."""

    @pytest.mark.asyncio
    async def test_y_with_none_callback(self) -> None:
        """Pressing 'y' with None callback doesn't crash."""
        hide_func = MagicMock()
        result = await handle_confirmation_key("y", None, hide_func)
        assert result is True
        hide_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_n_with_none_callback(self) -> None:
        """Pressing 'n' with None callback doesn't crash."""
        hide_func = MagicMock()
        result = await handle_confirmation_key("n", None, hide_func)
        assert result is True
        hide_func.assert_called_once()
