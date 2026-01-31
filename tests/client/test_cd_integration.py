#!/usr/bin/env python3
"""Integration tests for cd command through dispatcher."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from platyplaty.commands.dispatcher import execute_command

MODULE = "platyplaty.commands.dispatcher"
CD_MODULE = "platyplaty.commands.cd"


def make_context(focus: str) -> MagicMock:
    """Create a mock AppContext with specified focus."""
    ctx = MagicMock()
    ctx.current_focus = focus
    return ctx


class TestCdSectionAwareness:
    """Tests for cd command section-awareness through dispatcher."""

    @pytest.mark.asyncio
    @patch(f"{CD_MODULE}.navigate_to_directory")
    @patch(f"{CD_MODULE}.validate_cd_path", return_value=None)
    @patch(f"{CD_MODULE}.expand_cd_path")
    async def test_cd_from_file_browser_succeeds(self, m_exp, m_val, m_nav):
        """cd from file_browser focus navigates successfully."""
        m_exp.return_value = (Path.home(), None)
        ctx = make_context("file_browser")
        result = await execute_command("cd", None, ctx, MagicMock(), Path("/base"))
        assert result == (True, None)

    @pytest.mark.asyncio
    async def test_cd_from_playlist_returns_error(self):
        """cd from playlist focus returns section error."""
        ctx = make_context("playlist")
        result = await execute_command("cd", None, ctx, MagicMock(), Path("/base"))
        expected = "Error: The 'cd' command only works in the file browser"
        assert result == (False, expected)

    @pytest.mark.asyncio
    async def test_cd_from_error_view_returns_error(self):
        """cd from error_view focus returns section error."""
        ctx = make_context("error_view")
        result = await execute_command("cd", None, ctx, MagicMock(), Path("/base"))
        expected = "Error: The 'cd' command only works in the file browser"
        assert result == (False, expected)


class TestCdErrorConditions:
    """Tests for cd command error conditions through dispatcher."""

    @pytest.mark.asyncio
    async def test_cd_to_nonexistent_directory(self, tmp_path):
        """cd to non-existent directory shows correct error."""
        ctx = make_context("file_browser")
        nonexistent = tmp_path / "does_not_exist"
        result = await execute_command("cd", str(nonexistent), ctx, MagicMock(), tmp_path)
        assert result[0] is False
        assert "no such directory" in result[1]
        assert str(nonexistent) in result[1]

    @pytest.mark.asyncio
    async def test_cd_to_file(self, tmp_path):
        """cd to a file shows correct error."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        ctx = make_context("file_browser")
        result = await execute_command("cd", str(test_file), ctx, MagicMock(), tmp_path)
        assert result[0] is False
        assert "not a directory" in result[1]
        assert str(test_file) in result[1]

    @pytest.mark.asyncio
    async def test_cd_with_undefined_env_var(self, tmp_path, monkeypatch):
        """cd with undefined environment variable shows correct error."""
        monkeypatch.delenv("UNDEFINED_VAR_XYZ123", raising=False)
        ctx = make_context("file_browser")
        result = await execute_command("cd", "$UNDEFINED_VAR_XYZ123", ctx, MagicMock(), tmp_path)
        assert result[0] is False
        assert "undefined variable" in result[1]
        assert "UNDEFINED_VAR_XYZ123" in result[1]

    @pytest.mark.asyncio
    async def test_cd_with_empty_env_var(self, tmp_path, monkeypatch):
        """cd with empty environment variable shows correct error."""
        monkeypatch.setenv("EMPTY_VAR_XYZ123", "")
        ctx = make_context("file_browser")
        result = await execute_command("cd", "$EMPTY_VAR_XYZ123", ctx, MagicMock(), tmp_path)
        assert result[0] is False
        assert "empty variable" in result[1]
        assert "EMPTY_VAR_XYZ123" in result[1]
