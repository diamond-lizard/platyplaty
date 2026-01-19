#!/usr/bin/env python3
"""Standard confirmation prompt messages for Platyplaty.

This module defines the standard prompt messages used throughout
the application for various confirmation dialogs.
"""

# Quit confirmation prompts
PROMPT_QUIT = "Quit? (y/n)"
PROMPT_QUIT_UNSAVED = "There are unsaved changes. Quit anyway? (y/n)"

# Playlist load/replace prompts
PROMPT_LOAD_REPLACE_UNSAVED = (
    "There are unsaved changes in the currently loaded playlist, "
    "replace anyway (y/n)?"
)
PROMPT_LOAD_CLEAR_NONEMPTY = (
    "Load selected playlist, clearing current playlist? (y/n)"
)

# File overwrite prompt
PROMPT_OVERWRITE = "File exists. Overwrite? (y/n)"

# Playlist clear prompt
PROMPT_CLEAR_UNSAVED = (
    "There are unsaved changes in the currently loaded playlist, "
    "clear anyway (y/n)?"
)
