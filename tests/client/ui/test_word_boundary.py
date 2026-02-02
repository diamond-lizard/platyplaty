#!/usr/bin/env python3
"""Unit tests for word boundary detection functions."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.word_boundary import (
    find_word_start_backward,
    find_word_end_forward,
    find_unix_word_start_backward,
    find_path_word_start_backward,
)


class TestFindWordStartBackward:
    """Tests for find_word_start_backward function."""

    def test_cursor_at_start_returns_zero(self):
        """Cursor at position 0 returns 0."""
        assert find_word_start_backward("hello", 0) == 0

    def test_cursor_in_middle_of_word(self):
        """Cursor in middle of word returns start of that word."""
        assert find_word_start_backward("hello", 3) == 0

    def test_cursor_after_word_with_spaces(self):
        """Cursor after word with spaces returns start of previous word."""
        assert find_word_start_backward("hello world", 11) == 6

    def test_cursor_after_punctuation(self):
        """Cursor after punctuation returns start of word before punctuation."""
        assert find_word_start_backward("hello-world", 11) == 6

    def test_empty_string_returns_zero(self):
        """Empty string returns 0."""
        assert find_word_start_backward("", 0) == 0

    def test_only_non_alphanumeric_returns_zero(self):
        """String with only non-alphanumeric characters returns 0."""
        assert find_word_start_backward("---", 3) == 0

    def test_multiple_words_correct_boundary(self):
        """Multiple words return correct boundary for each position."""
        text = "foo bar baz"
        assert find_word_start_backward(text, 7) == 4
        assert find_word_start_backward(text, 5) == 4
        assert find_word_start_backward(text, 3) == 0


class TestFindWordEndForward:
    """Tests for find_word_end_forward function."""

    def test_cursor_at_end_returns_length(self):
        """Cursor at end of string returns len(text)."""
        assert find_word_end_forward("hello", 5) == 5

    def test_cursor_at_start_of_word(self):
        """Cursor at start of word returns end of that word."""
        assert find_word_end_forward("hello", 0) == 5

    def test_cursor_before_word_with_spaces(self):
        """Cursor before word with spaces returns end of next word."""
        assert find_word_end_forward("hello world", 5) == 11

    def test_cursor_before_punctuation(self):
        """Cursor before punctuation returns end of word after punctuation."""
        assert find_word_end_forward("hello-world", 5) == 11

    def test_empty_string_returns_zero(self):
        """Empty string returns 0."""
        assert find_word_end_forward("", 0) == 0

    def test_only_non_alphanumeric_returns_length(self):
        """String with only non-alphanumeric characters returns len(text)."""
        assert find_word_end_forward("---", 0) == 3

    def test_multiple_words_correct_boundary(self):
        """Multiple words return correct boundary for each position."""
        text = "foo bar baz"
        assert find_word_end_forward(text, 0) == 3
        assert find_word_end_forward(text, 3) == 7
        assert find_word_end_forward(text, 4) == 7


class TestFindUnixWordStartBackward:
    """Tests for find_unix_word_start_backward function."""

    def test_path_with_slashes(self):
        """Path with slashes treated as single word."""
        text = "xyz foo/bar_baz.milk"
        assert find_unix_word_start_backward(text, 20) == 4

    def test_slashes_hyphens_underscores_dots_in_word(self):
        """Slashes, hyphens, underscores, and dots are all part of word."""
        text = "prefix a-b_c.d/e suffix"
        assert find_unix_word_start_backward(text, 17) == 7

    def test_only_whitespace_is_boundary(self):
        """Only whitespace acts as boundary."""
        text = "hello world"
        assert find_unix_word_start_backward(text, 11) == 6

    def test_empty_string_returns_zero(self):
        """Empty string returns 0."""
        assert find_unix_word_start_backward("", 0) == 0

    def test_cursor_at_zero_returns_zero(self):
        """Cursor at position 0 returns 0."""
        assert find_unix_word_start_backward("hello", 0) == 0


class TestFindPathWordStartBackward:
    """Tests for find_path_word_start_backward function."""

    def test_basic_path_from_end(self):
        """Basic path from end returns start of last component."""
        # /foo/bar/baz from position 12 -> 9 (before 'b' in baz)
        assert find_path_word_start_backward("/foo/bar/baz", 12) == 9

    def test_path_with_trailing_space(self):
        """Path with trailing space absorbs the space."""
        # /foo/bar/baz  from position 13 -> 9 (cuts "baz ")
        assert find_path_word_start_backward("/foo/bar/baz ", 13) == 9

    def test_lone_slash_after_whitespace(self):
        """Lone slash after whitespace is absorbed with preceding word."""
        # "load /" from end returns 0 (cuts "load /")
        assert find_path_word_start_backward("load /", 6) == 0

    def test_lone_slash_with_multiple_spaces(self):
        """Lone slash with multiple spaces still absorbed."""
        # "load  /" from end returns 0 (cuts "load  /")
        assert find_path_word_start_backward("load  /", 7) == 0

    def test_consecutive_slashes_from_end(self):
        """Consecutive slashes from end returns start of last component."""
        # /foo//bar from position 9 -> 6 (before 'b' in bar)
        assert find_path_word_start_backward("/foo//bar", 9) == 6

    def test_consecutive_slashes_absorbed_into_component(self):
        """Consecutive slashes absorbed into preceding component."""
        # /foo//bar from position 6 (before 'bar') -> 1 (cuts "foo//")
        assert find_path_word_start_backward("/foo//bar", 6) == 1

    def test_trailing_consecutive_slashes(self):
        """Trailing consecutive slashes absorbed into component."""
        # /foo// from end (position 6) -> 1 (cuts "foo//")
        assert find_path_word_start_backward("/foo//", 6) == 1

    def test_root_slash_from_end(self):
        """Root slash from end returns 0."""
        # "/" from end (position 1) -> 0
        assert find_path_word_start_backward("/", 1) == 0

    def test_tilde_path(self):
        """Tilde path works like regular path."""
        # ~/foo/bar from end (position 10) -> 7 (before 'b' in bar)
        assert find_path_word_start_backward("~/foo/bar", 9) == 6

    def test_relative_path(self):
        """Relative path from end returns start of last component."""
        # foo/bar/baz from end (position 11) -> 8 (before 'b' in baz)
        assert find_path_word_start_backward("foo/bar/baz", 11) == 8

    def test_cursor_in_middle_of_component(self):
        """Cursor in middle of component returns start of that component."""
        # /foo/bar/baz with cursor at position 11 (before 'z') -> 9
        assert find_path_word_start_backward("/foo/bar/baz", 11) == 9

    def test_cursor_right_after_slash(self):
        """Cursor right after slash cuts preceding component with slash."""
        # /foo/bar/baz with cursor at position 9 (after '/') -> 5 (cuts "bar/")
        assert find_path_word_start_backward("/foo/bar/baz", 9) == 5

    def test_mixed_content_from_end(self):
        """Mixed content from end returns start of last path component."""
        # "load /foo/bar" from end (position 13) -> 10 (before 'b' in bar)
        assert find_path_word_start_backward("load /foo/bar", 13) == 10
