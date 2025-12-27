#!/usr/bin/env python3
"""Socket path computation and stale socket handling for Platyplaty."""

import errno
import os
import socket
from pathlib import Path


def compute_socket_path() -> str:
    """Compute the socket path using environment variable fallback.

    Tries paths in order:
    1. $XDG_RUNTIME_DIR/platyplaty.sock
    2. $TEMPDIR/platyplaty-<uid>.sock
    3. $TMPDIR/platyplaty-<uid>.sock
    4. /tmp/platyplaty-<uid>.sock

    Returns:
        Absolute path to the socket file.

    Raises:
        RuntimeError: If no valid socket directory is found.
    """
    uid = os.getuid()
    candidates = _build_candidate_paths(uid)

    for sock_path, dir_path in candidates:
        if dir_path.is_dir():
            return str(sock_path)

    checked = [str(p) for _, p in candidates]
    msg = f"No valid socket directory found. Checked: {', '.join(checked)}"
    raise RuntimeError(msg)


def _build_candidate_paths(uid: int) -> list[tuple[Path, Path]]:
    """Build list of candidate socket paths and their directories.

    Args:
        uid: User ID for socket filename.

    Returns:
        List of (socket_path, directory_path) tuples.
    """
    candidates: list[tuple[Path, Path]] = []

    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        xdg_path = Path(xdg)
        candidates.append((xdg_path / "platyplaty.sock", xdg_path))

    for var in ("TEMPDIR", "TMPDIR"):
        val = os.environ.get(var)
        if val:
            dir_path = Path(val)
            candidates.append((dir_path / f"platyplaty-{uid}.sock", dir_path))

    tmp_path = Path("/tmp")
    candidates.append((tmp_path / f"platyplaty-{uid}.sock", tmp_path))

    return candidates


class AlreadyRunningError(Exception):
    """Raised when another instance of platyplaty is already running."""


class StaleSocketError(Exception):
    """Raised for unexpected socket errors during stale socket check."""


def check_stale_socket(path: str) -> None:
    """Check for stale socket and handle accordingly.

    Args:
        path: Path to the socket file.

    Raises:
        AlreadyRunningError: If another instance is running.
        StaleSocketError: For unexpected socket errors.
    """
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(path)
        sock.close()
        raise AlreadyRunningError("Another instance of platyplaty is already running")
    except OSError as e:
        if e.errno == errno.ENOENT:
            return  # Socket doesn't exist, proceed normally
        if e.errno == errno.ECONNREFUSED:
            os.unlink(path)  # Stale socket, remove and proceed
            return
        msg = (
            f"Unexpected error checking socket: {e}. "
            "Cannot determine if another instance is running."
        )
        raise StaleSocketError(msg) from e
