#!/usr/bin/env python3
"""Valid key names for keybindings configuration.

Key names follow the Textual naming convention.
"""

import re
import sys

# Single character keys (letters and digits)
_LETTER_KEYS = set("abcdefghijklmnopqrstuvwxyz")
_DIGIT_KEYS = set("0123456789")

# Special keys
_SPECIAL_KEYS = frozenset({
    "escape", "enter", "tab", "space", "backspace", "delete",
    "up", "down", "left", "right",
    "home", "end", "pageup", "pagedown", "insert",
    "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f20",
    "f21", "f22", "f23", "f24",
})

# Valid modifier prefixes (full names only)
_MODIFIER_PREFIXES = frozenset({"ctrl+", "shift+", "alt+"})

# Abbreviated modifier prefixes (rejected with fatal error)
_ABBREVIATED_PREFIXES = frozenset({"c-", "s-", "a-"})

# Pattern for abbreviated modifiers at start
_ABBREVIATED_PATTERN = re.compile(r"^(c-|s-|a-)")


def is_valid_key_name(key: str) -> bool:
    """Check if a key name is valid.

    Args:
        key: The key name to validate.

    Returns:
        True if the key name is valid, False otherwise.
    """
    # Strip modifiers and validate base key
    base_key = key
    for prefix in _MODIFIER_PREFIXES:
        while base_key.startswith(prefix):
            base_key = base_key[len(prefix):]

    # Base key must be a letter, digit, or special key
    if base_key in _LETTER_KEYS:
        return True
    if base_key in _DIGIT_KEYS:
        return True
    return base_key in _SPECIAL_KEYS


def has_abbreviated_modifier(key: str) -> bool:
    """Check if a key name uses abbreviated modifier prefixes.

    Args:
        key: The key name to check.

    Returns:
        True if the key uses c-, s-, or a- prefixes.
    """
    return bool(_ABBREVIATED_PATTERN.match(key))


def warn_invalid_key(key: str, context: str) -> None:
    """Print a warning for an unrecognized key name.

    Args:
        key: The invalid key name.
        context: Description of where the key was found.
    """
    print(f"Warning: unrecognized key name '{key}' in {context}", file=sys.stderr)
