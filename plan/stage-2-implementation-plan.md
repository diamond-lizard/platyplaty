---
goal: Implement Stage 2 - Socket IPC, Audio Capture, and Two-Phase Initialization
version: 1.0
date_created: 2025-12-24
last_updated: 2025-12-24
owner: Platyplaty Development Team
status: 'Planned'
tags: [feature, architecture, ipc, audio]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan implements Stage 2 of the Platyplaty renderer, adding Unix domain socket IPC with netstring framing, PulseAudio capture, and two-phase initialization. The renderer will print `SOCKET READY\n` after creating the listening socket, then wait for `CHANGE AUDIO SOURCE` and `INIT` commands before completing initialization.

## 1. Requirements & Constraints

### Architectural Requirements (from platyplaty-architecture-discussion.md)

- **REQ-0100**: Renderer initializes in two phases: Phase 1 creates socket and prints `SOCKET READY\n`; Phase 2 (triggered by `INIT` command) creates window, projectM, and audio thread
- **REQ-0200**: Client must send `CHANGE AUDIO SOURCE` before `INIT`; sending `INIT` without prior `CHANGE AUDIO SOURCE` is fatal
- **REQ-0300**: Commands use netstring framing: `<length>:<json>,` with 64KB max payload
- **REQ-0400**: Responses use same netstring framing; format is `{"id": N, "success": true/false, "data": {}/"error": "msg"}`
- **REQ-0500**: Socket thread uses single command slot (not queue); blocks until main thread processes command
- **REQ-0600**: Audio uses PulseAudio async API with 44100 Hz, stereo, float32 format
- **REQ-0700**: Audio buffer size ~735 samples (~16.7ms) for low-latency synchronization
- **REQ-0800**: Socket path resolution: `$XDG_RUNTIME_DIR/platyplaty.sock` > `$TEMPDIR/platyplaty-<uid>.sock` > `$TMPDIR/platyplaty-<uid>.sock` > `/tmp/platyplaty-<uid>.sock`
- **REQ-0900**: `CHANGE AUDIO SOURCE` after `INIT` returns error response (rejected)
- **REQ-1000**: Audio errors are fatal; audio thread sets shutdown flag and exits
- **REQ-1100**: Socket errors and clean EOF both trigger shutdown; errors log to stderr, EOF exits silently
- **REQ-1200**: Malformed netstrings cause client disconnect (fatal); malformed JSON returns error response (non-fatal)
- **REQ-1300**: Missing `id` field or wrong parameter types cause client disconnect
- **REQ-1400**: Unrecognized fields in commands cause client disconnect (catches typos)
- **REQ-1500**: Zero-length netstrings rejected with error response before JSON parsing
- **REQ-1600**: Relative paths in `LOAD PRESET` cause client disconnect
- **REQ-1700**: nlohmann/json library vendored at `renderer/vendor/nlohmann/json.hpp`

### Code Style Requirements

- **STY-0100**: Follow `reference/cppbestpractices-as-text.txt` for all C++ code
- **STY-0200**: Follow `reference/generic-cpp-project-outline.org` for project structure
- **STY-0300**: Files should be under 100 lines; up to ~150 is acceptable for cohesive modules
- **STY-0400**: Maximum 3 levels of indentation; use early returns and helper functions
- **STY-0500**: Use RAII for all resource management
- **STY-0600**: Use exceptions for initialization failures; constructors throw `std::runtime_error`
- **STY-0700**: Use `const` liberally; pass complex types by `const&`
- **STY-0800**: Use `std::size_t` for sizes; use `'\n'` not `"\n"` for single chars
- **STY-0900**: Mark single-parameter constructors `explicit`
- **STY-1000**: Use member initializer lists; prefer brace initialization

### Constraints

- **CON-100**: Must use installed libprojectM from `/usr/local/apps/libprojectm/` via pkg-config
- **CON-200**: Must not include or build against reference source tree
- **CON-300**: Stage 1 functionality must continue to work during development
- **CON-400**: Renderer stdout reserved for protocol messages (`SOCKET READY`); diagnostics go to stderr

### Guidelines

- **GUD-100**: Test incrementally after each component
- **GUD-200**: Keep socket thread and audio thread logic minimal; delegate to main thread
- **GUD-300**: Use atomic shutdown flag pattern established in Stage 1

