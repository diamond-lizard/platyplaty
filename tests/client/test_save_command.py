#!/usr/bin/env python3
"""Unit tests for :save command handler."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.save_playlist import (
    execute,
    save_to_associated,
    save_to_path,
)
from platyplaty.playlist import Playlist


def make_ctx(playlist: Playlist) -> MagicMock:
    """Create a mock AppContext with the given playlist."""
    ctx = MagicMock()
    ctx.playlist = playlist
    return ctx


class TestSaveWithArgument:
    """Tests for :save with path argument."""

    @pytest.mark.asyncio
    async def test_save_with_valid_platy_extension(self, tmp_path: Path) -> None:
        """Save with .platy extension succeeds."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        filepath = tmp_path / "test.platy"
        success, error = await save_to_path(str(filepath), ctx, tmp_path)
        assert success is True
        assert error is None
        assert filepath.exists()

    @pytest.mark.asyncio
    async def test_save_updates_associated_filename(self, tmp_path: Path) -> None:
        """Save with argument updates associated filename."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        filepath = tmp_path / "new.platy"
        await save_to_path(str(filepath), ctx, tmp_path)
        assert playlist.associated_filename == filepath


class TestSaveWithoutArgument:
    """Tests for :save without path argument."""

    @pytest.mark.asyncio
    async def test_save_to_associated_filename(self, tmp_path: Path) -> None:
        """Save without argument uses associated filename."""
        playlist = Playlist([Path("/a.milk")])
        playlist_file = tmp_path / "existing.platy"
        playlist.associated_filename = playlist_file
        ctx = make_ctx(playlist)
        success, error = await save_to_associated(ctx)
        assert success is True
        assert error is None
        assert playlist_file.exists()

    @pytest.mark.asyncio
    async def test_save_no_associated_returns_error(self) -> None:
        """Save without argument and no associated filename returns error."""
        playlist = Playlist([Path("/a.milk")])
        ctx = make_ctx(playlist)
        success, error = await save_to_associated(ctx)
        assert success is False
        assert error == "Error: No file name"

    @pytest.mark.asyncio
    async def test_save_clears_dirty_flag(self, tmp_path: Path) -> None:
        """Save without argument clears dirty flag."""
        playlist = Playlist([Path("/a.milk")])
        playlist_file = tmp_path / "existing.platy"
        playlist.associated_filename = playlist_file
        playlist.dirty_flag = True
        ctx = make_ctx(playlist)
        await save_to_associated(ctx)
        assert playlist.dirty_flag is False

