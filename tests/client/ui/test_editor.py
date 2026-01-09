#!/usr/bin/env python3
"""Tests for editor detection and fallback behavior.

This module tests:
- Editor fallback chain: $VISUAL -> $EDITOR -> sensible-editor -> vi
- NoEditorFoundError when no editor is available
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.errors import NoEditorFoundError
from platyplaty.ui.editor import get_editor_command, require_editor_command


class TestEditorFallback:
    """Tests for editor detection fallback chain."""

    def test_visual_env_var_takes_priority(self) -> None:
        """get_editor_command() returns $VISUAL value when set."""
        with patch.dict("os.environ", {"VISUAL": "my-visual-editor", "EDITOR": "my-editor"}):
            result = get_editor_command()
        assert result == "my-visual-editor", "should return $VISUAL value"

    def test_editor_env_var_when_visual_not_set(self) -> None:
        """get_editor_command() returns $EDITOR value when $VISUAL is not set."""
        with patch.dict("os.environ", {"EDITOR": "my-editor"}, clear=True):
            result = get_editor_command()
        assert result == "my-editor", "should return $EDITOR value"

    def test_sensible_editor_when_env_vars_not_set(self) -> None:
        """get_editor_command() returns sensible-editor when env vars not set."""
        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/sensible-editor" if cmd == "sensible-editor" else None
        with patch.dict("os.environ", {}, clear=True):
            with patch("shutil.which", mock_which):
                result = get_editor_command()
        assert result == "sensible-editor", "should return sensible-editor"

    def test_vi_when_sensible_editor_not_found(self) -> None:
        """get_editor_command() returns vi when sensible-editor not found."""
        def mock_which(cmd: str) -> str | None:
            return "/usr/bin/vi" if cmd == "vi" else None
        with patch.dict("os.environ", {}, clear=True):
            with patch("shutil.which", mock_which):
                result = get_editor_command()
        assert result == "vi", "should return vi"

    def test_require_editor_raises_when_no_editor_found(self) -> None:
        """require_editor_command() raises NoEditorFoundError when no editor found."""
        def mock_which(cmd: str) -> str | None:
            return None
        with patch.dict("os.environ", {}, clear=True):
            with patch("shutil.which", mock_which):
                with pytest.raises(NoEditorFoundError):
                    require_editor_command()
