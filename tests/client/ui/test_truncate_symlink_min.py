#!/usr/bin/env python3
"""Unit tests for minimum symlink display (TASK-08000)."""


from platyplaty.ui.truncation_indicator import truncate_symlink


class TestMinimumSymlinkDisplay:
    """Minimum symlink display: v~ + space + indicator (TASK-08000)."""

    def test_minimum_display_dir(self) -> None:
        """Minimum symlink to directory is v~ + space + indicator."""
        # min_name=2 (v~), space=1, indicator="-> 42"=5, total=8
        result = truncate_symlink("verylongname", "-> 42", 8)
        assert result == "v~ -> 42"
        assert len(result) == 8

    def test_minimum_display_file(self) -> None:
        """Minimum symlink to file is v~ + space + indicator."""
        # min_name=2, space=1, indicator="-> 1 K"=6, total=9
        result = truncate_symlink("verylongname", "-> 1 K", 9)
        assert result == "v~ -> 1 K"
        assert len(result) == 9

    def test_minimum_with_larger_size(self) -> None:
        """Minimum symlink with larger size indicator."""
        # min_name=2, space=1, indicator="-> 15.5 M"=9, total=12
        result = truncate_symlink("verylongname", "-> 15.5 M", 12)
        assert result == "v~ -> 15.5 M"
        assert len(result) == 12

    def test_minimum_single_digit_count(self) -> None:
        """Minimum symlink with single digit count."""
        # min_name=2, space=1, indicator="-> 5"=4, total=7
        result = truncate_symlink("verylongname", "-> 5", 7)
        assert result == "v~ -> 5"
        assert len(result) == 7

    def test_minimum_large_count(self) -> None:
        """Minimum symlink with large count."""
        # min_name=2, space=1, indicator="-> 1234"=7, total=10
        result = truncate_symlink("verylongname", "-> 1234", 10)
        assert result == "v~ -> 1234"
        assert len(result) == 10
