from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.ui.widgets.img_upload import ImgUpload, NoImgUploaded, generate_identicon
from elogate.models import CHAR_FIELD_LEN_NAMES, Player


@ui.page("/users/create")
async def user_create_page(edit_id: int | None = None):
    if edit_id is not None:
        edit_player = await Player.filter(id=edit_id).first()
    else:
        edit_player = None

    _ = Header()

    def _string_length_ok(value: str) -> bool:
        return len(value) < CHAR_FIELD_LEN_NAMES

    async def _save_player():
        _player_name: str = player_name.value  # pyright: ignore [reportAny]
        _player_name = _player_name.strip()
        if not _player_name:
            ui.notify("Player must have a name!")
            return
        existing_players = (
            await Player.filter(name__not=getattr(edit_player, "name", ""))
            .filter(name=_player_name)
            .all()
        )
        if existing_players:
            ui.notify("Player name already taken!")
            return
        try:
            img_upload.save()
        except NoImgUploaded:
            if not edit_player or not edit_player.icon:
                img_upload.image = generate_identicon(_player_name)
                img_upload.save()
        if not edit_player:
            player = Player(name=_player_name, icon=img_upload.uuid)
        else:
            player = edit_player
            player.name = _player_name
            player.icon = img_upload.uuid
        await player.save()
        # TODO: navigate to a player list
        ui.navigate.to("/users")

    with ui.column():
        if edit_player:
            _ = ui.label(f"Edit Player '{edit_player.name}'")
        else:
            _ = ui.label(f"Create New Player")

        player_name = ui.input(
            label="Player Name", validation={"Input too long": _string_length_ok}
        )
        img_upload = ImgUpload(label="Profile Image")
        if edit_player:
            player_name.set_value(edit_player.name)
            img_upload.uuid = edit_player.icon

        _ = ui.button(text="Submit", on_click=_save_player)
