#!/usr/bin/env python3
"""Unit tests for format_file_size function."""

import pytest

from platyplaty.ui.size_format import format_file_size


class TestFormatFileSizeBytes:
    """Tests for sizes < 1024 bytes (TASK-3000)."""

    def test_zero_bytes(self) -> None:
        """Zero bytes returns '0 B'."""
        assert format_file_size(0) == "0 B"

    def test_one_byte(self) -> None:
        """One byte returns '1 B'."""
        assert format_file_size(1) == "1 B"

    def test_512_bytes(self) -> None:
        """512 bytes returns '512 B'."""
        assert format_file_size(512) == "512 B"

    def test_1023_bytes(self) -> None:
        """1023 bytes returns '1023 B'."""
        assert format_file_size(1023) == "1023 B"


class TestFormatFileSizeKilobytes:
    """Tests for K unit (TASK-3100)."""

    def test_exactly_1024_bytes(self) -> None:
        """Exactly 1024 bytes returns '1 K'."""
        assert format_file_size(1024) == "1 K"

    def test_1536_bytes(self) -> None:
        """1536 bytes (1.5 K) returns '1.5 K'."""
        assert format_file_size(1536) == "1.5 K"


class TestFormatFileSizeBoundaries:
    """Tests for K/M/G/T boundaries and rounding (TASK-3200)."""

    def test_megabyte_boundary(self) -> None:
        """Exactly 1 MiB returns '1 M'."""
        assert format_file_size(1024**2) == "1 M"

    def test_gigabyte_boundary(self) -> None:
        """Exactly 1 GiB returns '1 G'."""
        assert format_file_size(1024**3) == "1 G"

    def test_terabyte_boundary(self) -> None:
        """Exactly 1 TiB returns '1 T'."""
        assert format_file_size(1024**4) == "1 T"

    def test_rounding_down(self) -> None:
        """2.984 K rounds to '2.98 K'."""
        # 2.984 * 1024 = 3055.616
        assert format_file_size(3056) == "2.98 K"

    def test_rounding_up(self) -> None:
        """2.985 K rounds to '2.99 K'."""
        # 2.985 * 1024 = 3056.64
        assert format_file_size(3057) == "2.99 K"


class TestFormatFileSizeTrailingZeros:
    """Tests for trailing zero removal (TASK-3300)."""

    def test_no_trailing_zeros(self) -> None:
        """Whole numbers have no decimal point."""
        assert format_file_size(2048) == "2 K"

    def test_single_decimal(self) -> None:
        """Single decimal preserved when needed."""
        assert format_file_size(1536) == "1.5 K"

    def test_two_decimals(self) -> None:
        """Two decimals preserved when needed."""
        # 1.25 * 1024 = 1280
        assert format_file_size(1280) == "1.25 K"
