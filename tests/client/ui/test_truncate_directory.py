#!/usr/bin/env python3
"""Unit tests for truncate_directory."""


from platyplaty.ui.truncation_indicator import truncate_directory


class TestDirectoryFits:
    """Directory name + space + count fits within width."""

    def test_fits_exactly(self) -> None:
        """Name + space + count fits exactly in width."""
        # "presets" (7) + " " (1) + "42" (2) = 10
        result = truncate_directory("presets", 42, 10)
        assert result == "presets 42"
        assert len(result) == 10

    def test_fits_with_padding(self) -> None:
        """Name + count fits with extra padding."""
        # "abc" (3) + padding + "5" (1) = 15
        result = truncate_directory("abc", 5, 15)
        assert result == "abc           5"
        assert len(result) == 15
        assert result.endswith("5")


class TestDirectoryTruncation:
    """Directory name truncated, count indicator preserved."""

    def test_truncate_name_preserve_count(self) -> None:
        """Truncate directory name, preserve count."""
        # "verylongpresets" = 15, "42" = 2, width=12
        # Available for name: 12 - 1 - 2 = 9
        result = truncate_directory("verylongpresets", 42, 12)
        assert result.endswith("42")
        assert len(result) == 12
        assert "~" in result

    def test_truncate_more_aggressively(self) -> None:
        """More aggressive truncation when width is smaller."""
        # width=8, count="123" (3)
        # Available for name: 8 - 1 - 3 = 4
        result = truncate_directory("verylongname", 123, 8)
        assert result.endswith("123")
        assert len(result) == 8


class TestMinimumDirectoryDisplay:
    """Minimum directory display: v~ + space + count (TASK-06400)."""

    def test_minimum_display(self) -> None:
        """Minimum directory is v~ + space + count."""
        # min_name=2 (v~), space=1, count="42"=2, total=5
        result = truncate_directory("verylongname", 42, 5)
        assert result == "v~ 42"
        assert len(result) == 5

    def test_minimum_single_digit_count(self) -> None:
        """Minimum directory with single digit count."""
        # min_name=2, space=1, count="5"=1, total=4
        result = truncate_directory("verylongname", 5, 4)
        assert result == "v~ 5"
        assert len(result) == 4

    def test_minimum_large_count(self) -> None:
        """Minimum directory with large count."""
        # min_name=2, space=1, count="1234"=4, total=7
        result = truncate_directory("verylongname", 1234, 7)
        assert result == "v~ 1234"
        assert len(result) == 7
