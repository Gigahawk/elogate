from nicegui import ui

from elogate.ui.widgets.header import Header
from elogate.ui.widgets.create_button import CreateButton


@ui.page("/")
async def main_page():
    _ = Header()

    _ = CreateButton()

    with ui.column().classes("absolute-center items-center"):
        _ = ui.label(f"Hello world!").classes("text-2xl")