## 2. Implementation Steps

### Implementation Phase 1: Vendor nlohmann/json and Create Netstring Module

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-100: Add JSON parsing capability and implement netstring framing

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-0100 | Download nlohmann/json single-header (v3.11.3) to `renderer/vendor/nlohmann/json.hpp`; add version comment at top of file | | |
| TASK-0200 | Create `renderer/netstring.hpp`: declare `struct NetstringParseResult { bool success; std::string payload; std::string error; }` and parsing/serialization function signatures | | |
| TASK-0300 | Create `renderer/netstring.cpp`: implement `NetstringParseResult parse_netstring(const std::string& input, std::size_t& bytes_consumed)` with validation (max 5 digits, no leading zeros, max 64KB payload) | | |
| TASK-0400 | Implement `std::string serialize_netstring(const std::string& payload)` in `renderer/netstring.cpp` | | |
| TASK-0500 | Add netstring source files to Makefile `SOURCES` (should be automatic via wildcard) | | |
| TASK-0600 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 2: Create Protocol Types and Command Structures

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-200: Define command and response structures with JSON serialization

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-0700 | Create `renderer/protocol.hpp`: define `enum class CommandType { CHANGE_AUDIO_SOURCE, INIT, LOAD_PRESET, SHOW_WINDOW, SET_FULLSCREEN, QUIT, UNKNOWN }` | | |
| TASK-0800 | In `renderer/protocol.hpp`: define `struct Command { CommandType type; int id; std::string audio_source; std::string preset_path; bool fullscreen_enabled; }` with sensible defaults | | |
| TASK-0900 | In `renderer/protocol.hpp`: define `struct Response { int id; bool success; std::string error; }` and `struct CommandParseResult { bool success; Command command; std::string error; }` | | |
| TASK-1000 | Create `renderer/protocol.cpp`: implement `CommandParseResult parse_command(const std::string& json)` using nlohmann/json; validate required fields, reject unknown fields | | |
| TASK-1100 | In `renderer/protocol.cpp`: implement `std::string serialize_response(const Response& response)` | | |
| TASK-1200 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 3: Create Socket Module

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-300: Implement Unix domain socket server with RAII

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-1300 | Create `renderer/socket_path.hpp`: declare `std::string get_socket_path()` function | | |
| TASK-1400 | Create `renderer/socket_path.cpp`: implement socket path resolution per REQ-0800 (XDG_RUNTIME_DIR > TEMPDIR > TMPDIR > /tmp) with uid suffix where needed | | |
| TASK-1500 | Create `renderer/server_socket.hpp`: declare RAII `ServerSocket` class with constructor taking path, `accept_client()` method, and `get_fd()` accessor | | |
| TASK-1600 | Create `renderer/server_socket.cpp`: implement `ServerSocket` constructor (create, bind, listen); destructor (close, unlink); throw on failure | | |
| TASK-1700 | Create `renderer/client_socket.hpp`: declare RAII `ClientSocket` class with `send()`, `recv()`, `get_fd()`, and `close()` methods | | |
| TASK-1800 | Create `renderer/client_socket.cpp`: implement `ClientSocket` wrapping accepted fd; `send()` writes netstring; `recv()` buffers partial reads and returns complete netstring payloads | | |
| TASK-1900 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 4: Create Command Slot for Thread Communication

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-400: Implement single-slot command handoff between socket thread and main thread

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-2000 | Create `renderer/command_slot.hpp`: declare `CommandSlot` class with `std::mutex`, `std::condition_variable`, `std::optional<Command>`, and `std::optional<Response>` | | |
| TASK-2100 | In `renderer/command_slot.hpp`: declare methods `void put_command(Command cmd)`, `std::optional<Command> try_get_command()`, `void put_response(Response resp)`, `bool wait_for_response(Response& out, std::chrono::milliseconds timeout)` | | |
| TASK-2200 | Create `renderer/command_slot.cpp`: implement `put_command()` - sets command, notifies CV; blocks until response arrives or shutdown | | |
| TASK-2300 | In `renderer/command_slot.cpp`: implement `try_get_command()` - non-blocking check for pending command | | |
| TASK-2400 | In `renderer/command_slot.cpp`: implement `put_response()` and `wait_for_response()` with ~100ms timeout for shutdown responsiveness | | |
| TASK-2500 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 5: Create Socket Thread

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-500: Implement socket thread that accepts one client and processes commands

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-2600 | Create `renderer/socket_thread.hpp`: declare `SocketThread` class with `std::thread`, reference to `CommandSlot`, socket path, and `start()`/`join()` methods | | |
| TASK-2700 | Create `renderer/socket_thread.cpp`: implement constructor that creates `ServerSocket` and stores path for later cleanup | | |
| TASK-2800 | In `renderer/socket_thread.cpp`: implement `start()` that spawns thread running `thread_main()` | | |
| TASK-2900 | In `renderer/socket_thread.cpp`: implement `thread_main()` state machine: wait for client, poll both sockets, read messages, parse netstrings, validate JSON, put commands in slot, send responses | | |
| TASK-3000 | In `renderer/socket_thread.cpp`: implement defensive rejection of second client connections (accept and immediately close) | | |
| TASK-3100 | In `renderer/socket_thread.cpp`: implement protocol error handling - disconnect on malformed netstring, missing id, unknown fields; error response on malformed JSON | | |
| TASK-3200 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 6: Create Audio Capture Module

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-600: Implement PulseAudio capture with async API

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-3300 | Update Makefile: add `pkg-config --cflags --libs libpulse` to compiler/linker flags | | |
| TASK-3400 | Create `renderer/audio_capture.hpp`: declare `AudioCapture` class with constructor taking source name and `Visualizer&`, `start()`/`stop()`/`join()` methods | | |
| TASK-3500 | Create `renderer/audio_capture.cpp`: implement constructor - create PulseAudio mainloop, context; set up state callback | | |
| TASK-3600 | In `renderer/audio_capture.cpp`: implement `start()` - connect context, create recording stream with 44100Hz stereo float32, ~735 sample buffer; spawn capture thread | | |
| TASK-3700 | In `renderer/audio_capture.cpp`: implement capture thread - poll with ~100ms timeout, read samples, call `Visualizer::add_audio_samples()`, check shutdown flag | | |
| TASK-3800 | In `renderer/audio_capture.cpp`: implement `stop()` - set shutdown flag; `join()` - wait for thread; destructor - cleanup PulseAudio resources in reverse order | | |
| TASK-3900 | In `renderer/audio_capture.cpp`: implement error handling - any PulseAudio error sets global `g_shutdown_requested` flag (fatal per REQ-1000) | | |
| TASK-4000 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 7: Refactor Main for Two-Phase Initialization

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-700: Restructure main() for two-phase initialization and command processing

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-4100 | Create `renderer/renderer_state.hpp`: declare enum `RendererPhase { WAITING_FOR_CONFIG, WAITING_FOR_INIT, RUNNING }` and state tracking struct | | |
| TASK-4200 | Refactor `main.cpp`: Phase 1 - setup signal handlers, create `CommandSlot`, create and start `SocketThread`, print `SOCKET READY\n` to stdout, flush | | |
| TASK-4300 | In `main.cpp`: implement pre-init command loop - poll `CommandSlot`, handle `CHANGE AUDIO SOURCE` (store source, respond success), reject other commands except `INIT` | | |
| TASK-4400 | In `main.cpp`: on `INIT` command - verify audio source was set (fatal if not), create Window, create Visualizer, create AudioCapture with stored source, respond success | | |
| TASK-4500 | In `main.cpp`: modify event loop to check `CommandSlot` each frame; dispatch to command handler | | |
| TASK-4600 | Create `renderer/command_handler.hpp`: declare `Response handle_command(const Command& cmd, Visualizer& viz, Window& win, bool& running)` | | |
| TASK-4700 | Create `renderer/command_handler.cpp`: implement command dispatch - `LOAD_PRESET`, `SHOW_WINDOW`, `SET_FULLSCREEN`, `QUIT`; return error for `CHANGE_AUDIO_SOURCE` and `INIT` and `UNKNOWN` (invalid after initialization); return appropriate responses | | |
| TASK-4800 | In `command_handler.cpp`: implement `LOAD_PRESET` - validate absolute path (disconnect if relative), delegate to `Visualizer::load_preset()` | | |
| TASK-4900 | In `command_handler.cpp`: implement `SHOW_WINDOW` - call `SDL_ShowWindow()`, idempotent; `SET_FULLSCREEN` - error if window not visible, otherwise set fullscreen state (idempotent) | | |
| TASK-5000 | In `command_handler.cpp`: implement `QUIT` - set running=false, return success | | |
| TASK-5100 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 8: Update Shutdown Coordination

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-800: Ensure clean shutdown from all trigger sources

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-5200 | Review shutdown flag usage: main loop, socket thread, audio thread all check `g_shutdown_requested` | | |
| TASK-5300 | Update `main.cpp` shutdown sequence: set flag, join audio thread, join socket thread, close sockets, destroy projectM, destroy SDL | | |
| TASK-5400 | Ensure socket thread exits cleanly on EOF (client disconnect) - set shutdown flag, exit thread | | |
| TASK-5500 | Ensure audio thread exits cleanly on PulseAudio error - set shutdown flag, exit thread | | |
| TASK-5600 | Add `atexit()` handler to unlink socket file (store path in static variable per architecture doc) | | |
| TASK-5700 | Test shutdown paths: QUIT command, window close, SIGINT, SIGTERM, client disconnect | | |
| TASK-5800 | Run `make test-renderer` and fix any issues revealed by cppcheck | | |

