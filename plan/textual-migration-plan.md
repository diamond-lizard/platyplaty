---
goal: Migrate from Prompt Toolkit to Textual for terminal UI
version: 1.0
date_created: 2026-01-02
last_updated: 2026-01-03
owner: Platyplaty Team
status: Completed
tags: [migration, refactor, ui]
---

# Introduction

![Status: Completed](https://img.shields.io/badge/status-Completed-blue)

This plan migrates the Platyplaty Python client from Prompt Toolkit to Textual. The migration establishes Textual as the application framework, replacing the current asyncio-based event loop with Textual's app lifecycle. This is a minimal migration that preserves existing functionality while laying the foundation for future TUI enhancements.

## 1. Requirements & Constraints

- **REQ-100**: Textual becomes the main application framework, owning the event loop and terminal
- **REQ-200**: Background tasks (auto-advance, stderr monitor) run as Textual Workers
- **REQ-300**: Workers use CancelledError for shutdown instead of explicit shutdown flags
- **REQ-400**: Actions are methods on PlatyplatyApp that access state via direct instance attributes (`self._client`, `self.playlist`, etc.)
- **REQ-500**: Key naming adopts Textual convention (`ctrl+q` instead of `control-q`)
- **REQ-600**: Reconnection logic is removed; disconnect triggers app exit
- **REQ-700**: Log messages are posted to the App via Textual's message system
- **REQ-800**: App displays status text and RichLog widget for messages
- **REQ-900**: Graceful shutdown sends QUIT command to renderer before closing socket
- **CON-100**: Breaking change for config files due to key naming convention change
- **CON-200**: Users must update keybinding config values to new format
- **GUD-100**: Prefer Textual's built-in mechanisms over custom implementations

### 1.1 Design Notes: Async Flow and Command Serialization

**Why custom dispatch tables instead of Textual's BINDINGS.** Textual provides a built-in `BINDINGS` class variable that automatically maps keys to actions without custom dispatch code. However, Platyplaty uses custom dispatch tables for two reasons: (1) keybindings are user-configurable via config files at runtime, while `BINDINGS` is designed for static compile-time declarations; (2) Platyplaty has two sources of key input - terminal keys (handled by Textual) and renderer window keys (received via stderr from the C++ process) - requiring a unified dispatch mechanism that works for both. The custom approach trades Textual's Footer widget integration for runtime flexibility.

**Why `run_worker()` instead of `@work` decorator.** Textual provides two mechanisms for starting workers: the `@work` decorator (for methods) and `run_worker()` (for any coroutine). This migration uses `run_worker()` to start `stderr_monitor_task()` and `auto_advance_loop()` because: (1) these are standalone functions in separate modules (`event_loop.py`, `auto_advance.py`), not methods on PlatyplatyApp; (2) the `@work` decorator requires a method on a DOMNode (App, Screen, or Widget) because it needs access to `self` to register the worker with Textual's WorkerManager - standalone functions have no such context; (3) keeping these as standalone functions preserves the modular code structure. In `on_mount()`, workers are started with `self.run_worker(stderr_monitor_task(self), name="stderr_monitor")` and similar for `auto_advance_loop()`.

**How Ctrl+C and SIGINT are handled.** Textual's terminal driver disables `ISIG` in termios settings by default (see `_patch_lflag()` in `linux_driver.py`). This means Ctrl+C pressed in the terminal is captured as a `ctrl+c` key event, NOT delivered as a SIGINT signal. To handle Ctrl+C for quitting, ensure `ctrl+c` is mapped to `"quit"` in `client_dispatch_table` (for terminal input) and `renderer_dispatch_table` (for renderer window input). Signal handlers registered via `loop.add_signal_handler(signal.SIGINT, ...)` only receive external signals (e.g., `kill -INT pid`, process managers, systemd). Both the key event path and signal handler path call `graceful_shutdown()`, and the `_exiting` flag prevents double-shutdown races. Textual's default `ctrl+c` binding calls `action_help_quit()` which shows a "use Ctrl+Q to quit" message; our custom dispatch table overrides this.

This section documents key Textual behaviors that inform the migration design.

**Textual message handlers can be async.** If you prefix a handler (e.g., `on_key`) with `async def`, Textual will automatically `await` it. This is documented in the Textual guide under "Async handlers." This allows `on_key()` to await async methods like `run_action()`.


**Textual lifecycle methods can also be async.** Methods like `on_mount()` can be declared as `async def` and Textual will await them. This is necessary when the lifecycle method needs to perform async operations like starting subprocesses, connecting sockets, or sending commands. In this migration, `on_mount()` is async because it awaits `start_renderer()`, `client.connect()`, and multiple `send_command()` calls during application startup.
**`run_action()` is a coroutine.** The Textual `App.run_action()` method is async, so any code calling it must either be async (and await it) or use `asyncio.create_task()`. In this migration, `dispatch_key_event()` becomes async and awaits `run_action()`.

**Socket command serialization is separate from key event buffering.** Two distinct concerns were previously conflated:

1. **Key event buffering** (being removed): The `command_pending` flag and `key_event_queue` deferred key dispatch while a command was in flight. This is no longer needed because Textual's message queue handles input event concurrency.

2. **Socket command serialization** (simplified): The IPC protocol requires "at most one command in flight at a time" (see `reference/architecture/cpp-wrapper-components.md`). This is enforced by an `asyncio.Lock` inside `SocketClient.send_command()`. When a command is in progress, other callers wait on the lock; the event loop remains responsive. No explicit queue is needed.

**Async call chain.** After migration:
- `on_key()` (async) -> awaits `dispatch_key_event()` (async) -> awaits `app.run_action()` -> action method awaits `send_command()` (serialized via internal lock)
- `_handle_stderr_event()` (async context) -> awaits `dispatch_key_event()` -> same flow
- `auto_advance_loop()` (async) -> awaits `_try_load_preset()` -> awaits `send_command()` (serialized via same lock)

This design means key presses are dispatched immediately (no buffering), commands are serialized by the lock inside `send_command()` (protocol requirement), and the event loop stays responsive during waits.

**EventLoopState is eliminated.** After removing shutdown flags, event queues, and other concerns that Textual handles internally, EventLoopState would only contain `playlist` and `client` - both already stored directly on PlatyplatyApp. Keeping EventLoopState would create duplicate references (`app._client` vs `app.state.client`) risking desynchronization, and mixed access patterns that hurt code clarity. For safety, robustness, and clarity, all state lives directly on PlatyplatyApp as the single source of truth.

**The `_exiting` flag guards against shutdown races.** Multiple events can trigger application exit: user pressing quit key, Ctrl+C, renderer window close, socket disconnect, or renderer process exit. Without coordination, these could cause double-exit attempts or commands being sent to a closed socket. The `_exiting` flag (initialized False, set True at shutdown start) serves two purposes:

1. **Prevents double-exit**: Each exit path checks `if not self._exiting` before acting, so only the first trigger takes effect.
2. **Guards command sending**: Action methods check `_exiting` before sending commands, avoiding attempts to communicate with a disconnecting renderer.

**Shutdown entry points.** Exit can be triggered by:
- **Client-initiated**: User presses quit key (terminal or renderer window) or Ctrl+C (as key event) or external SIGINT/SIGTERM. These call `graceful_shutdown()`, which sets `_exiting`, sends QUIT command, closes socket, then calls `app.exit()`.
- **Renderer-initiated**: Renderer window closed, renderer receives signal, or renderer crashes. The stderr monitor sees a QUIT/DISCONNECT event or process exit. It sets `_exiting` then calls `app.exit()` (no QUIT command needed since renderer already exited).
- **Socket failure during operation**: If `send_command()` raises `ConnectionError` (socket EOF or write failure while awaiting response), set `_exiting` then call `app.exit()` directly. Do not call `graceful_shutdown()` since the socket is already broken and QUIT cannot be sent. The renderer will detect the client disconnect and stay alive per the robustness philosophy. See TASK-0100 and TASK-0200. See the State Transition Tables below for all `_exiting` transitions.

**Stderr events from renderer.** The renderer sends structured events on stderr:
- `KEY_PRESSED <key>`: User pressed a key in the renderer window; dispatched via `renderer_dispatch_table`
- `QUIT`: Renderer is exiting (window closed, signal received, or responding to QUIT command)
- `DISCONNECT`: Socket write failed on renderer side
- `AUDIO_ERROR <reason>`: Audio capture failed; logged as warning

**State Transition Tables.** Following the guidance in [future-architecture-considerations.md](../reference/architecture/future-architecture-considerations.md), these tables specify all state transitions with responsible components.

*`_renderer_ready` flag transitions:*

| Transition | Trigger | Responsible Component | Method/Location |
|------------|---------|----------------------|-----------------|
| False -> True | INIT command succeeds | PlatyplatyApp | `on_mount()` Stage A |

*`_exiting` flag transitions:*

| Transition | Trigger | Responsible Component | Method/Location |
|------------|---------|----------------------|-----------------|
| False -> True | User presses quit key | PlatyplatyApp | `graceful_shutdown()` |
| False -> True | Ctrl+C key event (terminal) | dispatch_key_event | Calls `action_quit()` -> `graceful_shutdown()` |
| False -> True | External SIGINT/SIGTERM | Signal handler | Calls `graceful_shutdown()` |
| False -> True | Renderer stderr emits QUIT | stderr_monitor | `_handle_stderr_event()` |
| False -> True | Renderer stderr emits DISCONNECT | stderr_monitor | `_handle_stderr_event()` |
| False -> True | Renderer process exits | stderr_monitor | `stderr_monitor_task()` |
| False -> True | Socket ConnectionError during action | dispatch_key_event | `dispatch_key_event()` |
| False -> True | Socket ConnectionError during auto-advance | auto_advance_loop | `auto_advance_loop()` |

## 2. Implementation Steps

### Phase 10: Update Dependencies

- GOAL-0100: Update project dependencies to use Textual instead of Prompt Toolkit

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-0300 | Run `uv add textual` to add the package | Yes | 2026-01-03 |
| TASK-0400 | Run `uv remove prompt-toolkit` to remove the package | Yes | 2026-01-03 |
| TASK-0500 | Run dependency installation to verify no conflicts | Yes | 2026-01-03 |

### Phase 20: Create Log Message Infrastructure

- GOAL-0200: Create Textual message types for worker-to-app log communication

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-0600 | Create `messages.py` module with `LogMessage` class extending Textual's Message | Yes | 2026-01-03 |
| TASK-0700 | LogMessage contains text content and optional severity level | Yes | 2026-01-03 |

### Phase 30: Update Key Naming Convention

- GOAL-0300: Adopt Textual's key naming convention in both Python code and C++ renderer

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-0800 | Update `types/keys.py` to use Textual key names: `ctrl+` instead of `control-`, `shift+` instead of `shift-`, `alt+` instead of `alt-` | Yes | 2026-01-03 |
| TASK-0900 | Update `_MODIFIER_PREFIXES` and `_ABBREVIATED_PREFIXES` constants | Yes | 2026-01-03 |
| TASK-1000 | Update `is_valid_key_name()` function for new format | Yes | 2026-01-03 |
| TASK-1100 | Update `has_abbreviated_modifier()` function for new format | Yes | 2026-01-03 |
| TASK-1200 | Update `types/config.py` validation error messages to reference new format | Yes | 2026-01-03 |
| TASK-1300 | Update `conf/platyplaty-conf.toml` example keybinding to use `ctrl+q` format | Yes | 2026-01-03 |
| TASK-1400 | Update `renderer/scancode_map.cpp` to use Textual modifier prefixes: `ctrl+` instead of `control-`, `shift+` instead of `shift-`, `alt+` instead of `alt-` | Yes | 2026-01-03 |
| TASK-1500 | Update file header comment in `scancode_map.cpp` from "prompt_toolkit-style" to "Textual-style" | Yes | 2026-01-03 |
| TASK-1600 | Rebuild the renderer with `make` | Yes | 2026-01-03 |

### Phase 40: Create App Skeleton

- GOAL-0400: Create PlatyplatyApp class skeleton with instance attributes for client, playlist, and state flags

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-1700 | Create `app.py` module with `PlatyplatyApp` class extending textual.app.App | Yes | 2026-01-03 |
| TASK-1800 | Add `renderer_dispatch_table` and `client_dispatch_table` attributes to PlatyplatyApp (type: mapping of key names to action name strings) | Yes | 2026-01-03 |
| TASK-1900 | Add `_renderer_ready: bool` instance attribute type annotation to PlatyplatyApp (initialization in TASK-2000) | Yes | 2026-01-03 |

### Phase 50: Migrate Actions to App Methods

- GOAL-0500: Move action functions to PlatyplatyApp as methods, change dispatch tables to map keys to action names

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-2100 | Change `DispatchTable` type alias from mapping keys to callbacks to mapping keys to action name strings | Yes | 2026-01-03 |
| TASK-2200 | Remove `ActionCallback` type alias (no longer needed with action methods) | Yes | 2026-01-03 |
| TASK-2300 | Add `action_quit()` async method to PlatyplatyApp that calls `await self.graceful_shutdown()` (graceful_shutdown handles exit internally) | Yes | 2026-01-03 |
| TASK-2400 | Add `action_next_preset()` async method to PlatyplatyApp that checks `self._renderer_ready` and `not self._exiting`, and if both True, calls `path = self.playlist.next()` and if `path is not None`, wraps the send_command call in try/except RendererError to catch preset load failures (e.g., file not found, parse error) and post a LogMessage warning; returns None when loop=false and at end of playlist | Yes | 2026-01-03 |
| TASK-2500 | Add `action_previous_preset()` async method to PlatyplatyApp that checks `self._renderer_ready` and `not self._exiting`, and if both True, calls `path = self.playlist.previous()` and if `path is not None`, wraps the send_command call in try/except RendererError to catch preset load failures (e.g., file not found, parse error) and post a LogMessage warning; returns None when loop=false and at start of playlist | Yes | 2026-01-03 |
| TASK-0100 | Update `dispatch_key_event()` to be async; change signature to take key, dispatch table, and app; look up action name from table and await `app.run_action(name)` (async required because run_action is a coroutine); wrap the `run_action()` call in try/except ConnectionError and set `app._exiting = True` then call `app.exit()`, but only if `not app._exiting` (central handling for socket failures during key-triggered actions) | Yes | 2026-01-03 |
| TASK-2600 | Delete `action_quit()`, `action_next_preset()`, `action_previous_preset()` standalone functions from keybinding_dispatch.py | Yes | 2026-01-03 |
| TASK-2700 | Update `build_renderer_dispatch_table()` to return action name strings (without `action_` prefix, e.g., `"quit"`, `"next_preset"`) instead of callbacks | Yes | 2026-01-03 |
| TASK-2800 | Update `build_client_dispatch_table()` to return action name strings (without `action_` prefix) instead of callbacks | Yes | 2026-01-03 |

### Phase 60: Implement Graceful Shutdown

- GOAL-0600: Add command serialization lock to SocketClient and implement graceful_shutdown on App

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-2900 | Add `_send_lock: asyncio.Lock` attribute to SocketClient; in `send_command()`, wrap the send-and-receive logic in `async with self._send_lock:` to serialize all commands. This ensures only one command is in flight at a time, enforcing the protocol invariant without an explicit queue | Yes | 2026-01-03 |
| TASK-3000 | Add `graceful_shutdown()` async method to PlatyplatyApp. Implementation: set `self._exiting = True`, wrap `await self._client.send_command("QUIT")` in try/except ConnectionError (renderer may already be gone), call `self._client.close()`, then call `self.exit()`. This makes `graceful_shutdown()` the single entry point for all intentional exits and prevents double-exit from stderr QUIT handler. | Yes | 2026-01-03 |

### Phase 70: Update Worker Functions

- GOAL-0700: Refactor worker functions to use CancelledError pattern and post log messages

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-3100 | Update `auto_advance_loop()` to use `while True` loop with CancelledError handling | Yes | 2026-01-03 |
| TASK-3200 | Update `auto_advance_loop()` signature to accept only `app`; access client via `app._client`, playlist via `app.playlist`, duration via `app.preset_duration`, and post LogMessage instead of writing to output; restructure to advance-try-wait order: (1) advance with `playlist.next()`, (2) call `await _try_load_preset()`, (3) if success wait `preset_duration` seconds, if failure post LogMessage warning, wait 0.5 seconds, and loop immediately; track consecutive failures and break with warning if failures reach playlist length (all presets broken); check `app._exiting` before each iteration | Yes | 2026-01-03 |
| TASK-3300 | Update `load_preset_with_retry()` signature to accept only `app`; access client via `app._client`, playlist via `app.playlist`, and post LogMessage for preset load warnings; add `if app._exiting: return False` check at start of each retry iteration to abort during shutdown | Yes | 2026-01-03 |
| TASK-3400 | Update `_try_load_preset()` signature to accept only `app`; access client via `app._client` and post LogMessage for preset load warnings | Yes | 2026-01-03 |
| TASK-0200 | Update `auto_advance_loop()` to catch `ConnectionError` and set `app._exiting = True` then call `app.exit()`, but only if `app._exiting` is False | Yes | 2026-01-03 |
| TASK-3500 | Update `stderr_monitor_task()` to use CancelledError pattern | Yes | 2026-01-03 |
| TASK-3600 | Update `stderr_monitor_task()` to accept app instead of state, output, and process; access process via `app._renderer_process` | Yes | 2026-01-03 |
| TASK-3700 | Update `process_stderr_line()` to accept app instead of state and output; for non-event lines (where `parse_stderr_event()` returns None), post `LogMessage(level="debug", message=line.rstrip())` instead of writing to output; change call to `_handle_stderr_event()` to use `await` (required because TASK-3800 makes it async) | Yes | 2026-01-03 |
| TASK-3800 | Make `_handle_stderr_event()` async and update it to await `dispatch_key_event()` with `app.renderer_dispatch_table` for KEY_PRESSED; remove the `if command_pending` branch and always dispatch immediately (key event buffering is no longer needed because Textual handles input concurrency; socket command serialization is handled by the internal lock in SocketClient). Note: while awaiting, stderr reading is paused; this is safe because actions await `send_command()` which typically completes in milliseconds (local Unix socket); for quit, this happens during shutdown when a brief pause is acceptable. For client-initiated quit, the QUIT command response is the authoritative confirmation; the stderr QUIT event that follows is redundant and harmless to miss. For renderer-initiated quit (window close, signal), the stderr QUIT event is received normally since no blocking await is in progress | Yes | 2026-01-03 |
| TASK-3900 | Update `_handle_stderr_event()` to accept app instead of state and output | Yes | 2026-01-03 |
| TASK-4000 | Update `_handle_stderr_event()` to set `app._exiting = True` then call `app.exit()` on QUIT event, but only if `app._exiting` is False (handles renderer-initiated exit like window close) | Yes | 2026-01-03 |
| TASK-4100 | Update `_handle_stderr_event()` to set `app._exiting = True` then call `app.exit()` on DISCONNECT event, but only if `app._exiting` is False (handles socket write failures) | Yes | 2026-01-03 |
| TASK-4200 | Update `_handle_stderr_event()` to post LogMessage for AUDIO_ERROR. Delete `log_audio_error()` function from stderr_parser.py (the single call site now inlines the logic as a simple `app.post_message(LogMessage(...))`) | Yes | 2026-01-03 |
| TASK-4300 | Update `stderr_monitor_task()` to set `app._exiting = True` then call `app.exit()` when renderer process exits, but only if `app._exiting` is False (no QUIT needed since renderer is already gone) | Yes | 2026-01-03 |

### Phase 80: Delete EventLoopState

- GOAL-0800: Delete EventLoopState class entirely. All state now lives directly on PlatyplatyApp: `_client`, `playlist`, `_renderer_ready`, `_exiting`, dispatch tables. Delete associated helper functions (process_queued_key_events, clear_key_event_queue). This phase depends on Phase 70 completing first, as worker function signatures must be updated before the state class they consume can be deleted

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-4400 | Delete `EventLoopState` class from event_loop.py (all state now on PlatyplatyApp) | Yes | 2026-01-03 |
| TASK-4500 | Delete `process_queued_key_events()` function from event_loop.py (no longer needed) | Yes | 2026-01-03 |
| TASK-4600 | Delete `clear_key_event_queue()` function from event_loop.py (no longer needed) | Yes | 2026-01-03 |
| TASK-4700 | Delete `MAX_KEY_EVENT_QUEUE` constant from event_loop.py (no longer needed) | Yes | 2026-01-03 |
| TASK-4800 | Remove unused imports from event_loop.py (`deque`, `asyncio.Event`, etc.) | Yes | 2026-01-03 |

### Phase 90: Implement Textual Application

- GOAL-0900: Implement Textual App methods for widgets and worker management

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-2000 | Add constructor accepting all startup parameters (socket_path, audio_source, playlist, preset_duration, fullscreen, client_keybindings, renderer_keybindings), store them as instance attributes, and initialize `_exiting = False` guard flag, `_renderer_process: asyncio.subprocess.Process | None = None`, and `_renderer_ready = False`, and `_client: SocketClient | None = None` | Yes | 2026-01-03 |
| TASK-4900 | Implement `compose()` method returning Static widget for status text and RichLog widget for messages | Yes | 2026-01-03 |
| TASK-5000 | Implement async `on_mount()` to perform startup sequence. Wrap all stages (A, B, C) in try/except to catch startup errors; in except block, terminate `self._renderer_process` if it exists (call `terminate()` then `await wait()` to prevent zombies and allow atexit cleanup), close `self._client` if it exists, then call `self.exit(message=str(error))` (workers started in Stage B are automatically cancelled by Textual when `exit()` is called). Stage A (direct calls, before workers start): call `await start_renderer(self.socket_path)` and store result in `self._renderer_process`, create `SocketClient()` and store in `self._client`, call `await self._client.connect(self.socket_path)`, await `self._client.send_command("CHANGE AUDIO SOURCE", ...)`, await `self._client.send_command("INIT")`, set `self._renderer_ready = True`, await `load_preset_with_retry()` for initial preset and post LogMessage warning if it returns False (all presets failed). Stage B (start workers): start stderr_monitor and auto_advance_loop as Textual workers. Stage C (send final startup commands): await `self._client.send_command("SHOW WINDOW")`, optionally await `self._client.send_command("SET FULLSCREEN", enabled=True)`. Note: All socket calls use `send_command()` which serializes commands via an internal asyncio.Lock (see Phase 60). No queue is needed | Yes | 2026-01-03 |
| TASK-5100 | In `on_mount()`, before calling `load_preset_with_retry()`, build dispatch tables from stored keybindings (mapping keys to action names), assign to `self.renderer_dispatch_table` and `self.client_dispatch_table` (part of Stage A; see TASK-5000 for ordering) | Yes | 2026-01-03 |
| TASK-5200 | In `on_mount()`, start stderr_monitor as a Textual worker (part of Stage B; see TASK-5000 for ordering) | Yes | 2026-01-03 |
| TASK-5300 | In `on_mount()`, start auto_advance_loop as a Textual worker (part of Stage B; see TASK-5000 for ordering) | Yes | 2026-01-03 |
| TASK-5400 | Implement async `on_key()` handler to dispatch terminal key events via `self.client_dispatch_table` using `await dispatch_key_event()` (Textual awaits async message handlers) | Yes | 2026-01-03 |
| TASK-5500 | Implement `on_log_message()` handler to write messages to RichLog widget | Yes | 2026-01-03 |
| TASK-5600 | In `on_mount()`, register SIGINT and SIGTERM handlers via `loop.add_signal_handler()` that call `asyncio.create_task(self.graceful_shutdown())`. These handlers are for external signals only (e.g., `kill -INT pid`) because Textual disables ISIG so terminal Ctrl+C arrives as a key event, not a signal. Note: registering in `on_mount()` (not `__init__()`) ensures the event loop is running | Yes | 2026-01-03 |

### Phase 100: Update Entry Points

- GOAL-1000: Connect the new Textual app to the existing startup flow

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-5700 | Update `run_sequence.py` to import PlatyplatyApp | Yes | 2026-01-03 |
| TASK-5800 | Update `run_startup_sequence()` to instantiate PlatyplatyApp with config values and remove the `output: TextIO` parameter from the function signature | Yes | 2026-01-03 |
| TASK-5900 | Replace `asyncio.run(async_main(...))` with `app.run()` | Yes | 2026-01-03 |
| TASK-6000 | Remove unused imports from run_sequence.py (async_main, etc.) | Yes | 2026-01-03 |
| TASK-6100 | Update `startup.py` to call `run_startup_sequence(config)` without output argument | Yes | 2026-01-03 |
| TASK-6200 | Update any failing tests; create replacement tests for key event handling (action methods, dispatch_key_event with run_action) to replace deleted test_key_events.py coverage | Yes | 2026-01-03 |

### Phase 110: Delete Obsolete Files

- GOAL-1100: Remove files that are no longer needed after migration

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-6300 | Delete `terminal_input.py` | Yes | 2026-01-03 |
| TASK-6400 | Delete `async_main.py` | Yes | 2026-01-03 |
| TASK-6500 | Delete `shutdown.py`. Note: `register_signal_handlers()` is replaced by signal handling in `PlatyplatyApp.on_mount()` (see TASK-5600). `cancel_tasks()` is not migrated because Textual handles worker cancellation internally (see REQ-300). `graceful_shutdown()` becomes a method on PlatyplatyApp (see TASK-3000). | Yes | 2026-01-03 |
| TASK-6600 | Delete `command_queue.py` (command queueing is replaced by direct async `send_command()` calls with internal lock serialization) | Yes | 2026-01-03 |
| TASK-6700 | Delete `reconnect.py` | Yes | 2026-01-03 |
| TASK-6800 | Delete `tests/client/test_reconnect.py` | Yes | 2026-01-03 |
| TASK-6900 | Delete `tests/client/test_key_events.py` (tests EventLoopState, command_pending, key_event_queue, command_queue - all concepts being removed; replacement tests created in TASK-6200) | Yes | 2026-01-03 |
| TASK-7000 | Remove imports of deleted modules and deleted exports (EventLoopState, process_queued_key_events, clear_key_event_queue, MAX_KEY_EVENT_QUEUE, ActionCallback) from any remaining files | Yes | 2026-01-03 |
| TASK-7100 | Update `types/__init__.py` if any deleted modules were referenced | Yes | 2026-01-03 |
| TASK-7200 | Update architecture documents to reflect Textual migration: (1) `keyboard-input.md` - replace prompt_toolkit implementation details (command_queue, command_pending, EventLoopState, key_event_queue) with Textual-based descriptions; update key naming examples to `ctrl+`/`shift+`/`alt+` format; remove the "Migration Note" section since migration is complete; (2) `manual-navigation.md` - update line 13 to say "Textual" instead of "Textual (migrating from prompt_toolkit)"; (3) `python-ui-enhancements.md` - update Historical Note to past tense; (4) `platyplaty-architecture-discussion-2.md` - update the framework comparison table to note that Textual was chosen and migration is complete | Yes | 2026-01-03 |

### Phase 120: Testing and Validation

- GOAL-1200: Verify the migration works correctly

| Task | Description | Completed | Date |
| -------- | --------------------- | --------- | ---- |
| TASK-7300 | Run the application and verify renderer starts | Yes | 2026-01-03 |
| TASK-7400 | Verify audio capture works | Yes | 2026-01-03 |
| TASK-7500 | Verify keybindings work in terminal (quit key) | Yes | 2026-01-03 |
| TASK-7600 | Verify keybindings work in renderer window (next/previous/quit) | Yes | 2026-01-03 |
| TASK-7700 | Verify auto-advance cycles through presets | Yes | 2026-01-03 |
| TASK-7800 | Verify log messages appear in RichLog widget | Yes | 2026-01-03 |
| TASK-7900 | Verify clean shutdown when pressing quit key | Yes | 2026-01-03 |
| TASK-8000 | Verify clean shutdown when closing renderer window | Yes | 2026-01-03 |
| TASK-8100 | Verify clean shutdown on Ctrl+C | Yes | 2026-01-03 |

## 3. Alternatives

- **ALT-100**: Minimal key input replacement - Replace only the terminal input layer with Textual equivalents while keeping the existing asyncio architecture. Rejected because it doesn't leverage Textual's strengths and would require another migration later.
- **ALT-200**: Keep shutdown_event alongside Textual cancellation - Maintain both shutdown mechanisms for safety. Rejected because it adds complexity and the analysis showed only a few files need changes.
- **ALT-300**: Keep actions as standalone functions instead of App methods - Would require passing app to each function and using dispatch callbacks. Rejected to use Textual's idiomatic action method pattern with `run_action()`.
- **ALT-400**: Keep prompt_toolkit key naming in renderer with Python translation layer - Would maintain renderer's existing key format and translate at the Python boundary. Rejected because updating the renderer is trivial (3 string literals) and eliminates the translation layer entirely.
- **ALT-500**: Keep reconnection logic - Maintain ability to recover from renderer crashes. Rejected for initial migration to reduce complexity; can be added back later with cleaner design.
- **ALT-600**: Blank screen or minimal status text only - Less UI work for initial migration. Rejected because log output is needed for debugging and user feedback.
- **ALT-700**: Keep custom key event queuing during command_pending - Queue key events in EventLoopState.key_event_queue while a socket command is in-flight, dispatch after response. Rejected because Textual has a built-in message queue that buffers key events automatically; the custom queuing adds complexity without benefit. Socket command serialization is handled by an internal lock in SocketClient.send_command(); key dispatch happens immediately.
- **ALT-800**: Full worker-based command handling (Option C) - Each action becomes a Textual worker with asyncio.Lock for command serialization. Rejected because it replaces one queuing mechanism with another more complex one (workers + locks) while gaining no real benefit. The socket protocol requires command serialization regardless of architecture.

## 4. Dependencies

- **DEP-100**: textual package (to be added via `uv add textual`)
- **DEP-200**: Existing socket_client.py module (adds _send_lock for command serialization)
- **DEP-300**: Existing playlist.py module (unchanged)
- **DEP-400**: Existing renderer.py module (unchanged)
- **DEP-500**: Existing netstring.py module (unchanged)

**Note:** The renderer (`platyplaty-renderer`) must be rebuilt after this migration to use the new Textual-format key names. Run `make` after completing Phase 30.

## 5. Files

- **FILE-0100**: `src/platyplaty/app.py` - New Textual App class with action methods and dispatch tables (created)
- **FILE-0200**: `src/platyplaty/messages.py` - New log message types (created)
- **FILE-0300**: `src/platyplaty/run_sequence.py` - Entry point update (modified)
- **FILE-0400**: `src/platyplaty/startup.py` - Remove output argument from run_startup_sequence call (modified)
- **FILE-0500**: `src/platyplaty/keybinding_dispatch.py` - Remove action functions, change dispatch tables to map keys to action names, update dispatch_key_event to use run_action (modified)
- **FILE-0600**: `src/platyplaty/event_loop.py` - Delete EventLoopState class; keep stderr_monitor_task, process_stderr_line, _handle_stderr_event functions (modified)
- **FILE-0700**: `src/platyplaty/stderr_parser.py` - Delete `log_audio_error()` function (modified)
- **FILE-0800**: `src/platyplaty/command_queue.py` - Delete entire file (deleted)
- **FILE-0900**: `src/platyplaty/auto_advance.py` - Worker pattern update (modified)
- **FILE-1000**: `src/platyplaty/socket_client.py` - Add _send_lock for command serialization (modified)
- **FILE-1100**: `src/platyplaty/types/keys.py` - Key naming convention (modified)
- **FILE-1200**: `src/platyplaty/types/config.py` - Validation messages (modified)
- **FILE-1300**: `conf/platyplaty-conf.toml` - Example config update (modified)
- **FILE-1400**: `pyproject.toml` - Dependencies (modified via uv commands)
- **FILE-1500**: `src/platyplaty/terminal_input.py` - (deleted)
- **FILE-1600**: `src/platyplaty/async_main.py` - (deleted)
- **FILE-1700**: `src/platyplaty/shutdown.py` - (deleted)
- **FILE-1800**: `src/platyplaty/reconnect.py` - (deleted)
- **FILE-1900**: `tests/client/test_reconnect.py` - (deleted)
- **FILE-2000**: `renderer/scancode_map.cpp` - Key naming convention update to Textual format (modified)
- **FILE-2100**: `tests/client/test_key_events.py` - (deleted)

## 6. Testing

- **TEST-0100**: Manual test: Application starts and displays status text and log panel
- **TEST-0200**: Manual test: Renderer window opens and displays visualizations
- **TEST-0300**: Manual test: Audio capture functions correctly
- **TEST-0400**: Manual test: Terminal quit keybinding triggers clean shutdown
- **TEST-0500**: Manual test: Renderer window next/previous/quit keybindings work
- **TEST-0600**: Manual test: Auto-advance cycles presets at configured interval
- **TEST-0700**: Manual test: Preset load failures appear in log panel
- **TEST-0800**: Manual test: Ctrl+C triggers clean shutdown
- **TEST-0900**: Manual test: Closing renderer window triggers client shutdown
- **TEST-1000**: Verify existing unit tests pass or update as needed

## 7. Risks & Assumptions

- **RISK-100**: Textual's worker cancellation timing may differ from explicit shutdown events, potentially causing race conditions during shutdown
- **RISK-200**: Breaking change to key naming in config files may confuse existing users
- **RISK-300**: Textual version updates may change key naming or worker APIs
- **ASSUMPTION-100**: Textual disables ISIG in termios settings, so terminal Ctrl+C arrives as a `ctrl+c` key event (not a SIGINT signal). Signal handlers registered via `loop.add_signal_handler()` are only needed for external signals (e.g., `kill -INT pid`). Both paths call `graceful_shutdown()` and the `_exiting` flag prevents double-shutdown
- **ASSUMPTION-200**: Workers receiving CancelledError will have time to clean up before the event loop stops
- **ASSUMPTION-300**: RichLog widget can handle the volume of log messages produced during operation
- **ASSUMPTION-400**: Textual's on_key event provides sufficient key information for keybinding dispatch

**Clarification on ASSUMPTION-200 (Worker Cancellation During Socket I/O):** When `app.exit()` is called, Textual cancels all running workers by raising `CancelledError` in their coroutines. This includes workers blocked on socket I/O (e.g., `await self._reader.read()`). Per the Textual documentation: "if you exit the app, any running tasks will be cancelled" and "This will raise a CancelledError within the coroutine." Per the Python asyncio documentation: "When a task is cancelled, asyncio.CancelledError will be raised in the task at the next opportunity" - any `await` is such an opportunity. Therefore, workers blocked on socket reads will be interrupted immediately when Textual cancels them; no timeout or special handling is required. This is standard asyncio behavior, not an assumption to be tested.

## 8. Related Specifications / Further Reading

- [reference/architecture/platyplaty-architecture-discussion.md](../reference/architecture/platyplaty-architecture-discussion.md) - Overall project architecture
- [reference/architecture/platyplaty-architecture-discussion-2.md](../reference/architecture/platyplaty-architecture-discussion-2.md) - Python UI brainstorming including Textual decision
- [Textual Documentation - Input](https://textual.textualize.io/guide/input/) - Key event handling
- [Textual Documentation - Workers](https://textual.textualize.io/guide/workers/) - Background task management
- [Textual Documentation - Events and Messages](https://textual.textualize.io/guide/events/) - Message passing between components
