#!/usr/bin/env python3
"""Unit tests for cd command handler."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd import execute


class TestExecute:
    """Tests for the execute function."""

    @pytest.mark.asyncio
    async def test_none_args_calls_expand_with_empty_string(self) -> None:
        """With args=None, expand_cd_path is called with empty string."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        base_dir = Path("/base")
        with patch("platyplaty.commands.cd.expand_cd_path") as mock_expand:
            mock_expand.return_value = (Path.home(), None)
            with patch("platyplaty.commands.cd.validate_cd_path") as mock_validate:
                mock_validate.return_value = None
                with patch("platyplaty.commands.cd.navigate_to_directory"):
                    await execute(None, mock_ctx, mock_app, base_dir)
        mock_expand.assert_called_once_with("", base_dir)

    @pytest.mark.asyncio
    async def test_expand_error_is_returned(self) -> None:
        """When expand_cd_path returns error, that error is returned."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        base_dir = Path("/base")
        error_msg = "Error: cd: undefined variable: '$FOO'"
        with patch("platyplaty.commands.cd.expand_cd_path") as mock_expand:
            mock_expand.return_value = (None, error_msg)
            result = await execute("$FOO", mock_ctx, mock_app, base_dir)
        assert result == (False, error_msg)

    @pytest.mark.asyncio
    async def test_validate_error_is_returned(self) -> None:
        """When validate_cd_path returns error, that error is returned."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        base_dir = Path("/base")
        error_msg = "Error: cd: no such directory: '/nonexistent'"
        with patch("platyplaty.commands.cd.expand_cd_path") as mock_expand:
            mock_expand.return_value = (Path("/nonexistent"), None)
            with patch("platyplaty.commands.cd.validate_cd_path") as mock_validate:
                mock_validate.return_value = error_msg
                result = await execute("/nonexistent", mock_ctx, mock_app, base_dir)
        assert result == (False, error_msg)

    @pytest.mark.asyncio
    async def test_navigate_called_on_success(self) -> None:
        """When validation passes, navigate_to_directory is called."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        base_dir = Path("/base")
        target_path = Path("/target")
        with patch("platyplaty.commands.cd.expand_cd_path") as mock_expand:
            mock_expand.return_value = (target_path, None)
            with patch("platyplaty.commands.cd.validate_cd_path") as mock_validate:
                mock_validate.return_value = None
                with patch("platyplaty.commands.cd.navigate_to_directory") as mock_nav:
                    await execute("/target", mock_ctx, mock_app, base_dir)
        mock_nav.assert_called_once()
        call_args = mock_nav.call_args[0]
        assert call_args[1] == target_path

    @pytest.mark.asyncio
    async def test_returns_success_on_navigation(self) -> None:
        """Returns (True, None) on successful navigation."""
        mock_ctx = MagicMock()
        mock_app = MagicMock()
        base_dir = Path("/base")
        with patch("platyplaty.commands.cd.expand_cd_path") as mock_expand:
            mock_expand.return_value = (Path("/target"), None)
            with patch("platyplaty.commands.cd.validate_cd_path") as mock_validate:
                mock_validate.return_value = None
                with patch("platyplaty.commands.cd.navigate_to_directory"):
                    result = await execute("/target", mock_ctx, mock_app, base_dir)
        assert result == (True, None)