### Implementation Phase 9: Integration Testing and Cleanup

**CRITICAL EDITING INSTRUCTIONS**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly. Make only ONE edit at a time. Edit files BOTTOM-UP (last line first). ALWAYS insert ALL leading whitespace programmatically using the documented techniques. Never type literal spaces or tabs for indentation.

**CODE STYLE**: Follow `reference/cppbestpractices-as-text.txt` and `reference/generic-cpp-project-outline.org` strictly. Keep files under ~150 lines (100 preferred). Use RAII. Use `const` liberally. Prefer brace initialization.

- GOAL-900: Verify complete Stage 2 functionality

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-5900 | Create `bin/test-stage2.py`: simple Python script that connects to socket, sends CHANGE AUDIO SOURCE, INIT, LOAD PRESET, SHOW WINDOW, waits, sends QUIT | | |
| TASK-6000 | Test error paths: missing CHANGE AUDIO SOURCE before INIT, unknown command, malformed JSON, invalid netstring | | |
| TASK-6100 | Test audio: verify visualization responds to audio input from default sink monitor | | |
| TASK-6200 | Verify all files are under ~150 lines; split any that exceed unless cohesive | | |
| TASK-6300 | Verify no more than 3 levels of indentation in any file | | |
| TASK-6400 | Review all headers for proper include guards and minimal includes | | |
| TASK-6500 | Run `make test-renderer` and fix any remaining issues | | |

