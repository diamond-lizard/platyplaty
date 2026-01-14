#!/usr/bin/env python3
"""Unit tests for truncate_file_with_indicator edge cases."""


from platyplaty.ui.truncation_indicator import truncate_file_with_indicator


class TestMinimumFileNoExtension:
    """Minimum file display without extension: v~ + space + size (TASK-04900)."""

    def test_minimum_no_extension(self) -> None:
        """Minimum file without extension is v~ + space + size."""
        # min_name=2 (v~), space=1, size="512 B"=5, total=8
        result = truncate_file_with_indicator("verylongname", "512 B", 8)
        assert result == "v~ 512 B"
        assert len(result) == 8

    def test_minimum_no_ext_short_size(self) -> None:
        """Minimum file without extension, shorter size."""
        # min_name=2, space=1, size="1 K"=3, total=6
        result = truncate_file_with_indicator("Makefile", "1 K", 6)
        assert result == "M~ 1 K"
        assert len(result) == 6


class TestEdgeCasesWidthBelowMinimum:
    """Edge cases: width < minimum drops indicator (TASK-05000)."""

    def test_width_below_min_with_ext(self) -> None:
        """Width below minimum for ext file drops indicator."""
        # min for ext with "1.5 K": 3 + 1 + 5 = 9
        # width=8 < 9, so drop indicator
        result = truncate_file_with_indicator("verylongname.milk", "1.5 K", 8)
        # Should just be truncated name, no indicator
        assert "1.5 K" not in result
        assert len(result) == 8

    def test_width_below_min_no_ext(self) -> None:
        """Width below minimum for no-ext file drops indicator."""
        # min for no-ext with "512 B": 2 + 1 + 5 = 8
        # width=7 < 8, so drop indicator
        result = truncate_file_with_indicator("Makefile", "512 B", 7)
        assert "512 B" not in result
        assert len(result) == 7

    def test_width_two(self) -> None:
        """Width 2 returns first char + tilde."""
        result = truncate_file_with_indicator("file.txt", "1.5 K", 2)
        assert result == "f~"

    def test_width_one(self) -> None:
        """Width 1 returns first char."""
        result = truncate_file_with_indicator("file.txt", "1.5 K", 1)
        assert result == "f"

    def test_width_zero(self) -> None:
        """Width 0 returns empty string."""
        result = truncate_file_with_indicator("file.txt", "1.5 K", 0)
        assert result == ""
