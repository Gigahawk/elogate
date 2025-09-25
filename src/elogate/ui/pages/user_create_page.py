from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.auth_utils import logged_in
from elogate.models import CHAR_FIELD_LEN_NAMES


@ui.page("/users/create")
async def user_create_page():
    _ = Header()

    def _string_length_ok(value: str) -> bool:
        return len(value) < CHAR_FIELD_LEN_NAMES

    with ui.column():
        _ = ui.input(
            label="Player Name", validation={"Input too long": _string_length_ok}
        )