## 3. Alternatives

- **ALT-100**: Using a command queue instead of single slot - rejected because the synchronous protocol guarantees at most one pending command; a queue adds unnecessary complexity
- **ALT-200**: Using synchronous PulseAudio API - rejected because it blocks and doesn't integrate well with the threaded architecture
- **ALT-300**: Using ZeroMQ or other message library for IPC - rejected to minimize dependencies; Unix domain sockets with netstrings are simple and sufficient
- **ALT-400**: Using CMake instead of Makefile - deferred; current Makefile is simple and sufficient for MVP

## 4. Dependencies

- **DEP-100**: nlohmann/json (v3.11.3) - vendored single header at `renderer/vendor/nlohmann/json.hpp`
- **DEP-200**: libpulse (PulseAudio client library) - system package, linked via pkg-config
- **DEP-300**: Stage 1 components (Window, Visualizer, shutdown, event_loop) - must remain functional

## 5. Files

### New Files

- **FILE-0100**: `renderer/vendor/nlohmann/json.hpp` - Vendored JSON library
- **FILE-0200**: `renderer/netstring.hpp` - Netstring parsing/serialization declarations
- **FILE-0300**: `renderer/netstring.cpp` - Netstring implementation
- **FILE-0400**: `renderer/protocol.hpp` - Command/Response type declarations
- **FILE-0500**: `renderer/protocol.cpp` - JSON parsing/serialization implementation
- **FILE-0600**: `renderer/socket_path.hpp` - Socket path resolution declaration
- **FILE-0700**: `renderer/socket_path.cpp` - Socket path resolution implementation
- **FILE-0800**: `renderer/server_socket.hpp` - Server socket RAII wrapper declaration
- **FILE-0900**: `renderer/server_socket.cpp` - Server socket implementation
- **FILE-1000**: `renderer/client_socket.hpp` - Client socket RAII wrapper declaration
- **FILE-1100**: `renderer/client_socket.cpp` - Client socket implementation
- **FILE-1200**: `renderer/command_slot.hpp` - Thread-safe command handoff declaration
- **FILE-1300**: `renderer/command_slot.cpp` - Command slot implementation
- **FILE-1400**: `renderer/socket_thread.hpp` - Socket thread declaration
- **FILE-1500**: `renderer/socket_thread.cpp` - Socket thread implementation
- **FILE-1600**: `renderer/audio_capture.hpp` - PulseAudio capture declaration
- **FILE-1700**: `renderer/audio_capture.cpp` - PulseAudio capture implementation
- **FILE-1800**: `renderer/renderer_state.hpp` - Renderer state enum and tracking
- **FILE-1900**: `renderer/command_handler.hpp` - Command handling declaration
- **FILE-2000**: `renderer/command_handler.cpp` - Command handling implementation
- **FILE-2100**: `bin/test-stage2.py` - Integration test script

