#!/usr/bin/env python3
"""Unit tests for app start path integration.

Tests that PlatyplatyApp correctly receives and stores start_path,
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.app import PlatyplatyApp


class TestAppStartPath:
    """Tests for PlatyplatyApp start_path handling."""

    def test_app_stores_start_path(self) -> None:
        """App should store start_path in _start_path attribute."""
        mock_config = MagicMock()
        mock_playlist = MagicMock()
        test_path = Path("/test/directory")
        app = PlatyplatyApp(
            config=mock_config,
            playlist=mock_playlist,
            start_path=test_path,
        )
        assert app._start_path == test_path

    def test_app_start_path_defaults_to_none(self) -> None:
        """App should default start_path to None if not provided."""
        mock_config = MagicMock()
        mock_playlist = MagicMock()
        app = PlatyplatyApp(config=mock_config, playlist=mock_playlist)
        assert app._start_path is None

