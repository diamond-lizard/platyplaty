#!/usr/bin/env python3
"""Example configuration template for Platyplaty."""

EXAMPLE_CONFIG = '''# Platyplaty configuration file

# Optional: Path to .platy playlist file to load at startup
# playlist = "/path/to/playlist.platy"

[renderer]
# PulseAudio source for audio capture
# Default: monitor of the default output sink
audio-source = "@DEFAULT_SINK@.monitor"

# Start in fullscreen mode
fullscreen = false

# Transition type when loading presets
# "soft" provides smooth blending between presets
# "hard" provides instant switching
transition-type = "hard"

# Keybindings available in all sections.
# Keys defined here work regardless of which section (file browser or playlist)
# has focus.
# Note: For shifted letters, both "K" and "shift+k" formats work.
[keybindings.global]
# Switch focus between file browser and playlist
switch-focus = ["tab"]

# Quit application
quit = ["q"]

# Move selection up
navigate-up = ["k", "up"]

# Move selection down
navigate-down = ["j", "down"]

# Enter directory (file browser) or open in editor (both sections)
open-selected = ["l", "right"]

# Open error view
view-errors = ["e"]

# Load preset into renderer (preview in file browser, play in playlist)
play-selection = ["enter"]

# Keybindings for file browser section.
[keybindings.file-browser]
# Go to parent directory
open-parent = ["h", "left"]

# Add selected preset to playlist, or load selected .platy file
add-preset-or-load-playlist = ["a"]

# Skip to previous .milk file and play
play-previous-preset = ["K"]

# Skip to next .milk file and play
play-next-preset = ["J"]

# Keybindings and settings for playlist section.
[keybindings.playlist]
# Seconds to display each preset before advancing (must be >= 1)
preset-duration = 30

# Select previous preset and play
play-previous = ["K"]

# Select next preset and play
play-next = ["J"]

# Move selected item up in list
reorder-up = ["ctrl+k"]

# Move selected item down in list
reorder-down = ["ctrl+j"]

# Remove selected preset from playlist
delete-from-playlist = ["D", "delete"]

# Undo last playlist modification
undo = ["u"]

# Redo last undone action
redo = ["ctrl+r"]

# Save playlist
save-playlist = ["ctrl+s"]

# Shuffle playlist order
shuffle-playlist = ["s"]

# Toggle autoplay on/off
toggle-autoplay = ["space"]

# Move view up one page
page-up = ["pageup"]

# Move view down one page
page-down = ["pagedown"]

# Go to first preset
navigate-to-first-preset = ["home"]

# Go to last preset
navigate-to-last-preset = ["end"]

# Keybindings for error view section.
[keybindings.error-view]
# Clear all errors from log
clear-errors = ["c"]
'''
