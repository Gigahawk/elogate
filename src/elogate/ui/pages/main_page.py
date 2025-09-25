from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.auth_utils import logged_in


@ui.page("/")
async def main_page():
    _ = Header()

    if logged_in():
        with ui.fab("add", direction="up").classes("absolute bottom-0 right-0 m-8"):
            _ = ui.fab_action(
                "person",
                label="Player",
                on_click=lambda: ui.navigate.to("/users/create"),
            )
            _ = ui.fab_action("leaderboard", label="Game")

    with ui.column().classes("absolute-center items-center"):
        _ = ui.label(f"Hello world!").classes("text-2xl")
