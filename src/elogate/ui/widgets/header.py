from typing import cast

from nicegui import ui, app
from nicegui.events import ValueChangeEventArguments


from elogate.auth_utils import logged_in, logout


class Header(ui.header):
    def set_dark_mode(self, evt: ValueChangeEventArguments):
        app.storage.user["dark_mode"] = cast(bool | None, evt.value)

    def __init__(self):
        super().__init__()

        dark_mode = ui.dark_mode(
            value=app.storage.user.get("dark_mode"),  # pyright: ignore [reportUnknownMemberType, reportUnknownArgumentType]
            on_change=self.set_dark_mode,
        )
        with self:
            with ui.row(align_items="center").classes("w-full"):
                with ui.link(target="/").classes(
                    "text-inherit no-underline hover:underline"
                ):
                    _ = ui.markdown("###### Elogate")
                _ = ui.space()
                if logged_in():
                    _ = ui.label(f"Hello {app.storage.user['username']}")
                    _ = ui.button(text="Log Out", on_click=logout)
                else:
                    _ = ui.button(
                        text="Log In", on_click=lambda: ui.navigate.to("/login")
                    )

                with (
                    ui.element()
                    .classes("max-[420px]:hidden")
                    .tooltip("Cycle theme mode through dark, light, and system/auto")
                ):
                    _ = (
                        ui.button(
                            icon="dark_mode", on_click=lambda: dark_mode.set_value(None)
                        )
                        .props("flat-fab-mini color=white")
                        .bind_visibility_from(dark_mode, "value", value=True)
                    )
                    _ = (
                        ui.button(
                            icon="light_mode",
                            on_click=lambda: dark_mode.set_value(True),
                        )
                        .props("flat-fab-mini color=white")
                        .bind_visibility_from(dark_mode, "value", value=False)
                    )
                    _ = (
                        ui.button(
                            icon="brightness_auto",
                            on_click=lambda: dark_mode.set_value(False),
                        )
                        .props("flat-fab-mini color=white")
                        .bind_visibility_from(
                            dark_mode,
                            "value",
                            lambda mode: mode is None,  # pyright: ignore [reportAny]
                        )
                    )
