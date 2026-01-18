#!/usr/bin/env python3
"""Constants for valid key names in keybindings configuration.

Key names follow the Textual naming convention.
"""

import re

# Single character keys (letters and digits)
LETTER_KEYS = set("abcdefghijklmnopqrstuvwxyz")
DIGIT_KEYS = set("0123456789")

# Special keys
SPECIAL_KEYS = frozenset({
    "escape", "enter", "tab", "space", "backspace", "delete",
    "up", "down", "left", "right",
    "home", "end", "pageup", "pagedown", "insert",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20",
    "f21", "f22", "f23", "f24",
})

# Valid modifier prefixes (full names only)
MODIFIER_PREFIXES = frozenset({"ctrl+", "shift+", "alt+"})

# Pattern for abbreviated modifiers at start (rejected with fatal error)
ABBREVIATED_PATTERN = re.compile(r"^(c-|s-|a-)")
