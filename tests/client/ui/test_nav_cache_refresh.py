"""Tests for indicator cache refresh on navigation."""

from pathlib import Path
from unittest.mock import patch

import pytest

from platyplaty.ui.nav_state import NavigationState


@pytest.fixture
def populated_nav_state(tmp_path: Path) -> NavigationState:
    """Create NavigationState with multiple entries for testing."""
    # Create files and directories
    (tmp_path / "aaa.milk").touch()
    (tmp_path / "bbb.milk").touch()
    (tmp_path / "ccc.milk").touch()
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    return NavigationState(tmp_path)


class TestUpDownRefreshesOldSelection:
    """Test up/down navigation refreshes OLD selection cache."""

    def test_move_down_refreshes_old_selection(
        self, populated_nav_state: NavigationState
    ) -> None:
        """move_down should call refresh for item losing selection."""
        state = populated_nav_state
        listing = state.get_listing()
        assert listing is not None
        old_entry = listing.entries[0]
        state.selected_name = old_entry.name

        with patch(
            "platyplaty.ui.nav_moves.refresh_indicator_cache"
        ) as mock_refresh:
            state.move_down()
            mock_refresh.assert_called_once_with(
                old_entry.entry_type, old_entry.path
            )

    def test_move_up_refreshes_old_selection(
        self, populated_nav_state: NavigationState
    ) -> None:
        """move_up should call refresh for item losing selection."""
        state = populated_nav_state
        listing = state.get_listing()
        assert listing is not None
        # Start at second item
        old_entry = listing.entries[1]
        state.selected_name = old_entry.name

        with patch(
            "platyplaty.ui.nav_moves.refresh_indicator_cache"
        ) as mock_refresh:
            state.move_up()
            mock_refresh.assert_called_once_with(
                old_entry.entry_type, old_entry.path
            )


class TestLeftRightRefreshesNewSelection:
    """Test left/right navigation refreshes NEW selection cache."""

    def test_move_right_into_dir_refreshes_new_selection(
        self, tmp_path: Path
    ) -> None:
        """move_right into directory should refresh new selection."""
        # Create structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.milk").touch()
        state = NavigationState(tmp_path)
        # Select the subdir
        state.selected_name = "subdir"

        with patch(
            "platyplaty.ui.nav_right.refresh_indicator_cache"
        ) as mock_refresh:
            state.move_right()
            # Should have refreshed the new selection in subdir
            assert mock_refresh.called

    def test_move_left_refreshes_new_selection(
        self, tmp_path: Path
    ) -> None:
        """move_left should refresh new selection in parent dir."""
        # Create structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file.milk").touch()
        state = NavigationState(subdir)

        with patch(
            "platyplaty.ui.nav_left.refresh_indicator_cache"
        ) as mock_refresh:
            state.move_left()
            # Should have refreshed the new selection (subdir in parent)
            assert mock_refresh.called
