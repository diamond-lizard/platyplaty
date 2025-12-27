---
goal: Implement GET STATUS command for renderer state querying
version: 1.0
date_created: 2025-12-27
last_updated: 2025-12-27
owner: platyplaty
status: 'Planned'
tags: [feature, stage-5, renderer, client]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement the GET STATUS command (Stage 5) to allow the Python client to query current renderer state. This enables efficient reconnection by skipping redundant commands and synchronizing client state with the running renderer.

## 1. Requirements & Constraints

- **REQ-100**: GET STATUS returns five fields: `audio_source`, `audio_connected`, `preset_path`, `visible`, `fullscreen`
- **REQ-200**: GET STATUS only works after INIT; returns error "command not allowed before INIT" otherwise
- **REQ-300**: GET STATUS cannot fail after INIT (always returns success with current state)
- **REQ-400**: Response uses flat JSON structure with all fields always present
- **REQ-500**: `preset_path` is empty string if no preset has been loaded yet
- **REQ-600**: `audio_source` reports configured source even if audio has since disconnected
- **REQ-700**: `audio_connected` reports whether audio is currently active (not just configured)
- **CON-100**: libprojectM 4.1.6 has no API to query current preset path; must track it ourselves
- **CON-200**: `m_source` in AudioCapture is immutable after construction (thread-safe to read without synchronization)
- **CON-300**: `m_audio_error` must be `std::atomic<bool>` since it's set by audio thread and read by main thread
- **GUD-100**: Use component-owned state pattern; each component exposes its own state via getters
- **GUD-200**: Query SDL directly for window state (`is_visible()`, `is_fullscreen()`) rather than tracking member variables
- **PAT-100**: Command follows same processing pattern as other post-INIT commands

## 2. Implementation Steps

### Phase 1: Renderer Component Getters

- GOAL-0100: Add state getter methods to renderer components (AudioCapture, Visualizer, Window)

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-0100 | In `audio_capture.hpp`: Add `std::atomic<bool> m_audio_error{false}` member in private section | | |
| TASK-0200 | In `audio_capture.hpp`: Add public method declaration `const std::string& get_source() const` | | |
| TASK-0300 | In `audio_capture.hpp`: Add public method declaration `bool is_connected() const` | | |
| TASK-0400 | In `audio_capture.cpp`: In `capture_loop()`, set `m_audio_error = true` immediately before the `break` statement that follows the `emit_stderr_event("AUDIO_ERROR", ...)` call | | |
| TASK-0500 | In `audio_capture.cpp`: Add implementation of `get_source()` returning `m_source` | | |
| TASK-0600 | In `audio_capture.cpp`: Add implementation of `is_connected()` returning `!m_audio_error.load()` | | |
| TASK-0700 | In `visualizer.hpp`: Add `std::string m_current_preset_path` member in private section | | |
| TASK-0800 | In `visualizer.hpp`: Add public method declaration `const std::string& get_current_preset_path() const` | | |
| TASK-0900 | In `visualizer.cpp`: In `load_preset()`, store `path` in `m_current_preset_path` immediately before `return {true, ""}` (only on success) | | |
| TASK-1000 | In `visualizer.cpp`: Add implementation of `get_current_preset_path()` returning `m_current_preset_path` | | |
| TASK-1100 | In `window.hpp`: Add public method declaration `bool is_fullscreen() const` | | |
| TASK-1200 | Verify `m_visible` member exists in `window.hpp` and `m_visible = true` exists in `window.cpp` before attempting removal | | |
| TASK-1300 | In `window.hpp`: Remove `bool m_visible` member declaration (will query SDL instead) | | |
| TASK-1400 | In `window.cpp`: Modify `is_visible()` to query SDL via `SDL_GetWindowFlags(m_window) & SDL_WINDOW_SHOWN` instead of returning `m_visible` | | |
| TASK-1500 | In `window.cpp`: Remove `m_visible = true` from `show()` method (now dead code) | | |
| TASK-1600 | In `window.cpp`: Add implementation of `is_fullscreen()` returning `SDL_GetWindowFlags(m_window) & SDL_WINDOW_FULLSCREEN_DESKTOP` | | |
| TASK-1700 | Verify C++ build: Run `make` to ensure renderer compiles without errors | | |

