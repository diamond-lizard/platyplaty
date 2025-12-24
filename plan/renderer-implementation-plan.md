---
goal: Implement Stage 1 C++ Renderer for Platyplaty
version: 1.0
date_created: 2025-12-24
last_updated: 2025-12-24
owner: Platyplaty Development
status: 'Planned'
tags: [feature, c++, renderer, stage-1]
---

# Introduction

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This plan covers the implementation of the Stage 1 C++ renderer for Platyplaty. Stage 1 is a minimal proof-of-concept that creates an SDL2 window with an OpenGL context, initializes projectM, loads a hardcoded test preset, and runs a render loop. There is no audio capture, no socket/IPC, and the window is visible immediately at startup.

## 1. Requirements & Constraints

- **REQ-100**: Renderer must link against system-installed libprojectM via pkg-config (`projectM-4.pc`)
- **REQ-200**: Renderer must use SDL2 for window management and OpenGL context creation
- **REQ-300**: Renderer must use C++17 standard
- **REQ-400**: Renderer must load a hardcoded test preset (`presets/test/101-per_frame.milk`)
- **REQ-500**: Renderer must handle window resize events and update projectM accordingly
- **REQ-600**: Renderer must exit cleanly on window close, SIGINT, SIGTERM, or SIGHUP

- **CON-100**: Must only depend on installed system libraries, not reference source tree
- **CON-200**: Headers located at `/usr/local/apps/libprojectm/include/projectM-4/`
- **CON-300**: Library located at `/usr/local/apps/libprojectm/lib64/libprojectM-4.so`
- **CON-400**: pkg-config file at `/usr/local/apps/libprojectm/lib64/pkgconfig/projectM-4.pc`
- **CON-500**: Individual source files should be under 100 lines
- **CON-600**: Maximum three levels of indentation

- **GUD-100**: Use const liberally for safety
- **GUD-200**: Prefer RAII for resource management
- **GUD-300**: Mark single-parameter constructors explicit
- **GUD-400**: Use pre-increment (++i) over post-increment (i++)
- **GUD-500**: Avoid raw memory allocation; use smart pointers where applicable
- **GUD-600**: Use std::array or std::vector instead of C-style arrays
- **GUD-700**: Use C++-style casts instead of C-style casts

- **PAT-100**: Flat directory structure for renderer source files
- **PAT-200**: Silent on stdout; diagnostics go to stderr
- **PAT-300**: Signal handlers only set atomic shutdown flag
- **PAT-400**: Use exceptions (std::runtime_error) for fatal initialization failures; main() wraps in try/catch

## 2. Implementation Steps

### Implementation Phase 1: Project Structure and Build System

- GOAL-100: Establish project directory structure and working Makefile

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-0100 | Create `renderer/` directory for C++ source files                                                       | Done      | 2025-12-24 |
| TASK-0200 | Create `build/` directory for compiled output (add to .gitignore)                                       | Done      | 2025-12-24 |
| TASK-0300 | Create `presets/test/` directory and copy test presets from `reference/libprojectM-4.1.6/presets/tests/`| Done      | 2025-12-24 |
| TASK-0400 | Create `Makefile` at project root with targets for building renderer                                    |           |      |
| TASK-0500 | Configure Makefile to use pkg-config for projectM-4 and SDL2 flags                                      |           |      |
| TASK-0600 | Configure Makefile with C++17 standard and warning flags (-Wall -Wextra -Wpedantic)                     |           |      |
| TASK-0700 | Add `clean` target to Makefile                                                                          |           |      |

### Implementation Phase 2: Core Application Entry Point

- GOAL-200: Create minimal main entry point with signal handling

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-0800 | Create `renderer/main.cpp` with main() function                                                         |           |      |
| TASK-0900 | Implement SIGPIPE ignore at startup via signal(SIGPIPE, SIG_IGN)                                        |           |      |
| TASK-1000 | Create `renderer/shutdown.hpp` declaring atomic shutdown flag and signal setup function                 |           |      |
| TASK-1100 | Create `renderer/shutdown.cpp` implementing signal handlers for SIGINT, SIGTERM, SIGHUP                 |           |      |
| TASK-1200 | Signal handlers must only set the atomic shutdown flag, no other operations                             |           |      |

### Implementation Phase 3: SDL2 Window and OpenGL Context

