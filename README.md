# Platyplaty

A music visualizer that pairs a C++ renderer ([libprojectM](https://github.com/projectM-visualizer/projectm) + SDL2 + PulseAudio)
with a Python terminal UI for browsing presets and managing playlists.

## How It Works

The C++ renderer captures audio from PulseAudio and drives libprojectM to
produce real-time visualizations in an SDL2/OpenGL window.  A Python TUI
(built with Textual) connects to the renderer over a Unix socket and lets you
browse `.milk` preset files, build playlists, and control playback from the
terminal.

## Dependencies

- Python 3.12+
- libprojectM 4.x (`projectM-devel` on Fedora/RHEL)
- SDL2 (`SDL2-devel` on Fedora/RHEL)
- PulseAudio (`libpulse-devel` on Fedora/RHEL)
- C++17 capable compiler (GCC 7+ or Clang 5+)
- pkg-config
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Building

Build the C++ renderer:

```bash
make renderer
```

Install the Python dependencies:

```bash
uv sync
```

### Non-standard libprojectM location

If libprojectM is installed in a non-standard location, set `PKG_CONFIG_PATH`
before building:

```bash
export PKG_CONFIG_PATH=/path/to/libprojectm/lib64/pkgconfig:$PKG_CONFIG_PATH
make renderer
```

## Configuration

Generate an example configuration file:

```bash
bin/platyplaty --generate-config ~/.config/platyplaty.toml
```

Use `-` to print the example config to stdout instead of writing a file.

The config file (`conf/platyplaty-conf.toml` has an annotated example) controls:

- **`[renderer]`** -- audio source, fullscreen, and transition type (soft/hard)
- **`[keybindings.global]`** -- keys that work in every section
- **`[keybindings.file-browser]`** -- keys for navigating presets on disk
- **`[keybindings.playlist]`** -- keys for managing the playlist, plus
  `preset-duration` (seconds per preset during autoplay)
- **`[keybindings.error-view]`** -- keys for the error log

## Running

```bash
bin/platyplaty --config-file ~/.config/platyplaty.toml [path]
```

The optional `path` argument can be a directory to open in the file browser or
a `.platy` playlist file to load at startup.

Symlink `bin/platyplaty` into a directory on
your `PATH` to run it from anywhere.

## Terminal UI

The TUI has three areas:

1. **File browser** (left) -- navigate the filesystem to find `.milk` presets.
2. **Playlist** (right) -- the ordered list of presets to play.
3. **Command prompt** -- activated with `:` for text commands.

### Default Keybindings

| Key                 | Scope        | Action                                           |
|---------------------|--------------|--------------------------------------------------|
| `tab`               | global       | switch focus between file browser and playlist   |
| `j`/`down`          | global       | move selection down                              |
| `k`/`up`            | global       | move selection up                                |
| `enter`             | global       | play the selected preset                         |
| `l`/`right`         | global       | enter directory / open in editor                 |
| `e`                 | global       | view error log                                   |
| `q`                 | global       | quit                                             |
| `h`/`left`          | file browser | go to parent directory                           |
| `a`                 | file browser | add preset to playlist (or load a `.platy` file) |
| `shift+j`           | file browser | skip to next `.milk` file and play               |
| `shift+k`           | file browser | skip to previous `.milk` file and play           |
| `space`             | playlist     | toggle autoplay                                  |
| `shift+j`           | playlist     | play next preset                                 |
| `shift+k`           | playlist     | play previous preset                             |
| `ctrl+j`            | playlist     | move selected item down                          |
| `ctrl+k`            | playlist     | move selected item up                            |
| `shift+d`/`delete`  | playlist     | remove preset from playlist                      |
| `u`                 | playlist     | undo                                             |
| `ctrl+r`            | playlist     | redo                                             |
| `ctrl+s`            | playlist     | save playlist                                    |
| `s`                 | playlist     | shuffle playlist                                 |
| `pageup`/`pagedown` | playlist     | page up / page down                              |
| `home`/`end`        | playlist     | jump to first / last preset                      |
| `c`                 | error view   | clear errors                                     |

All keybindings are reconfigurable in the TOML config file.

### Commands

Type `:` to open the command prompt (supports Emacs-style editing):

| Command        | Description                       |
|----------------|-----------------------------------|
| `:load <path>` | load a `.platy` playlist file     |
| `:save [path]` | save the current playlist         |
| `:clear`       | clear the playlist                |
| `:shuffle`     | randomize playlist order          |
| `:cd [path]`   | change the file browser directory |

## Playlists

Playlists are `.platy` text files containing one absolute path to a `.milk`
preset per line.  They can be created from the TUI or edited by hand.

## Cleaning

```bash
make clean
```

## Make Targets

| Target                   | Description                        |
|--------------------------|------------------------------------|
| `make renderer`          | build the C++ renderer             |
| `make clean`             | remove build artifacts             |
| `make test`              | run ruff, mypy, then pytest        |
| `make test-renderer`     | run cppcheck + renderer tests      |
| `make ruff`              | lint Python source with ruff       |
| `make mypy`              | type-check Python source with mypy |
| `make cppcheck-renderer` | run cppcheck on renderer source    |
