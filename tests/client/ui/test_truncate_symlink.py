#!/usr/bin/env python3
"""Unit tests for truncate_symlink (TASK-07900)."""


from platyplaty.ui.truncation_indicator import truncate_symlink


class TestSymlinkFits:
    """Symlink name + space + indicator fits within width."""

    def test_fits_exactly(self) -> None:
        """Name + space + indicator fits exactly in width."""
        # "favorites" (9) + " " (1) + "-> 42" (5) = 15
        result = truncate_symlink("favorites", "-> 42", 15)
        assert result == "favorites -> 42"
        assert len(result) == 15

    def test_fits_with_padding(self) -> None:
        """Name + indicator fits with extra padding."""
        # "abc" (3) + padding + "-> 5" (4) = 20
        result = truncate_symlink("abc", "-> 5", 20)
        assert result == "abc             -> 5"
        assert len(result) == 20
        assert result.endswith("-> 5")


class TestSymlinkTruncation:
    """Symlink name truncated, indicator preserved."""

    def test_truncate_name_preserve_indicator(self) -> None:
        """Truncate symlink name, preserve indicator."""
        # "verylongfavorites" = 17, "-> 42" = 5, width=15
        # Available for name: 15 - 1 - 5 = 9
        result = truncate_symlink("verylongfavorites", "-> 42", 15)
        assert result.endswith("-> 42")
        assert len(result) == 15
        assert "~" in result

    def test_truncate_more_aggressively(self) -> None:
        """More aggressive truncation when width is smaller."""
        # width=12, indicator="-> 1.5 K" (8)
        # Available for name: 12 - 1 - 8 = 3
        result = truncate_symlink("verylongname", "-> 1.5 K", 12)
        assert result.endswith("-> 1.5 K")
        assert len(result) == 12


class TestSymlinkToFile:
    """Symlink to file with size indicator (-> 1.5 K format)."""

    def test_symlink_to_file_fits(self) -> None:
        """Symlink to file indicator format fits."""
        result = truncate_symlink("link.milk", "-> 1.5 K", 20)
        assert result.endswith("-> 1.5 K")
        assert "link.milk" in result

    def test_symlink_to_file_truncated(self) -> None:
        """Symlink to file with truncated name."""
        # "very-long-link.milk" = 19, "-> 512 B" = 8, width=15
        # Available for name: 15 - 1 - 8 = 6
        result = truncate_symlink("very-long-link.milk", "-> 512 B", 15)
        assert result.endswith("-> 512 B")
        assert len(result) == 15
