#!/usr/bin/env python3
"""Generate example configuration file for Platyplaty."""
import sys
from pathlib import Path

EXAMPLE_CONFIG = '''# Platyplaty configuration file
# See https://github.com/your-repo/platyplaty for documentation

# Required: List of directories containing .milk preset files
# Relative paths are resolved from the current working directory
preset-dirs = [
    "presets/test",
]

# Optional: PulseAudio source for audio capture
# Default: monitor of the default output sink
# audio-source = "@DEFAULT_SINK@.monitor"

# Optional: Seconds to display each preset before advancing (must be >= 1)
# preset-duration = 30

# Optional: Randomize playlist order (true/false)
# shuffle = false

# Optional: Loop playlist when reaching the end (true/false)
# loop = true

# Optional: Start in fullscreen mode (true/false)
# fullscreen = false
'''

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
