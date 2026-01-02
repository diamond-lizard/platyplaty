#!/usr/bin/env python3
"""
Unit tests for key event handling.

Tests KEY_PRESSED event parsing, event queueing, keybinding dispatch,
and navigation functions.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.event_loop import (
    EventLoopState,
    MAX_KEY_EVENT_QUEUE,
    clear_key_event_queue,
    process_queued_key_events,
)
from platyplaty.keybinding_dispatch import (
    action_next_preset,
    action_previous_preset,
    action_quit,
    build_client_dispatch_table,
    build_renderer_dispatch_table,
    dispatch_key_event,
)
from platyplaty.playlist import Playlist
from platyplaty.stderr_parser import parse_stderr_event
from platyplaty.types import (
    ClientKeybindings,
    KeyPressedEvent,
)


def make_netstring(payload: str) -> str:
    """Create a netstring from a payload string."""
    encoded = payload.encode("utf-8")
    return f"{len(encoded)}:{payload},"


# =============================================================================
# TASK-4400: Test that client parses KEY_PRESSED events correctly
# =============================================================================


class TestKeyPressedParsing:
    """Tests for KEY_PRESSED event parsing."""

    def test_parse_key_pressed_simple_key(self) -> None:
        """Parse a simple KEY_PRESSED event with a letter key."""
        line = make_netstring('{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "n"}')
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.event == "KEY_PRESSED"
        assert event.key == "n"

    def test_parse_key_pressed_with_control_modifier(self) -> None:
        """Parse a KEY_PRESSED event with control modifier."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "control-n"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "control-n"

    def test_parse_key_pressed_with_multiple_modifiers(self) -> None:
        """Parse a KEY_PRESSED event with multiple modifiers."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "control-shift-alt-n"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "control-shift-alt-n"

    def test_parse_key_pressed_function_key(self) -> None:
        """Parse a KEY_PRESSED event with a function key."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "f12"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "f12"

    def test_parse_key_pressed_navigation_key(self) -> None:
        """Parse a KEY_PRESSED event with a navigation key."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "KEY_PRESSED", "key": "pagedown"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert isinstance(event, KeyPressedEvent)
        assert event.key == "pagedown"

    def test_parse_key_pressed_missing_key_field_returns_none(self) -> None:
        """KEY_PRESSED without key field returns None (invalid event)."""
        line = make_netstring('{"source": "PLATYPLATY", "event": "KEY_PRESSED"}')
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_non_platyplaty_source_returns_none(self) -> None:
        """Events with non-PLATYPLATY source return None."""
        line = make_netstring(
            '{"source": "OTHER", "event": "KEY_PRESSED", "key": "n"}'
        )
        event = parse_stderr_event(line)
        assert event is None

    def test_parse_regular_output_returns_none(self) -> None:
        """Regular stderr output returns None."""
        event = parse_stderr_event("Some debug output from renderer")
        assert event is None

    def test_parse_disconnect_event_still_works(self) -> None:
        """DISCONNECT events still parse correctly after adding KEY_PRESSED."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "DISCONNECT", "reason": "client closed"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "DISCONNECT"

    def test_parse_quit_event_still_works(self) -> None:
        """QUIT events still parse correctly after adding KEY_PRESSED."""
        line = make_netstring(
            '{"source": "PLATYPLATY", "event": "QUIT", "reason": "user quit"}'
        )
        event = parse_stderr_event(line)
        assert event is not None
        assert event.event == "QUIT"


# =============================================================================
# TASK-4500: Test that event queueing works during pending commands
# =============================================================================


@pytest.fixture
def mock_client() -> AsyncMock:
    """Create a mock SocketClient."""
    return AsyncMock()


@pytest.fixture
def playlist() -> Playlist:
    """Create a test playlist with multiple presets."""
    return Playlist([
        Path("/presets/test1.milk"),
        Path("/presets/test2.milk"),
        Path("/presets/test3.milk"),
    ])


@pytest.fixture
def renderer_dispatch_table() -> dict:
    """Create a test renderer dispatch table."""
    return build_renderer_dispatch_table("n", "p", "q")


