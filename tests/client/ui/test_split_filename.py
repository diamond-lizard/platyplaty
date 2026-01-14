#!/usr/bin/env python3
"""Unit tests for split_filename helper function."""

from platyplaty.ui.truncation import split_filename


class TestSplitFilename:
    """Tests for split_filename helper."""

    def test_normal_file(self) -> None:
        """Normal file with extension."""
        assert split_filename("file.txt") == ("file", ".txt")

    def test_milk_file(self) -> None:
        """Milk preset file."""
        assert split_filename("cool-preset.milk") == ("cool-preset", ".milk")

    def test_no_extension(self) -> None:
        """File without extension."""
        assert split_filename("noext") == ("noext", "")

    def test_hidden_file(self) -> None:
        """Hidden file (dot at start)."""
        assert split_filename(".hidden") == (".hidden", "")

    def test_multiple_dots(self) -> None:
        """File with multiple dots."""
        assert split_filename("file.tar.gz") == ("file.tar", ".gz")
