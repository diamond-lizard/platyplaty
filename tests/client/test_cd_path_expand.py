#!/usr/bin/env python3
"""Unit tests for cd path expansion functions."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd_path_expand import (
    find_undefined_variables,
    find_empty_variables,
    expand_cd_path,
)


class TestFindUndefinedVariables:
    """Tests for find_undefined_variables function."""

    def test_no_variables_returns_empty(self) -> None:
        """Path with no variables returns empty list."""
        assert find_undefined_variables("/home/user/presets") == []

    def test_defined_variable_returns_empty(self, monkeypatch) -> None:
        """Path with defined variable returns empty list."""
        monkeypatch.setenv("MY_VAR", "/some/path")
        assert find_undefined_variables("$MY_VAR/subdir") == []

    def test_undefined_bare_var_returns_name(self, monkeypatch) -> None:
        """Path with undefined $VAR returns variable name."""
        monkeypatch.delenv("UNDEFINED_VAR_XYZ", raising=False)
        assert find_undefined_variables("$UNDEFINED_VAR_XYZ/path") == ["UNDEFINED_VAR_XYZ"]

    def test_undefined_braced_var_returns_name(self, monkeypatch) -> None:
        """Path with undefined ${VAR} returns variable name."""
        monkeypatch.delenv("UNDEFINED_VAR_ABC", raising=False)
        assert find_undefined_variables("${UNDEFINED_VAR_ABC}/path") == ["UNDEFINED_VAR_ABC"]

    def test_multiple_undefined_returns_all(self, monkeypatch) -> None:
        """Path with multiple undefined variables returns all names."""
        monkeypatch.delenv("UNDEF_A", raising=False)
        monkeypatch.delenv("UNDEF_B", raising=False)
        result = find_undefined_variables("$UNDEF_A/${UNDEF_B}")
        assert set(result) == {"UNDEF_A", "UNDEF_B"}

    def test_mixed_defined_undefined_returns_only_undefined(self, monkeypatch) -> None:
        """Path with mix of defined and undefined returns only undefined."""
        monkeypatch.setenv("DEFINED_VAR", "/path")
        monkeypatch.delenv("UNDEF_VAR", raising=False)
        result = find_undefined_variables("$DEFINED_VAR/$UNDEF_VAR")
        assert result == ["UNDEF_VAR"]


class TestFindEmptyVariables:
    """Tests for find_empty_variables function."""

    def test_no_variables_returns_empty(self) -> None:
        """Path with no variables returns empty list."""
        assert find_empty_variables("/home/user/presets") == []

    def test_nonempty_variable_returns_empty(self, monkeypatch) -> None:
        """Path with non-empty variable returns empty list."""
        monkeypatch.setenv("NONEMPTY_VAR", "/some/path")
        assert find_empty_variables("$NONEMPTY_VAR/subdir") == []

    def test_empty_variable_returns_name(self, monkeypatch) -> None:
        """Path with empty variable returns that variable name."""
        monkeypatch.setenv("EMPTY_VAR", "")
        assert find_empty_variables("$EMPTY_VAR/path") == ["EMPTY_VAR"]

    def test_undefined_not_returned(self, monkeypatch) -> None:
        """Undefined variables are NOT returned (only defined-but-empty)."""
        monkeypatch.delenv("UNDEFINED_VAR_ZZZ", raising=False)
        assert find_empty_variables("$UNDEFINED_VAR_ZZZ/path") == []
