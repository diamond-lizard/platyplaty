#!/usr/bin/env python3
"""Unit tests for :save command when target file does not exist."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSaveNewFile:
    """Tests for :save when target file does not exist."""

    @pytest.mark.asyncio
    async def test_save_new_file_skips_prompt(
        self, mock_ctx, mock_app, tmp_path
    ):
        """Save to new file does not show overwrite prompt."""
        from platyplaty.commands.save_playlist import check_and_save

        new_file = tmp_path / "new.platy"
        mock_prompt = MagicMock()
        mock_app.query_one.return_value = mock_prompt

        with patch(
            "platyplaty.commands.save_playlist.perform_save",
            return_value=(True, None),
        ):
            await check_and_save(new_file, mock_ctx, mock_app)

        mock_prompt.show_prompt.assert_not_called()
