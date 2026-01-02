#!/usr/bin/env python3
"""Terminal key input capture for Platyplaty.

Captures terminal key events via prompt_toolkit and routes them to the
event queue for keybinding dispatch.
"""

import asyncio
import atexit
import contextlib
import sys
import termios
from collections.abc import Callable

from prompt_toolkit.input import Input, create_input
from prompt_toolkit.keys import Keys

from platyplaty.event_loop import EventLoopState
from platyplaty.types import KeyPressedEvent

# Original terminal settings for restoration
_original_termios: list[object] | None = None


def is_stdin_tty() -> bool:
    """Check if stdin is connected to a TTY."""
    return sys.stdin.isatty()


def _save_terminal_state() -> None:
    """Save the current terminal state for later restoration."""
    global _original_termios
    if not is_stdin_tty() or _original_termios is not None:
        return
    with contextlib.suppress(OSError, termios.error):
        _original_termios = termios.tcgetattr(sys.stdin.fileno())


def _restore_terminal_state() -> None:
    """Restore the terminal to its original state."""
    if _original_termios is None:
        return
    with contextlib.suppress(OSError, termios.error):
        termios.tcsetattr(
            sys.stdin.fileno(),
            termios.TCSANOW,
            _original_termios,  # type: ignore[arg-type]
        )


def _register_atexit_handler() -> None:
    """Register atexit handler to restore terminal state on exit."""
    atexit.register(_restore_terminal_state)


def _key_to_name(key: Keys | str) -> str:
    """Convert prompt_toolkit key to standardized key name.

    Args:
        key: The prompt_toolkit key object or string.

    Returns:
        Lowercase prompt_toolkit-style key name.
    """
    if not isinstance(key, Keys):
        return str(key).lower()
    name = key.value if hasattr(key, "value") else str(key)
    if name.startswith("c-"):
        return "control-" + name[2:]
    if name.startswith("s-"):
        return "shift-" + name[2:]
    return name.lower()


def _create_key_event(key_name: str) -> KeyPressedEvent:
    """Create a KeyPressedEvent from a key name.

    Args:
        key_name: The standardized key name.

    Returns:
        A KeyPressedEvent with source "client".
    """
    return KeyPressedEvent(source="PLATYPLATY", event="KEY_PRESSED", key=key_name)


async def _process_key_queue(
    key_queue: asyncio.Queue[str],
    state: EventLoopState,
    key_callback: Callable[[KeyPressedEvent], None],
) -> None:
    """Process keys from the queue until shutdown.

    Args:
        key_queue: Queue of key names from terminal input.
        state: Shared event loop state.
        key_callback: Callback to invoke with each key event.
    """
    while not state.shutdown_requested:
        try:
            key_name = await asyncio.wait_for(key_queue.get(), timeout=0.5)
        except TimeoutError:
            continue
        except asyncio.CancelledError:
            break
        event = _create_key_event(key_name)
        key_callback(event)


def _read_keys_to_queue(
    input_obj: Input,
    key_queue: asyncio.Queue[str],
    loop: asyncio.AbstractEventLoop,
) -> None:
    """Read available keys from input and put them in the queue.

    Args:
        input_obj: The prompt_toolkit Input object.
        key_queue: Queue to put key names into.
        loop: The asyncio event loop for thread-safe queue access.
    """
    for key_press in input_obj.read_keys():
        key_name = _key_to_name(key_press.key)
        loop.call_soon_threadsafe(key_queue.put_nowait, key_name)


def _handle_keys_ready(
    input_obj: Input,
    key_queue: asyncio.Queue[str],
    loop: asyncio.AbstractEventLoop,
    state: EventLoopState,
) -> None:
    """Handle the keys_ready callback from prompt_toolkit.

    Args:
        input_obj: The prompt_toolkit Input object.
        key_queue: Queue to put key names into.
        loop: The asyncio event loop.
        state: Shared event loop state.
    """
    try:
        _read_keys_to_queue(input_obj, key_queue, loop)
    except OSError:
        state.shutdown_requested = True
        loop.call_soon_threadsafe(state.shutdown_event.set)


async def _run_input_loop(
    state: EventLoopState,
    key_callback: Callable[[KeyPressedEvent], None],
) -> None:
    """Run the main input loop with prompt_toolkit.

    Args:
        state: Shared event loop state.
        key_callback: Callback to invoke with each key event.
    """
    input_obj = create_input()
    loop = asyncio.get_running_loop()
    key_queue: asyncio.Queue[str] = asyncio.Queue()

    def keys_ready() -> None:
        _handle_keys_ready(input_obj, key_queue, loop, state)

    with input_obj.attach(keys_ready):
        await _process_key_queue(key_queue, state, key_callback)


async def terminal_input_task(
    state: EventLoopState,
    key_callback: Callable[[KeyPressedEvent], None],
) -> None:
    """Async task that captures terminal key events.

    Uses prompt_toolkit's Input.attach() for callback-based input
    that integrates with the asyncio event loop without blocking.

    Args:
        state: Shared event loop state.
        key_callback: Callback to invoke with each key event.
    """
    if not is_stdin_tty():
        return

    _save_terminal_state()
    _register_atexit_handler()

    try:
        await _run_input_loop(state, key_callback)
    except OSError:
        state.shutdown_requested = True
        state.shutdown_event.set()
    finally:
        _restore_terminal_state()