### Phase 2: Protocol Layer Updates

- GOAL-0200: Register GET STATUS command in the protocol layer

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-1800 | In `protocol.hpp`: Add `GET_STATUS` to the `CommandType` enum (after existing entries) | | |
| TASK-1900 | In `protocol.cpp`: Add `"GET STATUS"` to the `VALID_COMMANDS` set | | |
| TASK-2000 | In `protocol.cpp`: Add `case` for `"GET STATUS"` in `string_to_command_type()` returning `CommandType::GET_STATUS` | | |
| TASK-2100 | In `protocol.cpp`: Add `case CommandType::GET_STATUS:` in `allowed_fields()` returning empty set `{}` (like INIT/QUIT) | | |
| TASK-2200 | Verify C++ build: Run `make` to ensure renderer compiles without errors | | |

### Phase 3: Command Handler and Event Loop Signature Changes

- GOAL-0300: Thread AudioCapture reference through to command handler for GET STATUS access

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-2300 | In `event_loop.hpp`: Add forward declaration `class AudioCapture;` | | |
| TASK-2400 | In `event_loop.hpp`: Update `run_event_loop()` declaration to add `AudioCapture& audio` parameter after existing parameters | | |
| TASK-2500 | In `event_loop.cpp`: Update `run_event_loop()` definition to add `AudioCapture& audio` parameter | | |
| TASK-2600 | In `event_loop.cpp`: Pass `audio` through to `handle_command()` call | | |
| TASK-2700 | In `command_handler.hpp`: Update `handle_command()` declaration to add `AudioCapture& audio` parameter | | |
| TASK-2800 | In `command_handler.cpp`: Add `#include "audio_capture.hpp"` | | |
| TASK-2900 | In `command_handler.cpp`: Update `handle_command()` definition to add `AudioCapture& audio` parameter | | |
| TASK-3000 | In `main.cpp`: Update `run_event_loop()` call to pass `audio_capture` as additional argument | | |
| TASK-3100 | Verify C++ build: Run `make` to ensure renderer compiles without errors | | |

### Phase 4: GET STATUS Command Implementation

- GOAL-0400: Implement the GET STATUS command handler that builds response from component getters

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-3200 | In `command_handler.cpp`: Add `case CommandType::GET_STATUS:` block in the command switch | | |
| TASK-3300 | In GET_STATUS case: Create `nlohmann::json data` object with fields: `data["audio_source"] = audio.get_source()`, `data["audio_connected"] = audio.is_connected()`, `data["preset_path"] = visualizer.get_current_preset_path()`, `data["visible"] = window.is_visible()`, `data["fullscreen"] = window.is_fullscreen()` | | |
| TASK-3400 | In GET_STATUS case: Return success response with data using `make_response(cmd.id, true, "", data)` or equivalent pattern | | |
| TASK-3500 | Verify C++ build: Run `make` to ensure renderer compiles without errors | | |

### Phase 5: Dead Code Cleanup

- GOAL-0500: Remove dead code (renderer_state.hpp is unused)

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-3600 | Delete file `renderer/renderer_state.hpp` entirely (RendererPhase and RendererState are defined but never used) | | |
| TASK-3700 | Verify C++ build: Run `make` to ensure renderer compiles without errors | | |

### Phase 6: Documentation Update

- GOAL-0600: Update protocol documentation with GET STATUS command

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-3800 | In `reference/architecture/communication-protocol.md`: Add GET STATUS to command table with row: `\| \`GET STATUS\` \| (none) \| Query current renderer state \| Stage 5 \|` | | |

### Phase 7: Python Type Definitions