@pytest.fixture
def client_keybindings() -> ClientKeybindings:
    """Create test client keybindings."""
    return ClientKeybindings(quit=None)


@pytest.fixture
def event_loop_state(
    mock_client: AsyncMock,
    playlist: Playlist,
    renderer_dispatch_table: dict,
    client_keybindings: ClientKeybindings,
) -> EventLoopState:
    """Create an EventLoopState for testing."""
    return EventLoopState(
        client_keybindings=client_keybindings,
        renderer_dispatch_table=renderer_dispatch_table,
        playlist=playlist,
        client=mock_client,
    )


def make_key_event(key: str) -> KeyPressedEvent:
    """Create a KeyPressedEvent for testing."""
    return KeyPressedEvent(
        source="PLATYPLATY",
        event="KEY_PRESSED",
        key=key,
    )


class TestEventQueueing:
    """Tests for event queueing during pending commands."""

    def test_queue_respects_max_size(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Queue discards oldest events when full (REQ-0500)."""
        event_loop_state.command_pending = True
        # Queue more than MAX_KEY_EVENT_QUEUE events
        for i in range(MAX_KEY_EVENT_QUEUE + 3):
            event_loop_state.key_event_queue.append(make_key_event(f"key{i}"))
        # Queue should be at max size
        assert len(event_loop_state.key_event_queue) == MAX_KEY_EVENT_QUEUE
        # Oldest events should have been discarded
        first_event = event_loop_state.key_event_queue[0]
        assert first_event.key == "key3"

    def test_process_queued_events_returns_fifo_order(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Queued events are processed in FIFO order (REQ-0600)."""
        event_loop_state.key_event_queue.append(make_key_event("first"))
        event_loop_state.key_event_queue.append(make_key_event("second"))
        event_loop_state.key_event_queue.append(make_key_event("third"))
        events = process_queued_key_events(event_loop_state)
        assert len(events) == 3
        assert events[0].key == "first"
        assert events[1].key == "second"
        assert events[2].key == "third"

    def test_process_queued_events_clears_queue(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Processing queued events clears the queue."""
        event_loop_state.key_event_queue.append(make_key_event("test"))
        process_queued_key_events(event_loop_state)
        assert len(event_loop_state.key_event_queue) == 0

    def test_clear_key_event_queue_empties_queue(
        self, event_loop_state: EventLoopState
    ) -> None:
        """clear_key_event_queue empties the queue (REQ-0700)."""
        event_loop_state.key_event_queue.append(make_key_event("test1"))
        event_loop_state.key_event_queue.append(make_key_event("test2"))
        clear_key_event_queue(event_loop_state)
        assert len(event_loop_state.key_event_queue) == 0


# =============================================================================
# TASK-4600: Test that keybinding dispatch invokes correct functions
# =============================================================================


class TestKeybindingDispatch:
    """Tests for keybinding dispatch."""

    def test_dispatch_bound_key_returns_true(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Dispatch returns True for bound keys."""
        table = build_renderer_dispatch_table("n", "p", "q")
        result = dispatch_key_event("n", table, event_loop_state)
        assert result is True

    def test_dispatch_unbound_key_returns_false(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Dispatch returns False for unbound keys (TASK-3800)."""
        table = build_renderer_dispatch_table("n", "p", "q")
        result = dispatch_key_event("x", table, event_loop_state)
        assert result is False

    def test_dispatch_invokes_quit_callback(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Dispatch invokes quit callback and sets shutdown flag."""
        table = build_renderer_dispatch_table("n", "p", "q")
        assert event_loop_state.shutdown_requested is False
        dispatch_key_event("q", table, event_loop_state)
        assert event_loop_state.shutdown_requested is True

    def test_build_renderer_dispatch_table_maps_all_keys(self) -> None:
        """Renderer dispatch table maps all three action keys."""
        table = build_renderer_dispatch_table("next", "prev", "exit")
        assert "next" in table
        assert "prev" in table
        assert "exit" in table

    def test_build_client_dispatch_table_with_quit(self) -> None:
        """Client dispatch table includes quit when specified."""
        table = build_client_dispatch_table("control-q")
        assert "control-q" in table

    def test_build_client_dispatch_table_without_quit(self) -> None:
        """Client dispatch table is empty when quit is None."""
        table = build_client_dispatch_table(None)
        assert len(table) == 0


# =============================================================================
# TASK-4700: Test next_preset and previous_preset navigation
# =============================================================================


class TestNavigationActions:
    """Tests for navigation action functions."""

    def test_next_preset_queues_load_command(
        self, event_loop_state: EventLoopState
    ) -> None:
        """next_preset queues LOAD PRESET command with next path."""
        event_loop_state.renderer_ready = True
        action_next_preset(event_loop_state)
        assert event_loop_state.command_queue.qsize() == 1
        cmd, params = event_loop_state.command_queue.get_nowait()
        assert cmd == "LOAD PRESET"
        assert "path" in params
        assert "test2.milk" in params["path"]

    def test_previous_preset_queues_load_command(
        self, event_loop_state: EventLoopState
    ) -> None:
        """previous_preset queues LOAD PRESET with previous path."""
        event_loop_state.renderer_ready = True
        # Advance once first so we can go back
        event_loop_state.playlist.next()
        action_previous_preset(event_loop_state)
        assert event_loop_state.command_queue.qsize() == 1
        cmd, params = event_loop_state.command_queue.get_nowait()
        assert cmd == "LOAD PRESET"
        assert "path" in params
        assert "test1.milk" in params["path"]

    def test_next_preset_ignored_when_renderer_not_ready(
        self, event_loop_state: EventLoopState
    ) -> None:
        """next_preset is silently ignored when renderer_ready is False."""
        event_loop_state.renderer_ready = False
        action_next_preset(event_loop_state)
        assert event_loop_state.command_queue.qsize() == 0

    def test_previous_preset_ignored_when_renderer_not_ready(
        self, event_loop_state: EventLoopState
    ) -> None:
        """previous_preset is silently ignored when renderer_ready is False."""
        event_loop_state.renderer_ready = False
        action_previous_preset(event_loop_state)
        assert event_loop_state.command_queue.qsize() == 0

    def test_next_preset_handles_end_of_playlist(
        self, event_loop_state: EventLoopState
    ) -> None:
        """next_preset handles end of non-looping playlist gracefully."""
        event_loop_state.renderer_ready = True
        # Disable looping and advance to end
        event_loop_state.playlist.loop = False
        event_loop_state.playlist.next()  # -> test2
        event_loop_state.playlist.next()  # -> test3
        event_loop_state.playlist.next()  # -> None (end)
        action_next_preset(event_loop_state)
        # No command should be queued when at end
        assert event_loop_state.command_queue.qsize() == 0


# =============================================================================
# TASK-4800: Test quit terminates the application cleanly
# =============================================================================


class TestQuitAction:
    """Tests for quit action."""

    def test_action_quit_sets_shutdown_flag(
        self, event_loop_state: EventLoopState
    ) -> None:
        """action_quit sets shutdown_requested to True."""
        assert event_loop_state.shutdown_requested is False
        action_quit(event_loop_state)
        assert event_loop_state.shutdown_requested is True

    def test_quit_works_when_renderer_not_ready(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Quit action works even when renderer is not ready."""
        event_loop_state.renderer_ready = False
        action_quit(event_loop_state)
        assert event_loop_state.shutdown_requested is True

    def test_quit_via_dispatch(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Quit action via dispatch sets shutdown flag."""
        table = build_renderer_dispatch_table("n", "p", "q")
        dispatch_key_event("q", table, event_loop_state)
        assert event_loop_state.shutdown_requested is True

    def test_quit_via_client_dispatch(
        self, event_loop_state: EventLoopState
    ) -> None:
        """Quit action via client dispatch sets shutdown flag."""
        table = build_client_dispatch_table("control-q")
        dispatch_key_event("control-q", table, event_loop_state)
        assert event_loop_state.shutdown_requested is True
