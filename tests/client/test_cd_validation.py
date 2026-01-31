#!/usr/bin/env python3
"""Unit tests for cd path validation functions."""

import sys
import os
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd_validation import validate_cd_path


class TestValidateCdPath:
    """Tests for validate_cd_path function."""

    def test_valid_directory_returns_none(self, tmp_path: Path) -> None:
        """Valid directory returns None."""
        assert validate_cd_path(tmp_path) is None

    def test_nonexistent_path_returns_error(self, tmp_path: Path) -> None:
        """Non-existent path returns ERR-100 format error."""
        nonexistent = tmp_path / "does_not_exist"
        result = validate_cd_path(nonexistent)
        assert result is not None
        assert "no such directory:" in result
        assert str(nonexistent) in result

    def test_regular_file_returns_error(self, tmp_path: Path) -> None:
        """Regular file returns ERR-200 format error."""
        file_path = tmp_path / "testfile.txt"
        file_path.write_text("content")
        result = validate_cd_path(file_path)
        assert result is not None
        assert "not a directory:" in result
        assert str(file_path) in result

    def test_broken_symlink_returns_error(self, tmp_path: Path) -> None:
        """Broken symlink returns ERR-400 format error."""
        target = tmp_path / "nonexistent_target"
        link = tmp_path / "broken_link"
        link.symlink_to(target)
        result = validate_cd_path(link)
        assert result is not None
        assert "broken symlink:" in result
        assert str(link) in result

    def test_symlink_to_file_returns_error(self, tmp_path: Path) -> None:
        """Symlink to file returns ERR-200 format error."""
        file_path = tmp_path / "target_file.txt"
        file_path.write_text("content")
        link = tmp_path / "link_to_file"
        link.symlink_to(file_path)
        result = validate_cd_path(link)
        assert result is not None
        assert "not a directory:" in result
        assert str(link) in result

    def test_symlink_to_directory_returns_none(self, tmp_path: Path) -> None:
        """Symlink to directory returns None (valid)."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        link = tmp_path / "link_to_dir"
        link.symlink_to(target_dir)
        assert validate_cd_path(link) is None

    @pytest.mark.skipif(
        sys.platform == "win32" or os.getuid() == 0,
        reason="Permission test not valid on Windows or as root",
    )
    def test_permission_denied_returns_error(self, tmp_path: Path) -> None:
        """Directory without read permission returns ERR-300 format error."""
        no_access = tmp_path / "no_access"
        no_access.mkdir()
        original_mode = no_access.stat().st_mode
        try:
            os.chmod(no_access, 0o000)
            result = validate_cd_path(no_access)
            assert result is not None
            assert "permission denied:" in result
            assert str(no_access) in result
        finally:
            os.chmod(no_access, original_mode)
