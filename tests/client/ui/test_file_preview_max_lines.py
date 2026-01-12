#!/usr/bin/env python3
"""Tests for file preview max lines limit (TASK-2510)."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.file_browser_file_utils import read_file_preview_lines


class TestFilePreviewMaxLines:
    """Tests for file preview reading only requested number of lines."""

    def test_read_all_lines_when_no_limit(self) -> None:
        """Without max_lines, all lines are read."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".milk", delete=False) as f:
            f.write("line1\nline2\nline3\nline4\nline5\n")
            f.flush()
            path = Path(f.name)
        try:
            lines = read_file_preview_lines(path)
            assert lines is not None
            assert len(lines) == 5
        finally:
            path.unlink()

    def test_read_limited_lines(self) -> None:
        """With max_lines=3, only 3 lines are read."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".milk", delete=False) as f:
            f.write("line1\nline2\nline3\nline4\nline5\n")
            f.flush()
            path = Path(f.name)
        try:
            lines = read_file_preview_lines(path, max_lines=3)
            assert lines is not None
            assert len(lines) == 3
            assert lines == ("line1", "line2", "line3")
        finally:
            path.unlink()

    def test_read_fewer_lines_than_limit(self) -> None:
        """If file has fewer lines than max_lines, return all lines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".milk", delete=False) as f:
            f.write("line1\nline2\n")
            f.flush()
            path = Path(f.name)
        try:
            lines = read_file_preview_lines(path, max_lines=10)
            assert lines is not None
            assert len(lines) == 2
        finally:
            path.unlink()

    def test_lines_are_stripped_of_newlines(self) -> None:
        """Lines are stripped of trailing newlines."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".milk", delete=False) as f:
            f.write("line1\r\nline2\n")
            f.flush()
            path = Path(f.name)
        try:
            lines = read_file_preview_lines(path)
            assert lines is not None
            assert lines[0] == "line1"
            assert lines[1] == "line2"
        finally:
            path.unlink()
