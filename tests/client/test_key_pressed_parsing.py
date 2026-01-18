#!/usr/bin/env python3
"""
Unit tests for KEY_PRESSED event parsing with Textual key format.

Tests parsing of KEY_PRESSED events from renderer stderr output.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.types import KeyPressedEvent


class TestKeyPressedParsing:
    """Tests for KEY_PRESSED event parsing."""

    def test_parse_key_pressed_simple_key(self) -> None:
        """Parse a simple KEY_PRESSED event with a letter key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.event == "KEY_PRESSED"
        assert event.key == "n"

    def test_parse_key_pressed_with_ctrl_modifier(self) -> None:
        """Parse a KEY_PRESSED event with ctrl modifier (Textual format)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "ctrl+n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "ctrl+n"

    def test_parse_key_pressed_with_multiple_modifiers(self) -> None:
        """Parse a KEY_PRESSED event with multiple modifiers (Textual format)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "ctrl+shift+alt+n"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "ctrl+shift+alt+n"

    def test_parse_key_pressed_function_key(self) -> None:
        """Parse a KEY_PRESSED event with a function key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "f12"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "f12"

    def test_parse_key_pressed_navigation_key(self) -> None:
        """Parse a KEY_PRESSED event with a navigation key."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "pagedown"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "pagedown"

    def test_parse_key_pressed_missing_key_field_returns_none(self) -> None:
        """KEY_PRESSED without key field returns None (invalid event)."""
        line = '{"source": "PLATYPLATY", "event": "KEY_PRESSED"}'
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_non_platyplaty_source_returns_none(self) -> None:
        """Events with non-PLATYPLATY source return None."""
        line = '{"source": "OTHER", "event": "KEY_PRESSED", "key": "n"}'
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_regular_output_returns_none(self) -> None:
        """Regular stderr output returns None."""
        event = parse_stderr_event("Some debug output from renderer")
        assert event is None

    def test_parse_disconnect_event_still_works(self) -> None:
        """DISCONNECT events still parse correctly."""
        line = '{"source": "PLATYPLATY", "event": "DISCONNECT", "reason": "client closed"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "DISCONNECT"

    def test_parse_quit_event_still_works(self) -> None:
        """QUIT events still parse correctly."""
        line = '{"source": "PLATYPLATY", "event": "QUIT", "reason": "user quit"}'
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "QUIT"
