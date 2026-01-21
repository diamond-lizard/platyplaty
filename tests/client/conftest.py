#!/usr/bin/env python3
"""Shared pytest fixtures for client tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture
def mock_ctx():
    """Create a mock AppContext."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.presets = [Path("/preset.milk")]
    ctx.playlist.associated_filename = None
    return ctx


@pytest.fixture
def mock_app():
    """Create a mock PlatyplatyApp."""
    return MagicMock()

@pytest.fixture
def mock_ctx_empty():
    """Create a mock AppContext with empty playlist."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    ctx.playlist.presets = []
    return ctx


@pytest.fixture
def mock_ctx_nonempty():
    """Create a mock AppContext with non-empty playlist, no unsaved changes."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = False
    ctx.playlist.presets = [Path("/existing.milk")]
    return ctx


@pytest.fixture
def mock_ctx_dirty():
    """Create a mock AppContext with unsaved changes."""
    ctx = MagicMock()
    ctx.playlist = MagicMock()
    ctx.playlist.dirty_flag = True
    ctx.playlist.presets = [Path("/existing.milk")]
    return ctx
