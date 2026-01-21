#!/usr/bin/env python3
"""Unit tests for :save command validation and error handling."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.save_playlist import save_to_path
from platyplaty.playlist import Playlist


def make_ctx(playlist: Playlist) -> MagicMock:
    """Create a mock AppContext with the given playlist."""
    ctx = MagicMock()
    ctx.playlist = playlist
    return ctx


class TestExtensionValidation:
    """Tests for .platy extension validation."""

    @pytest.mark.asyncio
    async def test_save_rejects_invalid_extension(self, tmp_path: Path) -> None:
        """Save with non-.platy extension returns error."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        filepath = tmp_path / "test.txt"
        success, error = await save_to_path(str(filepath), ctx, MagicMock(), tmp_path)
        assert success is False
        assert error == "Error: a playlist filename must end with .platy"

    @pytest.mark.asyncio
    async def test_save_accepts_uppercase_platy(self, tmp_path: Path) -> None:
        """Save with .PLATY extension succeeds (case-insensitive)."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        filepath = tmp_path / "test.PLATY"
        success, error = await save_to_path(str(filepath), ctx, MagicMock(), tmp_path)
        assert success is True
        assert error is None
        assert filepath.exists()


class TestSaveErrorHandling:
    """Tests for save error handling."""

    @pytest.mark.asyncio
    async def test_save_to_nonexistent_directory(self, tmp_path: Path) -> None:
        """Save to non-existent directory returns error."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        filepath = tmp_path / "nonexistent" / "test.platy"
        success, error = await save_to_path(str(filepath), ctx, MagicMock(), tmp_path)
        assert success is False
        assert "Error: could not save playlist:" in error

    @pytest.mark.asyncio
    async def test_save_failure_keeps_dirty_flag(self, tmp_path: Path) -> None:
        """Playlist remains dirty after failed save."""
        playlist = Playlist([Path("/a.milk")])
        playlist.dirty_flag = True
        ctx = make_ctx(playlist)
        filepath = tmp_path / "nonexistent" / "test.platy"
        await save_to_path(str(filepath), ctx, MagicMock(), tmp_path)
        assert playlist.dirty_flag is True
