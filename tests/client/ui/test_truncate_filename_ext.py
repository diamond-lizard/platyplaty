#!/usr/bin/env python3
"""Unit tests for truncate_filename_with_extension."""


from platyplaty.ui.truncation_filename import truncate_filename_with_extension


class TestTruncateFilenameStage1:
    """Stage 1: If name + ext fits, return as-is."""

    def test_fits_exactly(self) -> None:
        """Name + ext fits exactly in width."""
        assert truncate_filename_with_extension("file", ".txt", 8) == "file.txt"

    def test_fits_with_room(self) -> None:
        """Name + ext fits with room to spare."""
        assert truncate_filename_with_extension("hi", ".txt", 10) == "hi.txt"


class TestTruncateFilenameStage2:
    """Stage 2-3: Truncate base name, keep extension."""

    def test_truncate_base_keep_ext(self) -> None:
        """Truncate base, add tilde before extension."""
        # "very-long-preset.milk" = 21 chars, width=15
        # Need: truncated_base + "~" + ".milk"
        # Available for base: 15 - 1 - 5 = 9 chars, resulting in "very-long"
        assert truncate_filename_with_extension(
            "very-long-preset", ".milk", 15
        ) == "very-long~.milk"

    def test_minimum_base_one_char(self) -> None:
        """Base truncated to minimum 1 char + tilde."""
        # "v~.milk" = 7 chars
        assert truncate_filename_with_extension("verylongname", ".milk", 7) == "v~.milk"


class TestTruncateFilenameStage4:
    """Stage 4: Truncate extension with tilde."""

    def test_truncate_extension_one(self) -> None:
        """Extension truncated, v~.mi~."""
        # Width 6: v~ + .mi + ~ = 6
        assert truncate_filename_with_extension("verylongname", ".milk", 6) == "v~.mi~"

    def test_truncate_extension_more(self) -> None:
        """Extension truncated more, v~.m~."""
        assert truncate_filename_with_extension("verylongname", ".milk", 5) == "v~.m~"

    def test_truncate_extension_minimal(self) -> None:
        """Extension truncated to minimum, v~.~."""
        assert truncate_filename_with_extension("verylongname", ".milk", 4) == "v~.~"


class TestTruncateFilenameStage5:
    """Stage 5: Absolute minimum 3 chars (v~~)."""

    def test_absolute_minimum(self) -> None:
        """Absolute minimum is 3 chars: v~~."""
        assert truncate_filename_with_extension("verylongname", ".milk", 3) == "v~~"

    def test_minimum_with_short_name(self) -> None:
        """Minimum with short name."""
        assert truncate_filename_with_extension("a", ".milk", 3) == "a~~"


class TestTruncateFilenameEdgeCases:
    """Edge cases: width < 3 (TASK-01800)."""

    def test_width_two(self) -> None:
        """Width 2 returns first char + tilde."""
        assert truncate_filename_with_extension("file", ".txt", 2) == "f~"

    def test_width_one(self) -> None:
        """Width 1 returns first char."""
        assert truncate_filename_with_extension("file", ".txt", 1) == "f"

    def test_width_zero(self) -> None:
        """Width 0 returns empty string."""
        assert truncate_filename_with_extension("file", ".txt", 0) == ""

    def test_width_negative(self) -> None:
        """Negative width returns empty string."""
        assert truncate_filename_with_extension("file", ".txt", -1) == ""

    def test_empty_name_width_one(self) -> None:
        """Empty name, width 1 returns first char of ext."""
        assert truncate_filename_with_extension("", ".txt", 1) == "."

    def test_both_empty_width_one(self) -> None:
        """Both empty, width 1 returns tilde."""
        assert truncate_filename_with_extension("", "", 1) == "~"
