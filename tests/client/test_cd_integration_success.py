#!/usr/bin/env python3
"""Integration tests for successful cd command navigation."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.dispatcher import execute_command

CD_MODULE = "platyplaty.commands.cd"


def make_context(focus: str) -> MagicMock:
    """Create a mock AppContext with specified focus."""
    ctx = MagicMock()
    ctx.current_focus = focus
    return ctx


class TestCdSuccessfulNavigation:
    """Tests for successful cd command navigation through dispatcher."""

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory")
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_without_argument_navigates_home(self, m_exp, m_val, m_nav):
        """cd without argument navigates to home directory."""
        m_exp.return_value = (Path.home(), None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", None, ctx, MagicMock(), Path("/base"))
        assert result == (True, None)
        m_exp.assert_called_once_with("", Path("/base"))

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory")
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_with_absolute_path(self, m_exp, m_val, m_nav):
        """cd with absolute path navigates correctly."""
        target = Path("/some/absolute/path")
        m_exp.return_value = (target, None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", "/some/absolute/path", ctx, MagicMock(), Path("/base"))
        assert result == (True, None)
        m_nav.assert_called_once()
        assert m_nav.call_args[0][1] == target

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory")
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_with_relative_path(self, m_exp, m_val, m_nav):
        """cd with relative path resolves from current directory."""
        base = Path("/current/dir")
        target = Path("/current/dir/subdir")
        m_exp.return_value = (target, None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", "subdir", ctx, MagicMock(), base)
        assert result == (True, None)
        m_exp.assert_called_once_with("subdir", base)

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory")
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_with_tilde(self, m_exp, m_val, m_nav):
        """cd with tilde expands correctly."""
        m_exp.return_value = (Path.home() / "subdir", None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", "~/subdir", ctx, MagicMock(), Path("/base"))
        assert result == (True, None)
        m_exp.assert_called_once_with("~/subdir", Path("/base"))

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory", return_value=False)
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_to_current_directory_is_noop(self, m_exp, m_val, m_nav):
        """cd to current directory is a no-op (returns success, no state change)."""
        current = Path("/current/dir")
        m_exp.return_value = (current, None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", ".", ctx, MagicMock(), current)
        assert result == (True, None)