- GOAL-300: Create SDL2 window with OpenGL context suitable for projectM

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-1300 | Create `renderer/window.hpp` declaring Window class with RAII semantics                                 |           |      |
| TASK-1400 | Create `renderer/window.cpp` implementing Window class                                                  |           |      |
| TASK-1500 | Include `<SDL_opengl.h>` for portable OpenGL declarations (pkg-config provides include path)                                       |           |      |
| TASK-1600 | Window constructor initializes SDL2 with SDL_INIT_VIDEO                                                 |           |      |
| TASK-1700 | Request OpenGL 2.1 with SDL_GL_CONTEXT_PROFILE_CORE via SDL GL attributes; check return values and throw on failure                               |           |      |
| TASK-1800 | Create window with flags: SDL_WINDOW_OPENGL, SDL_WINDOW_RESIZABLE, SDL_WINDOW_MAXIMIZED, SDL_WINDOW_ALLOW_HIGHDPI             |           |      |
| TASK-1900 | Initial window size 1280x720 (fallback if maximize ignored), title "Platyplaty"                         |           |      |
| TASK-2000 | Create OpenGL context via SDL_GL_CreateContext                                                          |           |      |
| TASK-2100 | Throw std::runtime_error if SDL_Init, SDL_CreateWindow, or SDL_GL_CreateContext fails         |           |      |
| TASK-2200 | Enable vsync: try adaptive vsync (-1), fall back to regular vsync (1)                                   |           |      |
| TASK-2300 | Call glClearColor(0.0, 0.0, 0.0, 1.0) once during initialization                                        |           |      |
| TASK-2400 | Window destructor cleans up OpenGL context and SDL window                                               |           |      |
| TASK-2500 | Implement get_drawable_size() method using SDL_GL_GetDrawableSize for HiDPI support                     |           |      |
| TASK-2600 | Implement swap_buffers() method wrapping SDL_GL_SwapWindow                                              |           |      |

### Implementation Phase 4: ProjectM Integration

- GOAL-400: Initialize projectM and configure for rendering, including preset loading

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-2700 | Create `renderer/visualizer.hpp` declaring Visualizer class wrapping projectM handle                    |           |      |
| TASK-2800 | Create `renderer/visualizer.cpp` implementing Visualizer class                                          |           |      |
| TASK-2900 | Visualizer constructor calls projectm_create() to create projectM instance                              |           |      |
| TASK-3000 | Check for NULL return from projectm_create() and throw std::runtime_error on failure ("Failed to create projectM instance")                                |           |      |
| TASK-3100 | Call projectm_set_window_size() with drawable dimensions immediately after creation                     |           |      |
| TASK-3200 | Call projectm_set_preset_locked(true) to disable internal auto-advance                                  |           |      |
| TASK-3300 | Visualizer destructor calls projectm_destroy() to clean up                                              |           |      |
| TASK-3400 | Implement set_window_size() method wrapping projectm_set_window_size()                                  |           |      |
| TASK-3500 | Implement render_frame() method calling projectm_opengl_render_frame()                                  |           |      |
| TASK-3600 | Register projectm_preset_switch_failed_event callback at construction to capture parse errors |           |      |
| TASK-3700 | Use fixed 32KB member buffer for error storage (callback uses user data pointer) (truncate if exceeded)                         |           |      |
| TASK-3800 | Implement load_preset() method with filesystem existence check                                 |           |      |
| TASK-3900 | Call projectm_load_preset_file() with smooth_transition=true                                   |           |      |
| TASK-4000 | load_preset() returns success/failure status with error message string                         |           |      |

### Implementation Phase 5: Render Loop and Event Handling

- GOAL-500: Implement main render loop with event processing

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-4100 | Create `renderer/event_loop.hpp` declaring run_event_loop() function                                    |           |      |
| TASK-4200 | Create `renderer/event_loop.cpp` implementing the render loop                                           |           |      |
| TASK-4300 | Loop continues while shutdown flag is false                                                             |           |      |
| TASK-4400 | Poll SDL events each frame via SDL_PollEvent                                                            |           |      |
| TASK-4500 | Handle SDL_QUIT event by setting shutdown flag                                                          |           |      |
| TASK-4600 | Handle SDL_WINDOWEVENT_SIZE_CHANGED by calling visualizer set_window_size() with new drawable size           |           |      |
| TASK-4700 | Clear buffers with glClear(GL_COLOR_BUFFER_BIT \| GL_DEPTH_BUFFER_BIT)                                  |           |      |
| TASK-4800 | Call visualizer render_frame()                                                                          |           |      |
| TASK-4900 | Call window swap_buffers()                                                                              |           |      |

### Implementation Phase 6: Main Function Integration