- GOAL-0700: Create types/ directory structure and add StatusData model

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-3900 | Verify which Python files import `CommandResponse`, `Config`, and `StderrEvent`; update Phase 8 task list if needed | | |
| TASK-4000 | Create directory `src/platyplaty/types/` | | |
| TASK-4100 | Create `src/platyplaty/types/__init__.py` that re-exports all types for convenient imports | | |
| TASK-4200 | Create `src/platyplaty/types/socket.py` with `StatusData` Pydantic model: fields `audio_source: str`, `audio_connected: bool`, `preset_path: str`, `visible: bool`, `fullscreen: bool` | | |
| TASK-4300 | In `types/socket.py`: Migrate `CommandResponse` class from its current location | | |
| TASK-4400 | Create `src/platyplaty/types/config.py` and migrate `Config` class from its current location | | |
| TASK-4500 | Create `src/platyplaty/types/events.py` and migrate `StderrEvent` class from its current location | | |
| TASK-4600 | Update `types/__init__.py` to re-export `StatusData`, `CommandResponse`, `Config`, `StderrEvent` | | |
| TASK-4700 | Verify Python syntax: Run `python3 -m py_compile` on all new Python files in `types/` | | |

### Phase 8: Python Import Updates

- GOAL-0800: Update imports in all files that use migrated types

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-4800 | Update imports in `async_main.py` to use `from platyplaty.types import ...` | | |
| TASK-4900 | Update imports in `auto_advance.py` to use `from platyplaty.types import ...` | | |
| TASK-5000 | Update imports in `event_loop.py` to use `from platyplaty.types import ...` | | |
| TASK-5100 | Update imports in `run_sequence.py` to use `from platyplaty.types import ...` | | |
| TASK-5200 | Update imports in `startup.py` to use `from platyplaty.types import ...` | | |
| TASK-5300 | Update imports in `reconnect.py` to use `from platyplaty.types import ...` | | |
| TASK-5400 | Update imports in `shutdown.py` to use `from platyplaty.types import ...` | | |
| TASK-5500 | Verify Python syntax: Run `python3 -m py_compile` on all modified Python files | | |

### Phase 9: Reconnect Logic Refactoring

- GOAL-0900: Replace reconnect startup sequence with GET STATUS-based state synchronization

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-5600 | In `reconnect.py`: Add new function `async def _sync_state_from_status(client: SocketClient, playlist: Playlist, fullscreen: bool, output: TextIO) -> bool` | | |
| TASK-5700 | Document return value contract in docstring: Returns `True` if GET STATUS succeeds and sync commands complete; returns `False` if GET STATUS fails or critical sync commands fail; `audio_connected: false` is a warning, not a failure | | |
| TASK-5800 | In `_sync_state_from_status`: Send GET STATUS command via `client.send_command("GET STATUS")` | | |
| TASK-5900 | In `_sync_state_from_status`: Parse response with `StatusData.model_validate(response.data)` after checking `response.success` | | |
| TASK-6000 | In `_sync_state_from_status`: If `status.audio_connected` is false, log warning "Audio disconnected, visualization may be unresponsive to music" to output and continue | | |
| TASK-6100 | In `_sync_state_from_status`: Compare `status.preset_path` with `str(playlist.current())`; only send LOAD PRESET if different | | |
| TASK-6200 | In `_sync_state_from_status`: Check `status.visible`; only send SHOW WINDOW if not visible | | |
| TASK-6300 | In `_sync_state_from_status`: Check `status.fullscreen != fullscreen`; only send SET FULLSCREEN if different | | |
| TASK-6400 | In `reconnect.py`: Update `attempt_reconnect()` to remove `audio_source` parameter (no longer needed) | | |
| TASK-6500 | In `reconnect.py`: Update `attempt_reconnect()` to call `_sync_state_from_status()` instead of `_run_startup_sequence()` | | |
| TASK-6600 | In `reconnect.py`: Delete `_run_startup_sequence()` function (now dead code) | | |
| TASK-6700 | In `reconnect.py`: Delete `_send_audio_source()` helper function (now dead code) | | |
| TASK-6800 | In `reconnect.py`: Delete `_send_init()` helper function (now dead code) | | |
| TASK-6900 | In `reconnect.py`: Delete `_load_current_preset()` helper function (now dead code) | | |
| TASK-7000 | In `reconnect.py`: Delete `_show_window()` helper function (now dead code) | | |
| TASK-7100 | In `async_main.py`: Update call to `attempt_reconnect()` to remove `audio_source` argument | | |
| TASK-7200 | Verify Python syntax: Run `python3 -m py_compile` on all modified Python files | | |

