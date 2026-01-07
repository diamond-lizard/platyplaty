#!/usr/bin/env python3
"""Renderer binary discovery for Platyplaty.

This module handles finding the C++ renderer binary relative to the
project root.
"""

from pathlib import Path


class RendererNotFoundError(Exception):
    """Raised when the renderer binary cannot be found."""


# Renderer binary path relative to project root
RENDERER_BINARY_PATH = "build/platyplaty-renderer"


def find_renderer_binary() -> Path:
    """Find the renderer binary relative to the project root.

    The project root is determined by finding the parent directory
    that contains the src/platyplaty package.

    Returns:
        Path to the renderer binary.

    Raises:
        RendererNotFoundError: If the binary is not found.
    """
    # Find project root by walking up from this file's location
    package_dir = Path(__file__).resolve().parent
    project_root = package_dir.parent.parent  # src/platyplaty -> src -> root

    renderer_path = project_root / RENDERER_BINARY_PATH
    if not renderer_path.exists():
        msg = (
            f"Renderer binary not found at {renderer_path}. "
            "Did you run 'make'?"
        )
        raise RendererNotFoundError(msg)

    return renderer_path
