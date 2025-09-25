from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.models import Player


@ui.page("/users/{id}")
async def user_page(id: int):
    _ = Header()

    player = await Player.filter(id=id).first()
    if player is None:
        raise ValueError(f"Player with ID {id} does not exist")

    with ui.dialog() as dialog, ui.card():
        _ = ui.label(f"Are you sure you want to delete Player '{player.name}'?")
        _ = ui.label("All associated matches will be deleted!")

        with ui.row():
            _ = ui.button("Yes", on_click=lambda: dialog.submit(True))
            _ = ui.button("No", on_click=lambda: dialog.submit(False))

    async def _delete_player():
        if await dialog is True:
            # TODO: handle match recalculation
            _ = await player.delete()
            ui.navigate.to("/users")

    with ui.column():
        with ui.row():
            _ = ui.image(source=player.icon_path).classes("w-30 h-30")
            _ = ui.label(text=player.name)
        with ui.row():
            _ = ui.button(text="Delete", on_click=_delete_player)
            _ = ui.button(
                text="Edit",
                on_click=lambda: ui.navigate.to(f"/users/create?edit_id={id}"),
            )
