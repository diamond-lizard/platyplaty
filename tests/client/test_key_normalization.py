#!/usr/bin/env python3
"""Tests for key normalization function."""

from platyplaty.dispatch_tables import normalize_key


class TestNormalizeKey:
    """Tests for normalize_key function."""

    def test_shift_j_normalizes_to_uppercase_J(self) -> None:
        """shift+j should normalize to J."""
        assert normalize_key("shift+j") == "J"

    def test_shift_k_normalizes_to_uppercase_K(self) -> None:
        """shift+k should normalize to K."""
        assert normalize_key("shift+k") == "K"

    def test_shift_a_normalizes_to_uppercase_A(self) -> None:
        """shift+a should normalize to A."""
        assert normalize_key("shift+a") == "A"

    def test_shift_enter_unchanged(self) -> None:
        """shift+enter should pass through unchanged."""
        assert normalize_key("shift+enter") == "shift+enter"

    def test_ctrl_j_unchanged(self) -> None:
        """ctrl+j should pass through unchanged."""
        assert normalize_key("ctrl+j") == "ctrl+j"

    def test_ctrl_shift_j_unchanged(self) -> None:
        """ctrl+shift+j should pass through unchanged."""
        assert normalize_key("ctrl+shift+j") == "ctrl+shift+j"

    def test_lowercase_j_unchanged(self) -> None:
        """Plain lowercase j should pass through unchanged."""
        assert normalize_key("j") == "j"

    def test_uppercase_J_unchanged(self) -> None:
        """Uppercase J should pass through unchanged."""
        assert normalize_key("J") == "J"

    def test_up_key_unchanged(self) -> None:
        """Special key 'up' should pass through unchanged."""
        assert normalize_key("up") == "up"

    def test_shift_d_normalizes_to_uppercase_D(self) -> None:
        """shift+d should normalize to D (for delete action)."""
        assert normalize_key("shift+d") == "D"

from platyplaty.dispatch_tables_ui import build_playlist_dispatch_table

def _make_playlist_table_with_shift_format():
    """Create a playlist dispatch table using shift+letter format."""
    return build_playlist_dispatch_table(
        play_previous_keys=["shift+k"],
        play_next_keys=["shift+j"],
        reorder_up_keys=["ctrl+k"],
        reorder_down_keys=["ctrl+j"],
        delete_keys=["shift+d", "delete"],
        undo_keys=["u"],
        redo_keys=["ctrl+r"],
        save_keys=["ctrl+s"],
        shuffle_keys=["s"],
        toggle_autoplay_keys=["space"],
        page_up_keys=["pageup"],
        page_down_keys=["pagedown"],
        navigate_to_first_keys=["home"],
        navigate_to_last_keys=["end"],
    )


class TestDispatchTableNormalizationIntegration:
    """Integration tests for key normalization in dispatch tables."""

    def test_shift_j_in_playlist_maps_to_uppercase_J(self) -> None:
        """Playlist dispatch table normalizes shift+j to J."""
        table = _make_playlist_table_with_shift_format()
        assert "J" in table
        assert table["J"] == "play_next"
        assert "shift+j" not in table

    def test_shift_k_in_playlist_maps_to_uppercase_K(self) -> None:
        """Playlist dispatch table normalizes shift+k to K."""
        table = _make_playlist_table_with_shift_format()
        assert "K" in table
        assert table["K"] == "play_previous"
        assert "shift+k" not in table

    def test_shift_d_in_playlist_maps_to_uppercase_D(self) -> None:
        """Playlist dispatch table normalizes shift+d to D."""
        table = _make_playlist_table_with_shift_format()
        assert "D" in table
        assert table["D"] == "delete_from_playlist"
        assert "shift+d" not in table
