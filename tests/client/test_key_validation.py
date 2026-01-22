#!/usr/bin/env python3
"""Tests for key validation functions."""

import pytest

from platyplaty.types.keys import is_valid_key_name


class TestIsValidKeyName:
    """Tests for is_valid_key_name function."""

    def test_lowercase_letters_valid(self) -> None:
        """Lowercase letters a-z should be valid."""
        for letter in "abcdefghijklmnopqrstuvwxyz":
            assert is_valid_key_name(letter)

    def test_uppercase_letters_valid(self) -> None:
        """Uppercase letters A-Z should be valid."""
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert is_valid_key_name(letter)

    def test_uppercase_j_and_k_valid(self) -> None:
        """Uppercase J and K should be valid (Shift+j/k in Textual)."""
        assert is_valid_key_name("J")
        assert is_valid_key_name("K")

    def test_digits_valid(self) -> None:
        """Digits 0-9 should be valid."""
        for digit in "0123456789":
            assert is_valid_key_name(digit)

    def test_special_keys_valid(self) -> None:
        """Common special keys should be valid."""
        special_keys = ["escape", "enter", "tab", "space", "up", "down"]
        for key in special_keys:
            assert is_valid_key_name(key)

    def test_modified_keys_valid(self) -> None:
        """Keys with modifiers should be valid."""
        assert is_valid_key_name("ctrl+j")
        assert is_valid_key_name("shift+enter")
        assert is_valid_key_name("alt+up")

    def test_invalid_key_names(self) -> None:
        """Invalid key names should return False."""
        assert not is_valid_key_name("foo")
        assert not is_valid_key_name("bar")
        assert not is_valid_key_name("unknown")
