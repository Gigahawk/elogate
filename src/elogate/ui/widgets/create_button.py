from nicegui import ui

from elogate.auth_utils import logged_in


class CreateButton(ui.fab):
    def __init__(self):
        if logged_in():
            super().__init__("add", direction="up")
            _ = self.classes("fixed bottom-0 right-0 m-8")
            with self:
                _ = ui.fab_action(
                    "person",
                    label="Player",
                    on_click=lambda: ui.navigate.to("/users/create"),
                )
                _ = ui.fab_action("leaderboard", label="Game")
