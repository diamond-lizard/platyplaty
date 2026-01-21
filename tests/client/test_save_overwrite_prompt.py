#!/usr/bin/env python3
"""Unit tests for :save command with overwrite prompt."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSaveOverwritePrompt:
    """Tests for :save when target file exists."""

    @pytest.mark.asyncio
    async def test_save_shows_overwrite_prompt(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Save shows overwrite prompt when file exists."""
        from platyplaty.commands.save_playlist import save_to_path

        existing_file = tmp_path / "existing.platy"
        existing_file.write_text("/old.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt

        await save_to_path(str(existing_file), mock_ctx, mock_app, tmp_path)

        mock_prompt.show_prompt.assert_called_once()
        call_args = mock_prompt.show_prompt.call_args
        assert "File exists" in call_args[0][0]
        assert "Overwrite" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_overwrite_confirmed_saves_file(
        self, mock_ctx, mock_app, tmp_path
    ):
        """User pressing 'y' on overwrite prompt performs save."""
        from platyplaty.commands.save_playlist import check_and_save

        existing_file = tmp_path / "existing.platy"
        existing_file.write_text("/old.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_prompt.show_prompt.side_effect = capture_callback
        await check_and_save(existing_file, mock_ctx, mock_app)

        with patch(
            "platyplaty.commands.save_playlist.perform_save",
            return_value=(True, None),
        ) as mock_save:
            captured_callback(True)
        mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_overwrite_declined_cancels_save(
        self, mock_ctx, mock_app, tmp_path
    ):
        """User pressing 'n' on overwrite prompt cancels save."""
        from platyplaty.commands.save_playlist import check_and_save

        existing_file = tmp_path / "existing.platy"
        existing_file.write_text("/old.milk\n")
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt
        captured_callback = None

        def capture_callback(msg, callback):
            nonlocal captured_callback
            captured_callback = callback

        mock_prompt.show_prompt.side_effect = capture_callback
        await check_and_save(existing_file, mock_ctx, mock_app)

        with patch(
            "platyplaty.commands.save_playlist.perform_save",
        ) as mock_save:
            captured_callback(False)
        mock_save.assert_not_called()