### Phase 10: Renderer Tests

- GOAL-1000: Implement renderer tests for GET STATUS command

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-7300 | Create `tests/renderer/test_get_status.py` test file | | |
| TASK-7400 | Add test: GET STATUS before INIT returns error "command not allowed before INIT" | | |
| TASK-7500 | Add test: GET STATUS after INIT returns success with all 5 fields present | | |
| TASK-7600 | Add test: `audio_source` matches value from CHANGE AUDIO SOURCE command | | |
| TASK-7700 | Add test: `audio_connected` is true when audio is active (query PulseAudio for available sources and use the first monitor source) | | |
| TASK-7800 | Manual test: Verify `audio_connected` is false after disconnecting audio device or stopping PulseAudio source | | |
| TASK-7900 | Add test: `preset_path` is empty string before any LOAD PRESET | | |
| TASK-8000 | Add test: `preset_path` matches last successful LOAD PRESET path | | |
| TASK-8100 | Add test: `preset_path` remains unchanged after a failed LOAD PRESET | | |
| TASK-8200 | Add test: `visible` reflects SHOW WINDOW state (false initially, true after SHOW WINDOW) | | |
| TASK-8300 | Add test: `fullscreen` reflects SET FULLSCREEN state | | |

### Phase 11: Client Tests

- GOAL-1100: Implement client tests for reconnect logic

| Task      | Description | Completed | Date |
| --------- | ----------- | --------- | ---- |
| TASK-8400 | Create `tests/client/` directory | | |
| TASK-8500 | Create `tests/client/test_reconnect.py` test file | | |
| TASK-8600 | Add test: `send_command("GET STATUS")` parses response correctly into StatusData | | |
| TASK-8700 | Add test: Reconnect uses GET STATUS to skip redundant commands | | |
| TASK-8800 | Add test: Reconnect sends LOAD PRESET only if preset differs from current | | |

## 3. Alternatives

- **ALT-100**: Centralized RendererState struct to hold all state. Rejected because it creates synchronization issues and violates component-owned state pattern.
- **ALT-200**: Track window visibility via member variable instead of querying SDL. Rejected because SDL query is always accurate even if user toggles fullscreen externally.
- **ALT-300**: Include `phase` field in GET STATUS response. Rejected because GET STATUS only works after INIT, so phase is always "RUNNING" and provides no information.

## 4. Dependencies

- **DEP-100**: libprojectM 4.1.6 (existing dependency)
- **DEP-200**: SDL2 (existing dependency, used for SDL_GetWindowFlags)
- **DEP-300**: nlohmann/json (existing dependency, used for response building)
- **DEP-400**: Pydantic (existing Python dependency, used for StatusData model)

## 5. Files

