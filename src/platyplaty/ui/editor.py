#!/usr/bin/env python3
"""Editor detection and invocation for file browser.

This module provides functions to determine the appropriate editor command
and invoke it on files. It implements the editor fallback chain:
$VISUAL -> $EDITOR -> sensible-editor -> vi
"""

import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App

from platyplaty.errors import NoEditorFoundError


def _command_exists(cmd: str) -> bool:
    """Check if the executable in a command string exists.

    Parses the command string to extract the executable (first token)
    and checks if it exists in PATH or as an absolute path.

    Args:
        cmd: A command string that may include arguments (e.g., "emacsclient -t").

    Returns:
        True if the executable exists, False otherwise.
    """
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return False
    if not tokens:
        return False
    executable = tokens[0]
    return shutil.which(executable) is not None

def get_editor_command() -> str | None:
    """Determine the editor command to use.

    Follows the fallback chain: $VISUAL -> $EDITOR -> sensible-editor -> vi.
    Returns the first available editor, or None if none found.

    Returns:
        The editor command string, or None if no editor is available.
    """
    # Try $VISUAL first
    visual = os.environ.get("VISUAL")
    if visual and _command_exists(visual):
        return visual

    # Try $EDITOR second
    editor = os.environ.get("EDITOR")
    if editor and _command_exists(editor):
        return editor

    # Try sensible-editor (Debian/Ubuntu standard)
    if shutil.which("sensible-editor"):
        return "sensible-editor"

    # Try vi as last resort
    if shutil.which("vi"):
        return "vi"

    return None


def require_editor_command() -> str:
    """Get the editor command, raising an exception if none available.

    Returns:
        The editor command string.

    Raises:
        NoEditorFoundError: If no editor is available.
    """
    editor = get_editor_command()
    if editor is None:
        raise NoEditorFoundError()
    return editor


async def open_in_editor(app: "App[None]", path: str | Path) -> None:
    """Open a file in the configured editor.

    Suspends the Textual app, runs the editor as a subprocess,
    then resumes the app after the editor exits.
    The path is passed directly to the editor without resolution,
    preserving symlink paths as logical paths.

    Args:
        app: The Textual App instance to suspend.
        path: The file path to open. For symlinks, pass the symlink
            path, not the resolved target.

    Raises:
        NoEditorFoundError: If no editor is available.
    """
    editor = require_editor_command()
    with app.suspend():
        subprocess.run(shlex.split(editor) + [path])
