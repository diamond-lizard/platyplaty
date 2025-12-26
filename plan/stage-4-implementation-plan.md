---
goal: Implement Stage 4 - Python Client Application with CLI, Config, and Playlist Management
version: 1.0
date_created: 2025-12-25
last_updated: 2025-12-25
owner: Platyplaty Development Team
status: 'Planned'
tags: [feature, python, cli, config, playlist]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan implements Stage 4 of Platyplaty: the Python client application. The client is the main user entry point, starting the C++ renderer as a subprocess, managing the playlist, handling configuration via TOML files, and providing the command-line interface. The client controls all preset timing and playlist navigation while the renderer handles visualization.

**Important:** This implementation must adhere to `reference/generic-python-project-outline.org` for Python project structure and style, though the architecture document (`reference/platyplaty-architecture-discussion.md`) takes precedence when there is a conflict between them.

## 1. Requirements & Constraints

### Architectural Requirements (from platyplaty-architecture-discussion.md)

- **REQ-0100**: Client is main entry point; starts renderer as subprocess with `start_new_session=True` so renderer does not receive SIGINT on Ctrl+C
- **REQ-0200**: Client computes socket path and passes it to renderer via `--socket-path` CLI argument
- **REQ-0300**: Socket path resolution order: (1) `$XDG_RUNTIME_DIR/platyplaty.sock`, (2) `$TEMPDIR/platyplaty-<uid>.sock`, (3) `$TMPDIR/platyplaty-<uid>.sock`, (4) `/tmp/platyplaty-<uid>.sock`; undefined env vars are skipped (not fatal)
- **REQ-0400**: Client handles stale socket detection: ENOENT = proceed normally, ECONNREFUSED = unlink and proceed, connection succeeds = exit with "already running" error, other errors = fatal
- **REQ-0500**: Client reads configuration from TOML file using Python's `tomllib`
- **REQ-0600**: Config options: `preset-dirs` (required list), `audio-source` (optional, default `@DEFAULT_SINK@.monitor`), `preset-duration` (optional integer >= 1, default 30), `shuffle` (optional bool, default false), `loop` (optional bool, default true), `fullscreen` (optional bool, default false)
- **REQ-0700**: Unknown config keys are fatal errors (catches typos)
- **REQ-0800**: `preset-duration` must be strictly integer type; float values (even 30.0) are rejected
- **REQ-0900**: Client expands `~` and environment variables in config file paths; undefined env vars in paths are fatal errors
- **REQ-1000**: Relative paths in config are resolved from current working directory; client always sends absolute paths to renderer
- **REQ-1100**: Client scans preset directories (flat, non-recursive), case-insensitive `.milk` extension matching
- **REQ-1200**: Playlist ordering: case-insensitive lexicographic sort by full absolute path (default); shuffle mode randomizes order once
- **REQ-1300**: Deduplication by full absolute path only; symlinks to same file from different paths appear as separate entries
- **REQ-1400**: Client errors at startup if no `.milk` files found; error message lists scanned directories
- **REQ-1500**: Client checks for renderer binary before starting; error if not found with message suggesting `make`
- **REQ-1600**: Client waits for `SOCKET READY\n` on renderer stdout (no timeout); monitors subprocess liveness
- **REQ-1700**: If renderer exits before `SOCKET READY`, client reports error with exit code
- **REQ-1800**: Client passes renderer stderr through to user in real-time (not buffered)
- **REQ-1900**: After `SOCKET READY`, client sends `CHANGE AUDIO SOURCE` then `INIT` to complete initialization
- **REQ-2000**: Client uses netstring framing for all socket messages; format `<length>:<json>,`
- **REQ-2100**: Client increments command ID for each command sent; verifies response ID matches
- **REQ-2200**: Client uses `asyncio` event loop; auto-advance timer resets after each successful `LOAD PRESET` to prevent race conditions
- **REQ-2300**: Socket stream monitored to detect renderer crashes (EOF) immediately
- **REQ-2400**: When auto-advance timer expires, client sends `LOAD PRESET` for next preset
- **REQ-2500**: When loop=false and playlist reaches end, auto-advancing stops; visualizer stays on last preset
- **REQ-2600**: Client attempts preset loads before `SHOW WINDOW`; if all fail, warns user and shows window with idle preset
- **REQ-2700**: Preset load failures are non-fatal; client receives error response and decides how to proceed
- **REQ-2800**: On Ctrl+C (SIGINT), client sends `QUIT` to renderer, waits for response, closes socket, exits
- **REQ-2900**: Graceful keyboard interrupt handling: exit code 1, no error message printed
- **REQ-3000**: Client parses renderer stderr for PLATYPLATY events (netstring-framed JSON with `"source": "PLATYPLATY"`); other stderr passed through
- **REQ-3100**: On stderr `DISCONNECT` event: attempt reconnect (renderer waiting); on `QUIT` event: do not reconnect (renderer exited)
- **REQ-3200**: On socket EOF with no stderr event: attempt reconnect (renderer may still be running)
- **REQ-3300**: Renderer binary location: `build/platyplaty-renderer` relative to project root; shell wrapper resolves symlinks to find project root

