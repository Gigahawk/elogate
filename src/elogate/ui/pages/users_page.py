from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.ui.widgets.create_button import CreateButton
from elogate.ui.widgets.player_card import PlayerCard
from elogate.models import Player


@ui.page("/users")
async def users_page():
    _ = Header()

    _ = CreateButton()

    with ui.row():
        if await Player.all().exists():
            # TODO: support pagination/lazy load?
            for player in await Player.filter().order_by("name").all():
                _ = PlayerCard(player)
        else:
            _ = ui.label("No players registered. Add one with the + button")
