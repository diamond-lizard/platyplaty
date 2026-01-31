#!/usr/bin/env python3
"""Unit tests for expand_cd_path function."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd_path_expand import expand_cd_path


class TestExpandCdPath:
    """Tests for expand_cd_path function."""

    def test_empty_string_returns_home(self) -> None:
        """Empty string returns home directory."""
        result, error = expand_cd_path("", Path("/base"))
        assert error is None
        assert result == Path.home()

    def test_whitespace_only_returns_home(self) -> None:
        """Whitespace-only returns home directory."""
        result, error = expand_cd_path("   ", Path("/base"))
        assert error is None
        assert result == Path.home()

    def test_tilde_returns_home(self) -> None:
        """Tilde alone returns home directory."""
        result, error = expand_cd_path("~", Path("/base"))
        assert error is None
        assert result == Path.home()

    def test_tilde_subdir_expands(self) -> None:
        """~/subdir returns home directory / subdir."""
        result, error = expand_cd_path("~/subdir", Path("/base"))
        assert error is None
        assert result == Path.home() / "subdir"

    def test_absolute_path_returns_unchanged(self) -> None:
        """Absolute path returns that path."""
        result, error = expand_cd_path("/absolute/path", Path("/base"))
        assert error is None
        assert result == Path("/absolute/path")

    def test_relative_path_resolved_from_base(self) -> None:
        """Relative path is resolved from base_dir."""
        result, error = expand_cd_path("relative/path", Path("/base"))
        assert error is None
        assert result == Path("/base/relative/path")

    def test_undefined_variable_singular_error(self, monkeypatch) -> None:
        """Single undefined variable returns singular ERR-500 format error."""
        monkeypatch.delenv("UNDEF_TEST_VAR", raising=False)
        result, error = expand_cd_path("$UNDEF_TEST_VAR/path", Path("/base"))
        assert result is None
        assert error == "Error: cd: undefined variable: '$UNDEF_TEST_VAR'"

    def test_undefined_variable_plural_error(self, monkeypatch) -> None:
        """Multiple undefined variables returns plural ERR-500 format error."""
        monkeypatch.delenv("UNDEF_A", raising=False)
        monkeypatch.delenv("UNDEF_B", raising=False)
        result, error = expand_cd_path("$UNDEF_A/$UNDEF_B", Path("/base"))
        assert result is None
        assert "undefined variables:" in error
        assert "'$UNDEF_A'" in error
        assert "'$UNDEF_B'" in error

    def test_empty_variable_singular_error(self, monkeypatch) -> None:
        """Single empty variable returns singular ERR-600 format error."""
        monkeypatch.setenv("EMPTY_TEST_VAR", "")
        result, error = expand_cd_path("$EMPTY_TEST_VAR/path", Path("/base"))
        assert result is None
        assert error == "Error: cd: empty variable: '$EMPTY_TEST_VAR'"

    def test_empty_variable_plural_error(self, monkeypatch) -> None:
        """Multiple empty variables returns plural ERR-600 format error."""
        monkeypatch.setenv("EMPTY_A", "")
        monkeypatch.setenv("EMPTY_B", "")
        result, error = expand_cd_path("$EMPTY_A/$EMPTY_B", Path("/base"))
        assert result is None
        assert "empty variables:" in error
        assert "'$EMPTY_A'" in error
        assert "'$EMPTY_B'" in error
