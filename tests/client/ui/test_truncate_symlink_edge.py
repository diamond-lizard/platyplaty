#!/usr/bin/env python3
"""Unit tests for truncate_symlink with width < minimum (TASK-08200)."""


from platyplaty.ui.truncation_indicator import truncate_symlink


class TestSymlinkWidthBelowMinimum:
    """Width < minimum drops indicator and clamps name."""

    def test_width_below_minimum_drops_indicator(self) -> None:
        """Width below minimum drops indicator entirely."""
        # min_width = 2 (v~) + 1 (space) + 5 (-> 42) = 8
        # width=7 is below minimum, so drop indicator
        result = truncate_symlink("favorites", "-> 42", 7)
        assert "-> 42" not in result
        assert len(result) == 7
        assert result == "favori~"

    def test_width_just_below_minimum(self) -> None:
        """Width just below minimum still drops indicator."""
        # min_width = 2 + 1 + 6 (-> 1 K) = 9
        # width=8 drops indicator
        result = truncate_symlink("mylinkname", "-> 1 K", 8)
        assert "->" not in result
        assert len(result) == 8

    def test_width_3_clamps_to_name(self) -> None:
        """Width=3 returns truncated name."""
        result = truncate_symlink("favorites", "-> 42", 3)
        assert result == "fa~"
        assert len(result) == 3

    def test_width_2_returns_minimum_name(self) -> None:
        """Width=2 returns first char + tilde."""
        result = truncate_symlink("favorites", "-> 42", 2)
        assert result == "f~"
        assert len(result) == 2

    def test_width_1_returns_first_char(self) -> None:
        """Width=1 returns just first char."""
        result = truncate_symlink("favorites", "-> 42", 1)
        assert result == "f"
        assert len(result) == 1

    def test_width_0_returns_empty(self) -> None:
        """Width=0 returns empty string."""
        result = truncate_symlink("favorites", "-> 42", 0)
        assert result == ""
        assert len(result) == 0
