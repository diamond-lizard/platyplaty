#!/usr/bin/env python3
"""Unit tests for truncate_file_with_indicator."""


from platyplaty.ui.truncation_indicator import truncate_file_with_indicator


class TestFileWithIndicatorFits:
    """File name + space + size fits within width."""

    def test_fits_exactly(self) -> None:
        """Name + space + size fits exactly in width."""
        # "cool.milk" (9) + " " (1) + "1.5 K" (5) = 15
        result = truncate_file_with_indicator("cool.milk", "1.5 K", 15)
        assert result == "cool.milk 1.5 K"
        assert len(result) == 15

    def test_fits_with_padding(self) -> None:
        """Name + size fits with extra padding."""
        # "a.milk" (6) + padding + "1 K" (3) = 20
        result = truncate_file_with_indicator("a.milk", "1 K", 20)
        assert result == "a.milk           1 K"
        assert len(result) == 20
        assert result.endswith("1 K")


class TestFileWithIndicatorTruncation:
    """File name truncated, size indicator preserved."""

    def test_truncate_base_preserve_indicator(self) -> None:
        """Truncate file base, preserve extension and indicator."""
        # "very-long-preset.milk" = 21, "1.5 K" = 5, width=25
        # Available for name: 25 - 1 - 5 = 19
        result = truncate_file_with_indicator("very-long-preset.milk", "1.5 K", 25)
        assert result.endswith("1.5 K")
        assert len(result) == 25
        # Name should be truncated to 19 chars: "very-long-pres~.milk"
        assert "~.milk" in result

    def test_truncate_more_aggressively(self) -> None:
        """More aggressive truncation when width is smaller."""
        # width=15, size="1.5 K" (5)
        # Available for name: 15 - 1 - 5 = 9
        result = truncate_file_with_indicator("verylongname.milk", "1.5 K", 15)
        assert result.endswith("1.5 K")
        assert len(result) == 15


class TestMinimumFileWithExtension:
    """Minimum file display with extension: v~~ + space + size (TASK-04800)."""

    def test_minimum_with_extension(self) -> None:
        """Minimum file with extension is v~~ + space + size."""
        # min_name=3 (v~~), space=1, size="1.5 K"=5, total=9
        result = truncate_file_with_indicator("verylongname.milk", "1.5 K", 9)
        assert result == "v~~ 1.5 K"
        assert len(result) == 9

    def test_minimum_short_size(self) -> None:
        """Minimum file with shorter size string."""
        # min_name=3, space=1, size="0 B"=3, total=7
        result = truncate_file_with_indicator("verylongname.milk", "0 B", 7)
        assert result == "v~~ 0 B"
        assert len(result) == 7

