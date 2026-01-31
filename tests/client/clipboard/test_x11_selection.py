#!/usr/bin/env python3
"""Unit tests for X11 primary selection access."""

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestGetPrimarySelection:
    """Tests for get_primary_selection function."""

    def test_successful_selection_read(self):
        """Test reading selection when Tkinter returns text."""
        mock_tk = MagicMock()
        mock_root = MagicMock()
        mock_tk.Tk.return_value = mock_root
        mock_root.selection_get.return_value = "selected text"

        with patch.dict(sys.modules, {"tkinter": mock_tk}):
            from platyplaty.clipboard.x11_selection import get_primary_selection
            # Reload to pick up mocked module
            import importlib
            import platyplaty.clipboard.x11_selection as mod
            importlib.reload(mod)
            result = mod.get_primary_selection()

        assert result == "selected text"
        mock_root.withdraw.assert_called_once()
        mock_root.selection_get.assert_called_once_with(selection="PRIMARY")
        mock_root.destroy.assert_called_once()

    def test_tclerror_returns_empty_string(self):
        """Test that TclError when selection is empty returns empty string."""
        mock_tk = MagicMock()
        mock_tk.TclError = Exception
        mock_root = MagicMock()
        mock_tk.Tk.return_value = mock_root
        mock_root.selection_get.side_effect = mock_tk.TclError("no selection")

        with patch.dict(sys.modules, {"tkinter": mock_tk}):
            import importlib
            import platyplaty.clipboard.x11_selection as mod
            importlib.reload(mod)
            result = mod.get_primary_selection()

        assert result == ""
        mock_root.destroy.assert_called_once()

    def test_importerror_returns_empty_string(self):
        """Test that ImportError when Tkinter unavailable returns empty string."""
        with patch.dict(sys.modules, {"tkinter": None}):
            import importlib
            import platyplaty.clipboard.x11_selection as mod
            importlib.reload(mod)
            result = mod.get_primary_selection()

        assert result == ""

    def test_oserror_returns_empty_string(self):
        """Test that OSError when display unavailable returns empty string."""
        mock_tk = MagicMock()
        mock_root = MagicMock()
        mock_tk.Tk.return_value = mock_root
        mock_root.selection_get.side_effect = OSError("no display")

        with patch.dict(sys.modules, {"tkinter": mock_tk}):
            import importlib
            import platyplaty.clipboard.x11_selection as mod
            importlib.reload(mod)
            result = mod.get_primary_selection()

        assert result == ""
        mock_root.destroy.assert_called_once()

    def test_window_destroyed_on_exception(self):
        """Test that Tk window is destroyed even when exception occurs."""
        mock_tk = MagicMock()
        mock_tk.TclError = Exception
        mock_root = MagicMock()
        mock_tk.Tk.return_value = mock_root
        mock_root.selection_get.side_effect = mock_tk.TclError("error")

        with patch.dict(sys.modules, {"tkinter": mock_tk}):
            import importlib
            import platyplaty.clipboard.x11_selection as mod
            importlib.reload(mod)
            mod.get_primary_selection()

        mock_root.destroy.assert_called_once()
