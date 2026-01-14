#!/usr/bin/env python3
"""Unit tests for truncate_filename_no_extension."""


from platyplaty.ui.truncation import truncate_filename_no_extension


class TestTruncateFilenameNoExtFits:
    """Test cases where name fits within width."""

    def test_fits_exactly(self) -> None:
        """Name fits exactly in width."""
        assert truncate_filename_no_extension("longname", 8) == "longname"

    def test_fits_with_room(self) -> None:
        """Name fits with room to spare."""
        assert truncate_filename_no_extension("hi", 10) == "hi"

    def test_empty_name(self) -> None:
        """Empty name returns empty string."""
        assert truncate_filename_no_extension("", 10) == ""


class TestTruncateFilenameNoExtTruncation:
    """Test cases where name needs truncation."""

    def test_truncate_with_tilde(self) -> None:
        """Name truncated with tilde."""
        # "verylongname" = 12 chars, width=8
        # Result: 7 chars + tilde = "verylo~" + "~" = "verylon~"
        assert truncate_filename_no_extension("verylongname", 8) == "verylon~"

    def test_truncate_to_three_chars(self) -> None:
        """Truncate to 3 chars: 2 letters + tilde."""
        assert truncate_filename_no_extension("verylongname", 3) == "ve~"


class TestTruncateFilenameNoExtMinimum:
    """Test minimum display: 2 chars (v~) per TASK-03300."""

    def test_minimum_two_chars(self) -> None:
        """Minimum is 2 characters: first letter + tilde."""
        assert truncate_filename_no_extension("verylongname", 2) == "v~"

    def test_short_name_truncated(self) -> None:
        """Short name that still needs truncation."""
        assert truncate_filename_no_extension("ab", 2) == "ab"  # fits exactly

    def test_three_char_name_width_two(self) -> None:
        """Three char name at width 2."""
        assert truncate_filename_no_extension("abc", 2) == "a~"


class TestTruncateFilenameNoExtEdgeCases:
    """Edge cases: width < 2 per TASK-03100."""

    def test_width_one(self) -> None:
        """Width 1 returns first char."""
        assert truncate_filename_no_extension("filename", 1) == "f"

    def test_width_zero(self) -> None:
        """Width 0 returns empty string."""
        assert truncate_filename_no_extension("filename", 0) == ""

    def test_width_negative(self) -> None:
        """Negative width returns empty string."""
        assert truncate_filename_no_extension("filename", -1) == ""

    def test_empty_name_width_one(self) -> None:
        """Empty name, width 1 returns tilde."""
        assert truncate_filename_no_extension("", 1) == "~"

    def test_empty_name_width_zero(self) -> None:
        """Empty name, width 0 returns empty string."""
        assert truncate_filename_no_extension("", 0) == ""