- GOAL-600: Wire all components together in main()

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-5000 | In main(), call signal setup function before any other initialization                                   |           |      |
| TASK-5100 | Wrap initialization in try/catch block; create Window instance                                         |           |      |
| TASK-5200 | Create Visualizer instance with drawable size from Window; exceptions propagate to catch block      |           |      |
| TASK-5300 | Attempt to load hardcoded preset path `presets/test/101-per_frame.milk`                                 |           |      |
| TASK-5400 | If preset load fails, print warning to stderr but continue with idle preset                             |           |      |
| TASK-5500 | Query and set window size after window creation (handle maximize hint timing)                           |           |      |
| TASK-5600 | Call run_event_loop() passing window and visualizer references                                          |           |      |
| TASK-5700 | Return exit code 0 on clean shutdown                                                                    |           |      |
| TASK-5800 | Catch block prints exception message to stderr and returns exit code 1                       |           |      |

### Implementation Phase 7: Testing and Validation

- GOAL-700: Verify Stage 1 renderer functions correctly

| Task       | Description                                                                                             | Completed | Date |
| ---------- | ------------------------------------------------------------------------------------------------------- | --------- | ---- |
| TASK-5900 | Build renderer with `make` and verify no compilation errors or warnings                                 |           |      |
| TASK-6000 | Run renderer from project root and verify window appears maximized                                      |           |      |
| TASK-6100 | Verify preset loads and animation displays (not just idle "M" logo)                                     |           |      |
| TASK-6200 | Resize window and verify visualization adjusts to new size                                              |           |      |
| TASK-6300 | Close window via window manager and verify clean exit (exit code 0)                                     |           |      |
| TASK-6400 | Test Ctrl+C (SIGINT) and verify clean exit (exit code 0)                                                |           |      |
| TASK-6500 | Test with missing preset file and verify warning printed, idle preset shown                             |           |      |

## 3. Alternatives

- **ALT-100**: Could use CMake instead of plain Make. Rejected because the architecture document specifies plain Make for simplicity and independence from libprojectM source tree.
- **ALT-200**: Could start with hidden window (full architecture). Rejected because Stage 1 explicitly uses visible window for easier debugging.
- **ALT-300**: Could use a single monolithic source file. Rejected because files should be under 100 lines per the style guide.

## 4. Dependencies

- **DEP-100**: libprojectM 4.x installed via projectM-devel package
- **DEP-200**: SDL2 installed via SDL2-devel package
- **DEP-300**: OpenGL development headers (typically bundled with graphics drivers or mesa-devel)
- **DEP-400**: pkg-config for build configuration
- **DEP-500**: C++17 capable compiler (GCC 7+ or Clang 5+)

## 5. Files

- **FILE-0100**: `Makefile` - Build configuration at project root
- **FILE-0200**: `renderer/main.cpp` - Application entry point
- **FILE-0300**: `renderer/shutdown.hpp` - Shutdown flag and signal setup declarations
- **FILE-0400**: `renderer/shutdown.cpp` - Signal handler implementations
- **FILE-0500**: `renderer/window.hpp` - Window class declaration
- **FILE-0600**: `renderer/window.cpp` - Window class implementation
- **FILE-0700**: `renderer/visualizer.hpp` - Visualizer class declaration
- **FILE-0800**: `renderer/visualizer.cpp` - Visualizer class implementation
- **FILE-0900**: `renderer/event_loop.hpp` - Event loop declaration
- **FILE-1000**: `renderer/event_loop.cpp` - Event loop implementation

## 6. Testing

- **TEST-100**: Manual verification that window appears and displays visualization
- **TEST-200**: Manual verification of window resize handling
- **TEST-300**: Manual verification of clean shutdown via window close
- **TEST-400**: Manual verification of clean shutdown via SIGINT (Ctrl+C)
- **TEST-500**: Manual verification of preset load failure handling (missing file continues with idle preset)
- **TEST-600**: Build with warnings enabled and verify no warnings produced

## 7. Risks & Assumptions

- **RISK-100**: pkg-config path may need PKG_CONFIG_PATH set for non-standard install location
- **RISK-200**: Window manager may ignore maximize hint (tiling WMs); mitigated by resize event handling
- **RISK-300**: OpenGL context creation may fail on systems without proper graphics drivers

- **ASSUMPTION-100**: libprojectM 4.x is installed and accessible via pkg-config
- **ASSUMPTION-200**: SDL2 is installed and accessible via pkg-config
- **ASSUMPTION-300**: Test presets exist in the reference directory for copying
- **ASSUMPTION-400**: The renderer will be run from the project root directory

## 8. Related Specifications / Further Reading

- [platyplaty-architecture-discussion.md](../reference/platyplaty-architecture-discussion.md)
- [generic-cpp-project-outline.org](../reference/generic-cpp-project-outline.org)
- [cppbestpractices-as-text.txt](../reference/cppbestpractices-as-text.txt)
- projectM Integration Quickstart Guide (external documentation)
- SDL2 Documentation (external)
