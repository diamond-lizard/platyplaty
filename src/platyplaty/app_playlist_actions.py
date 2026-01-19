"""Playlist action methods for the Platyplaty application."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from platyplaty.app import PlatyplatyApp


async def action_navigate_up(app: PlatyplatyApp) -> None:
    """Move selection up in current focused section."""
    from platyplaty.playlist_actions import navigate_up

    await navigate_up(app.ctx, app)


async def action_navigate_down(app: PlatyplatyApp) -> None:
    """Move selection down in current focused section."""
    from platyplaty.playlist_actions import navigate_down

    await navigate_down(app.ctx, app)


async def action_play_next(app: PlatyplatyApp) -> None:
    """Play next preset in playlist."""
    from platyplaty.playlist_actions import play_next

    await play_next(app.ctx, app)


async def action_play_previous(app: PlatyplatyApp) -> None:
    """Play previous preset in playlist."""
    from platyplaty.playlist_actions import play_previous

    await play_previous(app.ctx, app)


async def action_reorder_up(app: PlatyplatyApp) -> None:
    """Move selected preset up in playlist."""
    from platyplaty.playlist_actions import reorder_up

    await reorder_up(app.ctx, app)


async def action_reorder_down(app: PlatyplatyApp) -> None:
    """Move selected preset down in playlist."""
    from platyplaty.playlist_actions import reorder_down

    await reorder_down(app.ctx, app)


async def action_delete_from_playlist(app: PlatyplatyApp) -> None:
    """Delete selected preset from playlist."""
    from platyplaty.playlist_actions import delete_from_playlist

    await delete_from_playlist(app.ctx, app)


async def action_undo(app: PlatyplatyApp) -> None:
    """Undo the last playlist operation."""
    from platyplaty.playlist_actions import undo

    await undo(app.ctx, app)


async def action_redo(app: PlatyplatyApp) -> None:
    """Redo the last undone playlist operation."""
    from platyplaty.playlist_actions import redo

    await redo(app.ctx, app)


async def action_play_selection(app: PlatyplatyApp) -> None:
    """Play the currently selected preset in the playlist."""
    from platyplaty.playlist_actions import play_selection

    await play_selection(app.ctx, app)


async def action_open_selected(app: PlatyplatyApp) -> None:
    """Open the currently selected preset in $EDITOR."""
    from platyplaty.playlist_actions import open_selected

    await open_selected(app.ctx, app)


async def action_page_up(app: PlatyplatyApp) -> None:
    """Move selection up by one page."""
    from platyplaty.playlist_actions import page_up

    await page_up(app.ctx, app)


async def action_page_down(app: PlatyplatyApp) -> None:
    """Move selection down by one page."""
    from platyplaty.playlist_actions import page_down

    await page_down(app.ctx, app)


async def action_navigate_to_first_preset(app: PlatyplatyApp) -> None:
    """Move selection to first preset."""
    from platyplaty.playlist_actions import navigate_to_first_preset

    await navigate_to_first_preset(app.ctx, app)


async def action_navigate_to_last_preset(app: PlatyplatyApp) -> None:
    """Move selection to last preset."""
    from platyplaty.playlist_actions import navigate_to_last_preset

    await navigate_to_last_preset(app.ctx, app)


async def action_shuffle_playlist(app: PlatyplatyApp) -> None:
    """Shuffle the playlist in place."""
    from platyplaty.playlist_actions import shuffle_playlist

    await shuffle_playlist(app.ctx, app)

async def action_save_playlist(app: PlatyplatyApp) -> None:
    """Save the playlist to its associated filename."""
    from platyplaty.playlist_actions import save_playlist

    await save_playlist(app.ctx, app)


async def action_toggle_autoplay(app: PlatyplatyApp) -> None:
    """Toggle autoplay on or off."""
    from platyplaty.playlist_actions import toggle_autoplay

    await toggle_autoplay(app.ctx, app)
