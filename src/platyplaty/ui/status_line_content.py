"""Content building for the status line widget.

Formats autoplay state and playlist filename with truncation rules.
"""

from pathlib import Path

from platyplaty.ui.status_line_truncate import format_filename

AUTOPLAY_ON = "[autoplay: on]"
AUTOPLAY_OFF = "[autoplay: off]"
NO_PLAYLIST = "no playlist file loaded"


def build_status_content(
    autoplay_enabled: bool,
    playlist_filename: Path | None,
    dirty: bool,
    width: int,
) -> str:
    """Build the status line content string with truncation.

    Format: "[autoplay: on/off] [* ]filename" or "[autoplay: on/off] no playlist..."
    The autoplay state is never truncated; only the filename is truncated.

    Args:
        autoplay_enabled: Whether autoplay is on.
        playlist_filename: Associated filename or None.
        dirty: Whether the playlist has unsaved changes.
        width: Available width in characters.

    Returns:
        The formatted status line content.
    """
    autoplay_text = AUTOPLAY_ON if autoplay_enabled else AUTOPLAY_OFF
    file_part = _build_file_part(playlist_filename, dirty, width, autoplay_text)
    return f"{autoplay_text} {file_part}"


def _build_file_part(
    playlist_filename: Path | None,
    dirty: bool,
    total_width: int,
    autoplay_text: str,
) -> str:
    """Build the file portion of the status line.

    Args:
        playlist_filename: Associated filename or None.
        dirty: Whether playlist has unsaved changes.
        total_width: Total available width.
        autoplay_text: The autoplay text already determined.

    Returns:
        The file portion string, possibly truncated.
    """
    if playlist_filename is None:
        return NO_PLAYLIST
    # Calculate available width for file part
    # Format: "autoplay_text file_part" (one space separator)
    available = total_width - len(autoplay_text) - 1
    return format_filename(playlist_filename.name, dirty, available)

