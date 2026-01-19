#!/usr/bin/env python3
"""Unit tests for status line content building.

Tests the build_status_content() function which formats the status line
showing autoplay state, playlist filename, and unsaved changes indicator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.status_line_content import build_status_content


class TestAutoplayState:
    """Tests for autoplay state display."""

    def test_autoplay_on(self) -> None:
        """Shows [autoplay: on] when enabled."""
        result = build_status_content(True, None, False, 100)
        assert result.startswith("[autoplay: on]")

    def test_autoplay_off(self) -> None:
        """Shows [autoplay: off] when disabled."""
        result = build_status_content(False, None, False, 100)
        assert result.startswith("[autoplay: off]")


class TestPlaylistFilename:
    """Tests for playlist filename display."""

    def test_no_playlist_loaded(self) -> None:
        """Shows 'no playlist file loaded' when no filename."""
        result = build_status_content(False, None, False, 100)
        assert "no playlist file loaded" in result

    def test_filename_displayed(self) -> None:
        """Shows playlist basename when loaded."""
        result = build_status_content(False, Path("/home/user/my.platy"), False, 100)
        assert "my.platy" in result

    def test_only_basename_shown(self) -> None:
        """Shows only basename, not full path."""
        result = build_status_content(False, Path("/deep/path/here/test.platy"), False, 100)
        assert "test.platy" in result
        assert "/deep/path" not in result


class TestDirtyIndicator:
    """Tests for unsaved changes indicator."""

    def test_no_prefix_when_clean(self) -> None:
        """No asterisk prefix when not dirty."""
        result = build_status_content(False, Path("/test.platy"), False, 100)
        assert "* test.platy" not in result
        assert "test.platy" in result

    def test_asterisk_prefix_when_dirty(self) -> None:
        """Shows '* ' prefix before filename when dirty."""
        result = build_status_content(False, Path("/test.platy"), True, 100)
        assert "* test.platy" in result
