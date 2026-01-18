#!/usr/bin/env python3
"""Generate example configuration file for Platyplaty."""

import sys
from pathlib import Path

from platyplaty.example_config import EXAMPLE_CONFIG


def generate_config(path: str) -> None:
    """Generate an example config file.

    Args:
        path: Output path, or '-' for stdout.
    """
    if path != "-":
        output_path = Path(path)
        if output_path.exists():
            msg = f"File already exists: {path}"
            raise FileExistsError(msg)
        output_path.write_text(EXAMPLE_CONFIG)
    else:
        sys.stdout.write(EXAMPLE_CONFIG)
