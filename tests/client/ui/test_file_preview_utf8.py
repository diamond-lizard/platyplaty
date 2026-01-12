#!/usr/bin/env python3
"""Tests for file preview UTF-8 handling (TASK-2520)."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

import pytest
from platyplaty.ui.file_browser_file_utils import read_file_preview_lines
from platyplaty.ui.file_browser_types import BinaryFileError

from contextlib import contextmanager


@contextmanager
def temp_file_with_content(content: bytes):
    """Create a temp file with content, yield path, then cleanup."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".milk", delete=False) as f:
        f.write(content)
        f.flush()
        path = Path(f.name)
    try:
        yield path
    finally:
        path.unlink()


class TestFilePreviewUtf8:
    """Tests for file preview strict UTF-8 handling."""

    def test_valid_utf8_file_reads_successfully(self) -> None:
        """Valid UTF-8 file is read without error."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".milk", delete=False) as f:
            f.write("Hello, World!\n".encode("utf-8"))
            f.flush()
            path = Path(f.name)
        try:
            lines = read_file_preview_lines(path)
            assert lines is not None
            assert lines[0] == "Hello, World!"
        finally:
            path.unlink()

    def test_non_utf8_file_raises_binary_file_error(self) -> None:
        """Non-UTF-8 file raises BinaryFileError."""
        content = b"\xff\xfe Invalid UTF-8 bytes"  # Latin-1 encoded
        with temp_file_with_content(content) as path:
            pytest.raises(BinaryFileError, read_file_preview_lines, path)

    def test_binary_file_raises_binary_file_error(self) -> None:
        """Binary file with invalid UTF-8 bytes raises BinaryFileError."""
        content = b"\x80\x81\x82\x83\x84"  # continuation bytes without starter
        with temp_file_with_content(content) as path:
            pytest.raises(BinaryFileError, read_file_preview_lines, path)

    def test_utf8_with_unicode_characters(self) -> None:
        """UTF-8 file with unicode characters is read correctly."""
        content = "Hello \xe4\xb8\x96\xe7\x95\x8c\n".encode("utf-8")  # "Hello 世界"
        with temp_file_with_content(content) as path:
            lines = read_file_preview_lines(path)
            assert lines is not None
            assert "Hello" in lines[0]
