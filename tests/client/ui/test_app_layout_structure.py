#!/usr/bin/env python3
"""Unit tests for app layout structure.

Tests that the app compose method yields the expected widgets
in the correct order with correct IDs.
"""

import sys
from pathlib import Path

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


class TestAppLayoutWidgets:
    """Tests that the app yields the expected widgets."""

    def test_compose_yields_file_browser(self) -> None:
        """App compose yields a FileBrowser widget."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert "file_browser" in ids

    def test_compose_yields_playlist(self) -> None:
        """App compose yields a PlaylistView widget."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert "playlist" in ids

    def test_compose_yields_status_line(self) -> None:
        """App compose yields a StatusLine widget."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert "status_line" in ids

    def test_compose_yields_section_divider(self) -> None:
        """App compose yields a section divider."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert "section_divider" in ids

    def test_compose_yields_command_line(self) -> None:
        """App compose yields a CommandLine widget."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert "command_line" in ids


class TestAppLayoutOrder:
    """Tests that widgets are in the correct order."""

    def test_file_browser_before_divider(self) -> None:
        """FileBrowser comes before section divider."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert ids.index("file_browser") < ids.index("section_divider")

    def test_divider_before_playlist(self) -> None:
        """Section divider comes before playlist."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert ids.index("section_divider") < ids.index("playlist")

    def test_playlist_before_status_line(self) -> None:
        """Playlist comes before status line."""
        app = make_test_app()
        widgets = list(app.compose())
        ids = [w.id for w in widgets]
        assert ids.index("playlist") < ids.index("status_line")

        def test_command_line_before_status_line(self) -> None:
            """CommandLine comes before StatusLine in yield order."""
            app = make_test_app()
            widgets = list(app.compose())
            ids = [w.id for w in widgets]
            assert ids.index("command_line") < ids.index("status_line")