### Modified Files

- **FILE-2200**: `renderer/main.cpp` - Refactored for two-phase initialization
- **FILE-2300**: `renderer/window.hpp` - Add `show()`, `set_fullscreen()`, and `is_visible()` methods with visibility tracking
- **FILE-2400**: `renderer/window.cpp` - Implement new window control methods; add SDL_WINDOW_HIDDEN to initial flags
- **FILE-2500**: `renderer/visualizer.hpp` - Add inline add_audio_samples() method for audio thread
- **FILE-2600**: `Makefile` - Add libpulse to pkg-config flags

## 6. Testing

- **TEST-100**: Netstring parsing: valid netstrings, max length, leading zeros, missing delimiters
- **TEST-200**: JSON command parsing: valid commands, missing id, unknown fields, wrong types
- **TEST-300**: Socket connection: successful connect, second client rejection, clean disconnect
- **TEST-400**: Command sequence: CHANGE AUDIO SOURCE then INIT succeeds; INIT without audio source fails
- **TEST-500**: Audio capture: stream connects, samples flow to projectM, graceful shutdown
- **TEST-600**: Command handling: LOAD PRESET (success/failure), SHOW WINDOW, SET FULLSCREEN, QUIT
- **TEST-700**: Shutdown paths: signal, window close, QUIT command, client disconnect, audio failure
- **TEST-800**: cppcheck passes with `--enable=all` and no warnings

## 7. Risks & Assumptions

### Risks

- **RISK-100**: PulseAudio async API complexity may require iteration; mitigate with careful study of examples
- **RISK-200**: Thread coordination bugs; mitigate with careful mutex/CV usage and testing all paths
- **RISK-300**: Socket cleanup on abnormal exit; mitigate with atexit handler and stale socket detection in client

### Assumptions

- **ASSUMPTION-100**: PulseAudio is available on the target system
- **ASSUMPTION-200**: Default audio source (`@DEFAULT_SINK@.monitor`) exists and is accessible
- **ASSUMPTION-300**: XDG_RUNTIME_DIR or /tmp is writable for socket creation
- **ASSUMPTION-400**: Single-threaded command processing is sufficient for MVP performance

## 8. Related Specifications / Further Reading

- [platyplaty-architecture-discussion.md](../reference/platyplaty-architecture-discussion.md) - Complete architecture decisions
- [stage-2-findings-and-concerns.md](../reference/stage-2-findings-and-concerns.md) - Implementation notes
- [cppbestpractices-as-text.txt](../reference/cppbestpractices-as-text.txt) - C++ coding standards
- [generic-cpp-project-outline.org](../reference/generic-cpp-project-outline.org) - Project structure guidelines
- [ed-non-interactive-guide.md](../.github/ed-non-interactive-guide.md) - Required editing procedures
- [PulseAudio Async API Documentation](https://freedesktop.org/software/pulseaudio/doxygen/async.html)
- [nlohmann/json Documentation](https://json.nlohmann.me/)