- **FILE-0100**: `renderer/audio_capture.hpp` - Add m_audio_error, get_source(), is_connected()
- **FILE-0200**: `renderer/audio_capture.cpp` - Set m_audio_error, implement getters
- **FILE-0300**: `renderer/visualizer.hpp` - Add m_current_preset_path, get_current_preset_path()
- **FILE-0400**: `renderer/visualizer.cpp` - Store path on success, implement getter
- **FILE-0500**: `renderer/window.hpp` - Add is_fullscreen(), remove m_visible
- **FILE-0600**: `renderer/window.cpp` - Modify is_visible() to query SDL, add is_fullscreen(), remove m_visible usage
- **FILE-0700**: `renderer/protocol.hpp` - Add GET_STATUS to CommandType enum
- **FILE-0800**: `renderer/protocol.cpp` - Register GET STATUS in VALID_COMMANDS, string_to_command_type(), allowed_fields()
- **FILE-0900**: `renderer/event_loop.hpp` - Add AudioCapture forward declaration, update run_event_loop() signature
- **FILE-1000**: `renderer/event_loop.cpp` - Update run_event_loop() to pass AudioCapture to handle_command()
- **FILE-1100**: `renderer/command_handler.hpp` - Update handle_command() signature
- **FILE-1200**: `renderer/command_handler.cpp` - Add include, update signature, implement GET_STATUS case
- **FILE-1300**: `renderer/main.cpp` - Pass audio_capture to run_event_loop()
- **FILE-1400**: `renderer/renderer_state.hpp` - DELETE (dead code)
- **FILE-1500**: `reference/architecture/communication-protocol.md` - Add GET STATUS to command table
- **FILE-1600**: `src/platyplaty/types/__init__.py` - Create, re-export all types
- **FILE-1700**: `src/platyplaty/types/socket.py` - Create, add StatusData, migrate CommandResponse
- **FILE-1800**: `src/platyplaty/types/config.py` - Create, migrate Config
- **FILE-1900**: `src/platyplaty/types/events.py` - Create, migrate StderrEvent
- **FILE-2000**: `src/platyplaty/reconnect.py` - Replace _run_startup_sequence with _sync_state_from_status, remove audio_source param
- **FILE-2100**: `src/platyplaty/async_main.py` - Update attempt_reconnect() call, update imports
- **FILE-2200**: `src/platyplaty/auto_advance.py` - Update imports
- **FILE-2300**: `src/platyplaty/event_loop.py` - Update imports
- **FILE-2400**: `src/platyplaty/run_sequence.py` - Update imports
- **FILE-2500**: `src/platyplaty/startup.py` - Update imports
- **FILE-2600**: `src/platyplaty/shutdown.py` - Update imports
- **FILE-2700**: `tests/renderer/test_get_status.py` - Create renderer tests
- **FILE-2800**: `tests/client/test_reconnect.py` - Create client tests

## 6. Testing

- **TEST-0100**: GET STATUS before INIT returns error "command not allowed before INIT"
- **TEST-0200**: GET STATUS after INIT returns success with all 5 fields
- **TEST-0300**: `audio_source` matches CHANGE AUDIO SOURCE value
- **TEST-0400**: `audio_connected` is true when audio active, false after AUDIO_ERROR
- **TEST-0500**: `preset_path` empty before LOAD PRESET
- **TEST-0600**: `preset_path` matches last successful LOAD PRESET
- **TEST-0700**: `preset_path` unchanged after failed LOAD PRESET
- **TEST-0800**: `visible` reflects SHOW WINDOW state
- **TEST-0900**: `fullscreen` reflects SET FULLSCREEN state
- **TEST-1000**: Python StatusData.model_validate() parses GET STATUS response correctly
- **TEST-1100**: Reconnect skips redundant commands based on GET STATUS
- **TEST-1200**: Reconnect sends LOAD PRESET only when preset differs

## 7. Risks & Assumptions

- **RISK-100**: If audio thread sets m_audio_error after GET STATUS reads it, the response may be slightly stale. Mitigation: Acceptable because next GET STATUS will show correct value; no critical decisions depend on this.
- **RISK-200**: SDL_GetWindowFlags() behavior may differ across platforms. Mitigation: Test on target platform (Linux with SDL2).
- **ASSUMPTION-100**: renderer_state.hpp is truly dead code and can be safely deleted
- **ASSUMPTION-200**: All listed Python files exist and use the types being migrated
- **ASSUMPTION-300**: Pydantic is already a dependency of the Python client

## 8. Related Specifications / Further Reading

- [status-command.md](../reference/architecture/status-command.md) - Original specification
- [communication-protocol.md](../reference/architecture/communication-protocol.md) - Protocol documentation
- [integration-contracts-december-2025.md](../reference/architecture/integration-contracts-december-2025.md) - Threading model
- [robustness-philosophy-december-2025.md](../reference/architecture/robustness-philosophy-december-2025.md) - Error handling philosophy
