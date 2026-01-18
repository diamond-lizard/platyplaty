#!/usr/bin/env python3
"""Key validation functions for keybindings configuration."""

import sys

from platyplaty.types.key_constants import (
    ABBREVIATED_PATTERN,
    DIGIT_KEYS,
    LETTER_KEYS,
    MODIFIER_PREFIXES,
    SPECIAL_KEYS,
)

def is_valid_key_name(key: str) -> bool:
    """Check if a key name is valid.

    Args:
        key: The key name to validate.

    Returns:
        True if the key name is valid, False otherwise.
    """
    # Strip modifiers and validate base key
    base_key = key
    for prefix in MODIFIER_PREFIXES:
        while base_key.startswith(prefix):
            base_key = base_key[len(prefix):]

    # Base key must be a letter, digit, or special key
    if base_key in LETTER_KEYS:
        return True
    if base_key in DIGIT_KEYS:
        return True
    return base_key in SPECIAL_KEYS


def has_abbreviated_modifier(key: str) -> bool:
    """Check if a key name uses abbreviated modifier prefixes.

    Args:
        key: The key name to check.

    Returns:
        True if the key uses c-, s-, or a- prefixes.
    """
    return bool(ABBREVIATED_PATTERN.match(key))


def warn_invalid_key(key: str, context: str) -> None:
    """Print a warning for an unrecognized key name.

    Args:
        key: The invalid key name.
        context: Description of where the key was found.
    """
    print(f"Warning: unrecognized key name '{key}' in {context}", file=sys.stderr)

def validate_single_key(key: str, field_path: str) -> None:
    """Validate a single key name and raise/warn as appropriate.

    Args:
        key: The key name to validate.
        field_path: Full path for error messages.

    Raises:
        ValueError: If the key has an abbreviated modifier.
    """
    if has_abbreviated_modifier(key):
        msg = f"Abbreviated modifier in {field_path}: '{key}'. "
        msg += "Use full names: ctrl+, shift+, alt+"
        raise ValueError(msg)
    if not is_valid_key_name(key):
        warn_invalid_key(key, field_path)


def validate_key_list(keys: list[str], field_path: str) -> None:
    """Validate a list of key names.

    Args:
        keys: List of key names to validate.
        field_path: Full path for error messages.

    Raises:
        ValueError: If any key has an abbreviated modifier.
    """
    for key in keys:
        validate_single_key(key, field_path)
