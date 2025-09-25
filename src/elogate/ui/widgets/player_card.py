from nicegui import ui

from elogate.config import Settings
from elogate.models import Player


class PlayerCard(ui.card):
    def __init__(self, player: Player):
        super().__init__()
        _ = self.on("click", handler=lambda: ui.navigate.to(f"/users/{player.id}"))
        _ = self.classes("w-96 h-40")
        with self:
            with ui.row().classes("w-full"):
                _ = ui.image(
                    source=Settings().resources_path / "images" / str(player.icon)
                ).classes("w-32 h-32")
                _ = ui.label(text=player.name).classes(
                    "max-w-40 overflow-hidden text-ellipsis"
                )
