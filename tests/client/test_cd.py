#!/usr/bin/env python3
"""Unit tests for cd command handler."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.cd import execute

MODULE = "platyplaty.commands.cd"


class TestExecute:
    """Tests for the execute function."""

    @pytest.mark.asyncio
    @patch(f"{MODULE}.navigate_to_directory")
    @patch(f"{MODULE}.validate_cd_path", return_value=None)
    @patch(f"{MODULE}.expand_cd_path")
    async def test_none_args_calls_expand_with_empty(self, m_exp, m_val, m_nav):
        """With args=None, expand_cd_path is called with empty string."""
        m_exp.return_value = (Path.home(), None)
        base_dir = Path("/base")
        await execute(None, MagicMock(), MagicMock(), base_dir)
        m_exp.assert_called_once_with("", base_dir)

    @pytest.mark.asyncio
    @patch(f"{MODULE}.expand_cd_path")
    async def test_expand_error_is_returned(self, mock_expand):
        """When expand_cd_path returns error, that error is returned."""
        error_msg = "Error: cd: undefined variable: '$FOO'"
        mock_expand.return_value = (None, error_msg)
        result = await execute("$FOO", MagicMock(), MagicMock(), Path("/base"))
        assert result == (False, error_msg)

    @pytest.mark.asyncio
    @patch(f"{MODULE}.validate_cd_path")
    @patch(f"{MODULE}.expand_cd_path")
    async def test_validate_error_is_returned(self, mock_expand, mock_validate):
        """When validate_cd_path returns error, that error is returned."""
        error_msg = "Error: cd: no such directory: '/nonexistent'"
        mock_expand.return_value = (Path("/nonexistent"), None)
        mock_validate.return_value = error_msg
        result = await execute("/nonexistent", MagicMock(), MagicMock(), Path("/b"))
        assert result == (False, error_msg)

    @pytest.mark.asyncio
    @patch(f"{MODULE}.navigate_to_directory")
    @patch(f"{MODULE}.validate_cd_path", return_value=None)
    @patch(f"{MODULE}.expand_cd_path")
    async def test_navigate_called_on_success(self, m_exp, m_val, mock_nav):
        """When validation passes, navigate_to_directory is called."""
        target_path = Path("/target")
        m_exp.return_value = (target_path, None)
        await execute("/target", MagicMock(), MagicMock(), Path("/base"))
        mock_nav.assert_called_once()
        assert mock_nav.call_args[0][1] == target_path

    @pytest.mark.asyncio
    @patch(f"{MODULE}.navigate_to_directory")
    @patch(f"{MODULE}.validate_cd_path", return_value=None)
    @patch(f"{MODULE}.expand_cd_path")
    async def test_returns_success_on_navigation(self, m_exp, m_val, m_nav):
        """Returns (True, None) on successful navigation."""
        m_exp.return_value = (Path("/target"), None)
        result = await execute("/target", MagicMock(), MagicMock(), Path("/base"))
        assert result == (True, None)