### CLI Requirements

- **CLI-100**: `--help` - Show help and exit (lazy imports for fast response)
- **CLI-200**: `--config-file <path>` - Load configuration from file and run
- **CLI-300**: `--generate-config <path|->` - Generate example config to file (or stdout if `-`); if path is existing file, error and exit (don't overwrite)
- **CLI-400**: No arguments = error with suggestion to use `--generate-config`
- **CLI-500**: Use click library for CLI argument handling

### Generated Config Requirements

- **GEN-100**: Example uses `presets/test` as directory with comment explaining relative path resolution
- **GEN-200**: Shows all config options with their defaults and descriptions

### Python Style Requirements (from reference/generic-python-project-outline.org)

- **STY-0100**: Use src-layout: `src/platyplaty/` package directory
- **STY-0200**: Shell wrapper in `bin/platyplaty` handles venv activation and symlink resolution
- **STY-0300**: Invoked via `python -m platyplaty` from shell wrapper
- **STY-0400**: Files under 100 lines preferred; up to ~150 acceptable for cohesive modules
- **STY-0500**: Maximum 3 levels of indentation; use early returns and helper functions
- **STY-0600**: Comprehensive docstrings and type annotations (Python 3.12+ syntax)
- **STY-0650**: Avoid `Any` types; use specific types, generics, or union types instead
- **STY-0660**: Avoid `# type: ignore` comments; fix type issues at their source
- **STY-0670**: Use pydantic models for protocol messages (commands and responses) for type-safe JSON handling
- **STY-0700**: Short single-purpose functions with functional style
- **STY-0800**: Lazy imports for fast `--help` response; heavy imports inside functions after argument validation
- **STY-0900**: Thin `__main__.py` that imports and calls main function
- **STY-1000**: click-decorated command in `main.py`; main.py imports only click at module level
- **STY-1100**: When class attribute can hold different types, declare type explicitly at class level

### Constraints

- **CON-100**: Stage 2 renderer functionality must continue to work
- **CON-200**: Interactive controls (next/prev/quit keys) are deferred to post-MVP; MVP runs with auto-advance only
- **CON-300**: Users quit by closing window or pressing Ctrl+C
- **CON-400**: No default config file location; only loaded if `--config-file` specified

### Guidelines

- **GUD-100**: Strictly synchronous request-response protocol; client sends command, waits for response before next command
- **GUD-200**: Keep socket communication simple; no pipelining or out-of-order responses
- **GUD-300**: Test incrementally after each component

### Exit Codes

- **EXIT-100**: Exit 0 on successful operation
- **EXIT-200**: Exit 1 on keyboard interrupt (no error message) or application errors
- **EXIT-300**: Exit 2 on usage errors (click handles this automatically)

## 2. Implementation Steps

### Implementation Phase 1: Project Structure and Dependencies

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0100: Set up Python package structure with proper tooling

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-00300 | Configure mypy in `pyproject.toml` with strict settings | x | 2025-12-25 |
| TASK-00400 | Configure ruff in `pyproject.toml` with appropriate rule sets | x | 2025-12-25 |
| TASK-00500 | Create `src/platyplaty/` directory structure | x | 2025-12-25 |
| TASK-00600 | Create `src/platyplaty/__init__.py` with version string | x | 2025-12-25 |
| TASK-00700 | Create `src/platyplaty/__main__.py` as thin entry point | x | 2025-12-25 |
| TASK-00800 | Run `uv add click pydantic` to add runtime dependencies (updates pyproject.toml and installs) | x | 2025-12-25 |
| TASK-00850 | Run `uv add --dev mypy ruff` to add dev dependencies (updates pyproject.toml and installs) | x | 2025-12-25 |
| TASK-00900 | Run `uv pip install -e .` for editable installation | x | 2025-12-25 |

### Implementation Phase 2: Shell Wrapper

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0200: Create shell wrapper that handles venv activation and symlink resolution

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-01000 | Create `bin/platyplaty` shell script with shebang and purpose comment |  |  |
| TASK-01100 | Implement symlink resolution using `realpath` to find project root |  |  |
| TASK-01200 | Implement venv activation (source `.venv/bin/activate`) |  |  |
| TASK-01300 | Preserve user's working directory context |  |  |
| TASK-01400 | Invoke Python code via `python -m platyplaty "$@"` |  |  |
| TASK-01500 | Make script executable (`chmod +x bin/platyplaty`) |  |  |
| TASK-01600 | Test wrapper with `--help` flag |  |  |

### Implementation Phase 3: CLI Framework with Click

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0300: Implement CLI with click, lazy imports for fast `--help`

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-01700 | Create `src/platyplaty/main.py` with click-decorated main command; import only click at module level |  |  |
| TASK-01800 | Add `--help` option (click provides automatically) |  |  |
| TASK-01900 | Add `--config-file` option (mutually exclusive with `--generate-config`) |  |  |
| TASK-02000 | Add `--generate-config` option (accepts path or `-` for stdout) |  |  |
| TASK-02100 | Implement no-arguments case: error with suggestion to use `--generate-config` |  |  |
| TASK-02200 | Update `__main__.py` to import and call main from `main.py` |  |  |
| TASK-02300 | Test `--help` responds quickly (lazy imports working) |  |  |
| TASK-02400 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 4: Configuration Module

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0400: Implement TOML config parsing with strict validation

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-02500 | Create `src/platyplaty/config.py` module |  |  |
| TASK-02600 | Define config using `pydantic.BaseModel` with all options: `preset_dirs` (list[str]), `audio_source` (str), `preset_duration` (int), `shuffle` (bool), `loop` (bool), `fullscreen` (bool) |  |  |
| TASK-02700 | Implement `load_config(path: str)` using `tomllib`; validate required `preset-dirs` key |  |  |
| TASK-02800 | Pydantic handles type validation automatically: `preset-duration` must be `int` (reject float even if whole number); `shuffle`, `loop`, and `fullscreen` must be bool |  |  |
| TASK-02900 | Configure `pydantic.ConfigDict(extra='forbid')` for unknown key detection: any unrecognized top-level key is fatal error |  |  |
| TASK-03000 | Define pydantic field defaults: `audio-source` = `@DEFAULT_SINK@.monitor`, `preset-duration` = 30, `shuffle` = false, `loop` = true, `fullscreen` = false |  |  |
| TASK-03100 | Use `pydantic.Field(ge=1)` for `preset-duration` validation: must be >= 1 |  |  |
| TASK-03200 | Create `src/platyplaty/paths.py` module for path expansion |  |  |
| TASK-03300 | Implement `expand_path(path: str)` using `os.path.expanduser()` and `os.path.expandvars()`; fatal error if referenced env var is undefined |  |  |
| TASK-03400 | Implement resolution of relative paths to absolute using `pathlib.Path.resolve()` from current working directory |  |  |
| TASK-03500 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 5: Generate Config

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0500: Implement `--generate-config` functionality

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-03600 | Create `src/platyplaty/generate_config.py` module |  |  |
| TASK-03700 | Implement example config content with `presets/test` as directory example |  |  |
| TASK-03800 | Add comment explaining relative paths are resolved from current working directory |  |  |
| TASK-03900 | Show all config options with defaults in comments |  |  |
| TASK-04000 | Implement `generate_config(path: str)`: if path is `-`, write to `sys.stdout`; otherwise write to file using `pathlib.Path.write_text()` |  |  |
| TASK-04100 | Implement overwrite protection using `pathlib.Path.exists()`: if path is existing file, error and exit |  |  |
| TASK-04200 | Integrate with main CLI |  |  |
| TASK-04300 | Test `--generate-config -` outputs to stdout |  |  |
| TASK-04400 | Test `--generate-config path` creates file |  |  |
| TASK-04500 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 6: Socket Path Resolution

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0600: Implement socket path computation and stale socket handling

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-04600 | Create `src/platyplaty/socket_path.py` module |  |  |
| TASK-04700 | Implement `compute_socket_path()` using `os` module that tries paths in order: (1) `$XDG_RUNTIME_DIR/platyplaty.sock`, (2) `$TEMPDIR/platyplaty-<uid>.sock`, (3) `$TMPDIR/platyplaty-<uid>.sock`, (4) `/tmp/platyplaty-<uid>.sock` |  |  |
| TASK-04800 | Skip undefined environment variables using `os.environ.get()` (not fatal) when computing socket path |  |  |
| TASK-04900 | Verify socket directory exists using `pathlib.Path.is_dir()`; error if no valid directory found |  |  |
| TASK-05000 | Implement `check_stale_socket(path: str)` using `socket` and `errno` modules to attempt connection: ENOENT = proceed, ECONNREFUSED = `os.unlink()` and proceed, success = exit with "already running" error, other = fatal |  |  |
| TASK-05100 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 7: Playlist Module

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0700: Implement preset directory scanning and playlist management

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-05200 | Create `src/platyplaty/playlist.py` module |  |  |
| TASK-05300 | Implement `scan_preset_dirs(dirs: list[str])` using `pathlib.Path.iterdir()` to scan directories flat (non-recursive) |  |  |
| TASK-05400 | Implement case-insensitive `.milk` extension matching using `pathlib.Path.suffix` |  |  |
| TASK-05500 | Implement deduplication by full absolute path |  |  |
| TASK-05600 | Error if no `.milk` files found; print to `sys.stderr` message listing scanned directories |  |  |
| TASK-05700 | Implement case-insensitive lexicographic sort by full absolute path |  |  |
| TASK-05800 | Implement shuffle mode using `random.shuffle()`: randomize order once when enabled |  |  |
| TASK-05900 | Create `Playlist` class with `current()`, `next()`, `previous()`, `at_end()` methods |  |  |
| TASK-06000 | Implement loop behavior: when loop=true, wrap around; when loop=false, stop at end |  |  |
| TASK-06100 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 8: Netstring Module

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0800: Implement netstring framing for socket communication

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-06200 | Create `src/platyplaty/netstring.py` module |  |  |
| TASK-06300 | Implement `encode_netstring(payload: str) -> bytes` that produces `<length>:<payload>,` format |  |  |
| TASK-06400 | Implement `decode_netstring(data: bytes) -> tuple[str, bytes]` that returns (payload, remaining_data) |  |  |
| TASK-06500 | Handle partial reads by buffering until complete netstring received |  |  |
| TASK-06550 | Implement 64KB (65536 bytes) maximum payload size validation; reject oversized messages |  |  |
| TASK-06560 | Follow "be liberal in what we accept, strict in what we send": encode_netstring must never produce leading zeros; decode_netstring should accept them |  |  |
| TASK-06600 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 9: Socket Client Module

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-0900: Implement socket client for renderer communication

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-06700 | Create `src/platyplaty/socket_client.py` module |  |  |
| TASK-06800 | Implement `SocketClient` class with Unix domain socket connection (using `socket` module) |  |  |
| TASK-06900 | Implement `send_command(command: dict) -> dict` that sends netstring-framed JSON (using `json` module) and waits for response |  |  |
| TASK-07000 | Track command ID; increment for each command; verify response ID matches |  |  |
| TASK-07100 | Implement `recv_response()` with buffering for partial reads |  |  |
| TASK-07200 | Wrap socket connection with `asyncio` streams for async I/O |  |  |
| TASK-07300 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 10: Renderer Process Management

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1000: Implement renderer subprocess lifecycle management

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-07400 | Create `src/platyplaty/renderer.py` module |  |  |
| TASK-07500 | Implement `find_renderer_binary()` using `pathlib` that locates `build/platyplaty-renderer` relative to project root (resolved via shell wrapper); error if not found with message suggesting `make` |  |  |
| TASK-07600 | Implement `start_renderer(socket_path: str)` using `asyncio.create_subprocess_exec()` with `start_new_session=True` |  |  |
| TASK-07700 | Pass `--socket-path` argument to renderer |  |  |
| TASK-07800 | Read renderer stdout from async stream for `SOCKET READY\n` line; no timeout; monitor subprocess liveness |  |  |
| TASK-07900 | If async subprocess exits before `SOCKET READY`, report error with exit code |  |  |
| TASK-08000 | Implement real-time stderr passthrough via async stream iteration |  |  |
| TASK-08100 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 11: Stderr Event Parsing

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1100: Implement parsing of PLATYPLATY stderr events

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-08200 | Create `src/platyplaty/stderr_parser.py` module |  |  |
| TASK-08300 | Implement detection of netstring-framed JSON on stderr using `re` module (line starts with digits followed by colon) |  |  |
| TASK-08400 | Parse PLATYPLATY events: parse with `json` module; check for `"source": "PLATYPLATY"` |  |  |
| TASK-08500 | Handle event types: `DISCONNECT`, `AUDIO_ERROR`, `QUIT` |  |  |
| TASK-08510 | On `AUDIO_ERROR` event: log warning to stderr ("Audio error: <reason>, visualization continues silently") and continue; no reconnect needed |  |  |
| TASK-08600 | Pass through non-PLATYPLATY stderr output to user |  |  |
| TASK-08700 | Handle malformed netstrings on stderr gracefully (pass through as regular output) |  |  |
| TASK-08800 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 12: Main Event Loop

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1200: Implement main event loop with auto-advance timer

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-08900 | Create `src/platyplaty/event_loop.py` module |  |  |
| TASK-09000 | Implement async event loop using separate `asyncio` tasks for socket and stderr, coordinated via `asyncio.gather()`; stderr task signals events to main loop via shared flags or `asyncio.Event` |  |  |
| TASK-09100 | Timer resets after each successful `LOAD PRESET`; use `asyncio` timeout of `preset_duration` seconds; no command sent while another is in flight |  |  |
| TASK-09200 | When timer expires, send `LOAD PRESET` for next preset from playlist; reset timer after successful response |  |  |
| TASK-09300 | Handle loop=false case: when playlist at end, stop auto-advancing; visualizer stays on last preset |  |  |
| TASK-09400 | Detect socket EOF immediately (renderer crash detection) |  |  |
| TASK-09500 | Process stderr events; on `QUIT` event set flag to not reconnect |  |  |
| TASK-09600 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 13: Signal Handling and Graceful Shutdown

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1300: Implement Ctrl+C handling and graceful shutdown

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-09700 | Implement SIGINT handler using asyncio's `loop.add_signal_handler()` that sets shutdown flag; event loop sends `QUIT` command when safe |  |  |
| TASK-09800 | Wait for `QUIT` response before closing socket |  |  |
| TASK-09900 | Exit with code 1, no error message on keyboard interrupt |  |  |
| TASK-10000 | Ensure socket is closed via `socket.close()` on all exit paths |  |  |
| TASK-10050 | On shutdown, cancel all asyncio tasks (stderr task, socket task) before closing resources; use asyncio's task cancellation mechanism |  |  |
| TASK-10100 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 14: Client Reconnection Logic

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1400: Implement reconnection behavior per Robustness Philosophy

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-10200 | On stderr `DISCONNECT` event: attempt reconnect using `socket` module (renderer is waiting) |  |  |
| TASK-10300 | On stderr `QUIT` event: do not reconnect (renderer has exited) |  |  |
| TASK-10400 | On socket EOF with no stderr event: attempt reconnect using `socket` module |  |  |
| TASK-10500 | After reconnect, re-run full startup sequence (CHANGE AUDIO SOURCE, INIT, LOAD PRESET, SHOW WINDOW) using current playlist position (same preset as before disconnect); renderer handles via idempotency; timer resets to full `preset-duration` after reconnect completes (preset gets fresh full duration, not remaining time from before disconnect) |  |  |
| TASK-10600 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 15: Startup Sequence Integration

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1500: Integrate all components into complete startup sequence

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-10700 | In main.py: load and validate config |  |  |
| TASK-10800 | Expand paths in config; resolve relative paths to absolute using `pathlib` |  |  |
| TASK-10900 | Validate all preset directories exist using `pathlib.Path.is_dir()` (strict validation per architecture) |  |  |
| TASK-11000 | Scan preset directories; build playlist |  |  |
| TASK-11100 | Compute socket path; check for stale socket |  |  |
| TASK-11200 | Check renderer binary exists using `pathlib.Path.exists()` |  |  |
| TASK-11300 | Start renderer subprocess using `asyncio.create_subprocess_exec()`; wait for `SOCKET READY` |  |  |
| TASK-11400 | Connect to socket using `socket` module |  |  |
| TASK-11500 | Send `CHANGE AUDIO SOURCE` command with audio source from config; error "cannot change audio source after INIT" is ignored during reconnect (expected per MVP reconnection behavior), other errors are fatal |  |  |
| TASK-11600 | Send `INIT` command; handle error response: "already initialized" is success (expected during reconnect per MVP reconnection behavior), other errors are fatal (exit with message; MVP does not retry) |  |  |
| TASK-11700 | Attempt to load first preset via `LOAD PRESET`; if fails, try next; if all fail, warn user via `sys.stderr`; start auto-advance timer after first successful load |  |  |
| TASK-11800 | Send `SHOW WINDOW` command |  |  |
| TASK-11810 | Track window visibility state locally; update after successful `SHOW WINDOW` |  |  |
| TASK-11850 | If `fullscreen` config is true and `SHOW WINDOW` succeeded, send `SET FULLSCREEN` command with `enabled: true`; per architecture, `SET FULLSCREEN` before `SHOW WINDOW` returns error "window not yet visible" |  |  |
| TASK-11900 | Enter main event loop |  |  |
| TASK-12000 | Run `uv run ruff check src/` and `uv run mypy src/` to verify code quality |  |  |

### Implementation Phase 16: Makefile Integration

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

- GOAL-1600: Update Makefile for Python tooling

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-12100 | Add `ruff` target to run ruff on `src/` |  |  |
| TASK-12200 | Add `mypy` target to run mypy on `src/` |  |  |
| TASK-12300 | Add `ruff-fix` target to auto-fix ruff issues |  |  |
| TASK-12400 | Update `test` target to run ruff first, then mypy, then pytest |  |  |
| TASK-12500 | Update default target to list available rules |  |  |

### Implementation Phase 17: Integration Testing

**CRITICAL**: Before making ANY edits, read `.github/ed-non-interactive-guide.md` and follow it exactly.

**CODE STYLE**: Follow `reference/generic-python-project-outline.org` and `reference/python-style.org` strictly. The architecture document takes precedence on any conflicts.

- GOAL-1700: Verify complete Stage 4 functionality

| Task | Description | Completed | Date |
| ---- | ----------- | --------- | ---- |
| TASK-12600 | Test `--help` responds quickly |  |  |
| TASK-12700 | Test `--generate-config -` produces valid TOML |  |  |
| TASK-12800 | Test `--generate-config path` creates file and refuses to overwrite |  |  |
| TASK-12900 | Test config validation: missing preset-dirs, unknown keys, wrong types |  |  |
| TASK-13000 | Test path expansion: `~`, `$HOME`, undefined env var error |  |  |
| TASK-13100 | Test preset scanning: finds .milk files, case-insensitive, deduplication |  |  |
| TASK-13200 | Test playlist: alphabetical order, shuffle, loop/no-loop |  |  |
| TASK-13300 | Test stale socket handling: ENOENT, ECONNREFUSED, already running |  |  |
| TASK-13400 | Test startup sequence: renderer starts, SOCKET READY received, commands sent |  |  |
| TASK-13500 | Test auto-advance: presets change at configured duration |  |  |
| TASK-13600 | Test Ctrl+C: QUIT sent, graceful shutdown |  |  |
| TASK-13700 | Test all files under ~150 lines |  |  |
| TASK-13800 | Test no more than 3 levels of indentation |  |  |
| TASK-13900 | Run `uv run ruff check src/` and `uv run mypy src/` |  |  |
| TASK-14000 | Run `uv run pytest tests/` |  |  |

## 3. Alternatives

- **ALT-100**: Using argparse instead of click - rejected because click provides cleaner decorator-based interface and automatic help generation per generic-python-project-outline.org
- **ALT-200**: Using threading for stderr handling - rejected to keep design simple; asyncio handles all I/O
- **ALT-300**: Using asyncio for event loop - selected; provides cleaner code with built-in subprocess and signal handling support
- **ALT-400**: Default config file location (e.g., `~/.config/platyplaty.toml`) - rejected per architecture; config only loaded if `--config-file` specified

## 4. Dependencies

- **DEP-100**: click - CLI argument handling (runtime dependency)
- **DEP-150**: pydantic - Config validation with automatic type checking and error messages (runtime dependency)
- **DEP-200**: mypy - static type checking (dev dependency)
- **DEP-300**: ruff - linting and formatting (dev dependency)
- **DEP-400**: pytest - testing (dev dependency, already present)
- **DEP-500**: tomllib - TOML parsing (Python 3.11+ stdlib)
- **DEP-600**: Stage 2 renderer - must be built and functional
- **DEP-700**: Standard library modules (no installation required):
  - `asyncio` - Async event loop, subprocess management, signal handling
  - `socket` - Unix domain socket communication with renderer (via asyncio streams)
  - `json` - JSON encoding/decoding for protocol messages
  - `os` - Environment variables, process info (uid), file operations
  - `pathlib` - Path manipulation and resolution
  - `signal` - Signal constants (SIGINT, SIGTERM); handlers registered via asyncio's `loop.add_signal_handler()`
  - `random` - Playlist shuffle randomization
  - `time` - Timer calculations for auto-advance using monotonic clock
  - `sys` - stdout/stderr access for config generation output
  - `re` - Regex pattern matching for stderr event detection
  - `errno` - Error code constants for socket error handling

## 5. Files

### New Files

- **FILE-0100**: `src/platyplaty/__init__.py` - Package init with version
- **FILE-0200**: `src/platyplaty/__main__.py` - Entry point for `python -m platyplaty`
- **FILE-0300**: `src/platyplaty/main.py` - CLI command definitions with click
- **FILE-0400**: `src/platyplaty/config.py` - TOML config parsing and validation
- **FILE-0500**: `src/platyplaty/paths.py` - Path expansion and resolution
- **FILE-0600**: `src/platyplaty/generate_config.py` - Example config generation
- **FILE-0700**: `src/platyplaty/socket_path.py` - Socket path computation and stale detection
- **FILE-0800**: `src/platyplaty/playlist.py` - Preset directory scanning and playlist management
- **FILE-0900**: `src/platyplaty/netstring.py` - Netstring encoding/decoding
- **FILE-1000**: `src/platyplaty/socket_client.py` - Socket client for renderer communication
- **FILE-1100**: `src/platyplaty/renderer.py` - Renderer subprocess management
- **FILE-1200**: `src/platyplaty/stderr_parser.py` - PLATYPLATY stderr event parsing
- **FILE-1300**: `src/platyplaty/event_loop.py` - Main event loop with auto-advance timer
- **FILE-1400**: `bin/platyplaty` - Shell wrapper script

### Modified Files

- **FILE-1500**: `pyproject.toml` - Add dependencies and tool configurations
- **FILE-1600**: `Makefile` - Add Python tooling targets

## 6. Testing

- **TEST-0100**: CLI tests: `--help`, `--config-file`, `--generate-config`, no args
- **TEST-0200**: Config validation: required keys, unknown keys, type checking, value ranges
- **TEST-0300**: Path expansion: tilde, environment variables, relative paths, undefined vars
- **TEST-0400**: Playlist: scanning, sorting, shuffle, loop, empty directory error
- **TEST-0500**: Socket path: environment variable fallback, stale socket detection
- **TEST-0600**: Netstring: encoding, decoding, partial reads
- **TEST-0700**: Renderer lifecycle: start, SOCKET READY, crash detection
- **TEST-0800**: Event loop: auto-advance timer, socket EOF detection
- **TEST-0900**: Signal handling: Ctrl+C sends QUIT, graceful exit
- **TEST-1000**: Reconnection: DISCONNECT event, QUIT event, EOF behavior
- **TEST-1100**: Full integration: config -> start -> connect -> preset -> show -> auto-advance -> quit

## 7. Risks & Assumptions

### Risks

- **RISK-100**: ~~Real-time stderr passthrough~~ - mitigated by using `asyncio` subprocess with async streams
- **RISK-200**: Signal handling in Python can be tricky; mitigate by keeping handler minimal
- **RISK-300**: Reconnection logic may have edge cases; mitigate with thorough testing

### Assumptions

- **ASSUMPTION-100**: Python 3.12+ available (per pyproject.toml requires-python)
- **ASSUMPTION-200**: Shell wrapper will be invoked from bash-compatible shell
- **ASSUMPTION-300**: Virtual environment `.venv` exists in project root
- **ASSUMPTION-400**: Stage 2 renderer is functional and tested
- **ASSUMPTION-500**: Users have write access to socket directory

## 8. Related Specifications / Further Reading

- [platyplaty-architecture-discussion.md](../reference/platyplaty-architecture-discussion.md) - Complete architecture decisions (takes precedence)
- [generic-python-project-outline.org](../reference/generic-python-project-outline.org) - Python project structure
- [python-style.org](../reference/python-style.org) - Python coding style
- [stage-2-implementation-plan.md](stage-2-implementation-plan.md) - Stage 2 implementation details
- [ed-non-interactive-guide.md](../.github/ed-non-interactive-guide.md) - Required editing procedures
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework documentation
