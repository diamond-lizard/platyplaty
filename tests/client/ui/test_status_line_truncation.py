#!/usr/bin/env python3
"""Unit tests for status line truncation behavior.

Tests that the status line truncates filenames properly while
never truncating the autoplay state.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.status_line_content import build_status_content


class TestAutoplayNeverTruncated:
    """Tests that autoplay state is never truncated."""

    def test_autoplay_on_preserved_narrow(self) -> None:
        """Autoplay on is preserved even at narrow width."""
        result = build_status_content(True, Path("/x.platy"), False, 30)
        assert result.startswith("[autoplay: on]")

    def test_autoplay_off_preserved_narrow(self) -> None:
        """Autoplay off is preserved even at narrow width."""
        result = build_status_content(False, Path("/x.platy"), False, 30)
        assert result.startswith("[autoplay: off]")


class TestFilenameTruncation:
    """Tests for filename truncation when width is limited."""

    def test_long_filename_truncated(self) -> None:
        """Long filename gets truncated with tilde."""
        # [autoplay: off] = 15 chars, + space = 16, leaves 14 for filename
        result = build_status_content(False, Path("/very-long-name.platy"), False, 30)
        assert "[autoplay: off]" in result
        assert "~" in result  # Truncation indicator

    def test_short_filename_not_truncated(self) -> None:
        """Short filename fits without truncation."""
        result = build_status_content(False, Path("/a.platy"), False, 100)
        assert "a.platy" in result
        assert "~" not in result

    def test_dirty_prefix_with_truncation(self) -> None:
        """Dirty prefix preserved even when truncating."""
        result = build_status_content(False, Path("/very-long-name.platy"), True, 30)
        assert "* " in result  # Dirty prefix present


class TestEdgeCases:
    """Tests for edge cases in truncation."""

    def test_very_narrow_width(self) -> None:
        """Very narrow width still shows autoplay state."""
        result = build_status_content(False, Path("/x.platy"), False, 20)
        assert "[autoplay: off]" in result

    def test_no_playlist_not_truncated_when_fits(self) -> None:
        """'no playlist file loaded' shown when fits."""
        result = build_status_content(False, None, False, 50)
        assert "no playlist file loaded" in result
