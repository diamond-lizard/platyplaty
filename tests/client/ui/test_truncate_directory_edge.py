#!/usr/bin/env python3
"""Unit tests for truncate_directory edge cases (TASK-06500)."""


from platyplaty.ui.truncation_indicator import truncate_directory


class TestEdgeCasesWidthBelowMinimum:
    """Edge cases: width < minimum drops count indicator."""

    def test_width_below_min_two_digit_count(self) -> None:
        """Width below minimum drops count indicator."""
        # min for count "42": 2 + 1 + 2 = 5
        # width=4 < 5, so drop indicator
        result = truncate_directory("verylongname", 42, 4)
        # Should just be truncated name, no count
        assert "42" not in result
        assert len(result) == 4

    def test_width_below_min_large_count(self) -> None:
        """Width below minimum for large count drops indicator."""
        # min for count "1234": 2 + 1 + 4 = 7
        # width=6 < 7, so drop indicator
        result = truncate_directory("verylongname", 1234, 6)
        assert "1234" not in result
        assert len(result) == 6

    def test_width_two(self) -> None:
        """Width 2 returns first char + tilde."""
        result = truncate_directory("presets", 42, 2)
        assert result == "p~"

    def test_width_one(self) -> None:
        """Width 1 returns first char."""
        result = truncate_directory("presets", 42, 1)
        assert result == "p"

    def test_width_zero(self) -> None:
        """Width 0 returns empty string."""
        result = truncate_directory("presets", 42, 0)
        assert result == ""

    def test_zero_count(self) -> None:
        """Directory with count of 0."""
        # "empty" (5) + " " (1) + "0" (1) = 7
        result = truncate_directory("empty", 0, 10)
        assert result.endswith("0")
        assert len(result) == 10
