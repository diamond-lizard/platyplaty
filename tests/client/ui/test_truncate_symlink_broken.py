#!/usr/bin/env python3
"""Unit tests for broken symlink preserves size indicator (TASK-08100)."""


from platyplaty.ui.truncation_indicator import truncate_symlink


class TestBrokenSymlinkSizeIndicator:
    """Broken symlink preserves size indicator (-> XX B format)."""

    def test_broken_symlink_fits(self) -> None:
        """Broken symlink with size indicator fits."""
        # "dead-link.milk" (14) + " " (1) + "-> 15 B" (7) = 22
        result = truncate_symlink("dead-link.milk", "-> 15 B", 22)
        assert result == "dead-link.milk -> 15 B"
        assert len(result) == 22

    def test_broken_symlink_truncated(self) -> None:
        """Broken symlink with truncated name preserves indicator."""
        # "dead-link.milk" = 14, "-> 15 B" = 7, width=15
        # Available for name: 15 - 1 - 7 = 7
        result = truncate_symlink("dead-link.milk", "-> 15 B", 15)
        assert result.endswith("-> 15 B")
        assert len(result) == 15
        assert "~" in result

    def test_broken_symlink_minimum(self) -> None:
        """Broken symlink at minimum display."""
        # min_name=2, space=1, indicator="-> 15 B"=7, total=10
        result = truncate_symlink("dead-link.milk", "-> 15 B", 10)
        assert result == "d~ -> 15 B"
        assert len(result) == 10

    def test_broken_symlink_small_size(self) -> None:
        """Broken symlink with small size (single byte)."""
        # min_name=2, space=1, indicator="-> 0 B"=6, total=9
        result = truncate_symlink("broken", "-> 0 B", 9)
        assert result == "b~ -> 0 B"
        assert len(result) == 9

    def test_broken_symlink_larger_size(self) -> None:
        """Broken symlink with larger size."""
        # "broken-link" (11) + padding + "-> 512 B" (8) = 20
        result = truncate_symlink("broken-link", "-> 512 B", 20)
        assert result == "broken-link -> 512 B"
        assert len(result) == 20
