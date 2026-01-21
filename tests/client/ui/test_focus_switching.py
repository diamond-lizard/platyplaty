#!/usr/bin/env python3
"""Unit tests for focus switching behavior.

Tests that the Tab key (switch_focus action) correctly toggles focus
between file browser and playlist sections, and updates visual state.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.app import PlatyplatyApp
from platyplaty.playlist import Playlist
from platyplaty.types.app_config import AppConfig
from platyplaty.types.keybindings import Keybindings


def make_test_app() -> PlatyplatyApp:
    """Create a PlatyplatyApp with minimal test configuration."""
    config = AppConfig(
        socket_path="/tmp/test.sock",
        audio_source="test",
        preset_duration=30.0,
        fullscreen=False,
        keybindings=Keybindings(),
    )
    playlist = Playlist([])
    return PlatyplatyApp(config, playlist)


class TestInitialFocus:
    """Tests for initial focus state."""

    def test_initial_focus_is_file_browser(self) -> None:
        """Initial focus is on file browser."""
        app = make_test_app()
        assert app.ctx.current_focus == "file_browser"


class TestFocusSwitching:
    """Tests for focus switching action."""

    @pytest.mark.asyncio
    async def test_switch_from_file_browser_to_playlist(self) -> None:
        """Switching from file browser sets focus to playlist."""
        app = make_test_app()
        app.ctx.current_focus = "file_browser"
        with patch.object(app, "_update_section_focus"):
            await app.action_switch_focus()
        assert app.ctx.current_focus == "playlist"

    @pytest.mark.asyncio
    async def test_switch_from_playlist_to_file_browser(self) -> None:
        """Switching from playlist sets focus to file browser."""
        app = make_test_app()
        app.ctx.current_focus = "playlist"
        with patch.object(app, "_update_section_focus"):
            await app.action_switch_focus()
        assert app.ctx.current_focus == "file_browser"

    @pytest.mark.asyncio
    async def test_switch_calls_update_section_focus(self) -> None:
        """Switching focus calls _update_section_focus."""
        app = make_test_app()
        with patch.object(app, "_update_section_focus") as mock_update:
            await app.action_switch_focus()
            mock_update.assert_called_once()


class TestVisualFocusUpdate:
    """Tests for visual focus state updates."""

    def test_update_section_focus_with_file_browser(self) -> None:
        """File browser focused updates widget states correctly."""
        app = make_test_app()
        app.ctx.current_focus = "file_browser"
        mock_fb = MagicMock()
        mock_pv = MagicMock()
        with patch.object(app, "query_one", side_effect=[mock_fb, mock_pv]):
            app._update_section_focus()
        mock_fb.set_focused.assert_called_once_with(True)
        mock_pv.set_focused.assert_called_once_with(False)

    def test_update_section_focus_with_playlist(self) -> None:
        """Playlist focused updates widget states correctly."""
        app = make_test_app()
        app.ctx.current_focus = "playlist"
        mock_fb = MagicMock()
        mock_pv = MagicMock()
        with patch.object(app, "query_one", side_effect=[mock_fb, mock_pv]):
            app._update_section_focus()
        mock_fb.set_focused.assert_called_once_with(False)
        mock_pv.set_focused.assert_called_once_with(True)
