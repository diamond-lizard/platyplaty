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
