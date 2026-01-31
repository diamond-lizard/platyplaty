#!/usr/bin/env python3
"""Additional unit tests for expand_cd_path function."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd_path_expand import expand_cd_path


class TestExpandCdPathExtra:
    """Additional tests for expand_cd_path function."""

    def test_whitespace_trimmed(self) -> None:
        """Leading/trailing whitespace is trimmed."""
        result, error = expand_cd_path("  /path/to/dir  ", Path("/base"))
        assert error is None
        assert result == Path("/path/to/dir")

    def test_internal_spaces_preserved(self) -> None:
        """Path with internal spaces is preserved."""
        result, error = expand_cd_path("/path/to/my directory", Path("/base"))
        assert error is None
        assert result == Path("/path/to/my directory")

    def test_defined_env_var_expands(self, monkeypatch) -> None:
        """Path with defined environment variable expands correctly."""
        monkeypatch.setenv("TEST_DIR", "/test/value")
        result, error = expand_cd_path("$TEST_DIR/subdir", Path("/base"))
        assert error is None
        assert result == Path("/test/value/subdir")

    def test_nonexistent_user_error(self) -> None:
        """~nonexistentuser returns ERR-700 format error."""
        result, error = expand_cd_path("~zzz_no_such_user_12345", Path("/base"))
        assert result is None
        assert error == "Error: cd: no such user: 'zzz_no_such_user_12345'"

    def test_tilde_user_expands(self, monkeypatch) -> None:
        """~$USER expands correctly when USER is a valid username."""
        import pwd
        current_user = pwd.getpwuid(os.getuid()).pw_name
        monkeypatch.setenv("USER", current_user)
        result, error = expand_cd_path("~$USER", Path("/base"))
        assert error is None
        expected_home = Path(pwd.getpwnam(current_user).pw_dir)
        assert result == expected_home

    def test_dot_dotdot_normalized(self) -> None:
        """Path with . and .. components is normalized."""
        result, error = expand_cd_path("/foo/../bar/./baz", Path("/base"))
        assert error is None
        assert result == Path("/bar/baz")

    def test_relative_dot_dotdot_normalized(self) -> None:
        """Relative path with .. is normalized."""
        result, error = expand_cd_path("foo/../bar", Path("/base"))
        assert error is None
        assert result == Path("/base/bar")
