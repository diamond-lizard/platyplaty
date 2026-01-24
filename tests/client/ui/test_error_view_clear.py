#!/usr/bin/env python3
"""Unit tests for error view clear functionality.

Tests the clear errors keyboard handling.
"""

import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from platyplaty.ui.error_view_key import _handle_clear_errors


class TestClearErrors:
    """Tests for clear errors functionality."""

    def test_clear_empties_error_log(self) -> None:
        """Clear errors removes all entries from error log."""
        from platyplaty.ui.error_view import ErrorView

        error_log: list[str] = ["error1", "error2", "error3"]
        view = ErrorView(error_log)
        view._wrapped_lines = ["error1", "error2", "error3"]

        class MockContext:
            def __init__(self) -> None:
                self.error_log = error_log

        context = MockContext()
        with patch.object(type(view), 'app', MagicMock()):
            _handle_clear_errors(view, context)
        assert context.error_log == []

    def test_clear_returns_true(self) -> None:
        """Clear errors returns True to indicate key was handled."""
        from platyplaty.ui.error_view import ErrorView

        error_log: list[str] = ["error"]
        view = ErrorView(error_log)
        view._wrapped_lines = ["error"]

        class MockContext:
            def __init__(self) -> None:
                self.error_log = error_log

        context = MockContext()
        with patch.object(type(view), 'app', MagicMock()):
            result = _handle_clear_errors(view, context)
        assert result is True
